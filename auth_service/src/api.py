import random
import string

from flask import Flask, Response, request, session, g
from flask_api import status
from flask_restful import Api
from flask_session import Session

from auth_request import AuthRequest
from auth_response import AuthResponse
from stream_key import StreamKey
from register_request import RegisterRequest
from user import User
from app_config import AppConfig
from db import Db

import jsonpickle

from datetime import datetime, timedelta

from bcrypt import hashpw, checkpw, gensalt

USER_SESSION_VAR = "user"

config = AppConfig.get_instance()

app = Flask(__name__)
api = Api(app)

app.secret_key = config["session_secret_key"]
app.config["SESSION_TYPE"] = config["session_type"]
# TODO switch to redis as a session_type

Session(app)

def json_serialize(content):
	return jsonpickle.encode(content, unpicklable=False, indent=4)


def gen_stream_key() -> StreamKey:
	len = config["stream_key_len"]
	chars = string.ascii_letters+string.digits
	return "".join(random.choice(chars) for i in range(len))

def gen_exp_date() -> datetime:
	longevity = config['stream_key_longevity']
	return datetime.now() + timedelta(seconds=longevity)

def get_db()->Db:
	if 'db' not in g:
		address = config["db_host"]
		port = config["db_port"]
		db = config["db_name"]
		user = config["db_user"]
		pwd = config["db_password"]
		g.db = Db(f"mongodb://{user}:{pwd}@{address}:{port}/{db}")

	return g.db


@app.route("/register", methods=["POST"])
def register():

	if request.data is None:
		return "No data provided ...", status.HTTP_400_BAD_REQUEST # bad request
	
	if not request.is_json:
		return "Json data required ... ", status.HTTP_415_UNSUPPORTED_MEDIA_TYPE # unsupported media type 
	
	try:
		reg_request = RegisterRequest(**request.get_json())
		if reg_request is None:
			raise Exception("Error parsing data ... ")
	except TypeError:
		print("Unable to parse incoming data: ")
		print(request.get_json())

		return "Error parsing data ... ", status.HTTP_400_BAD_REQUEST
		# Should return 422 but this one is not defined in status.
	
	print("Register request ... ")
	print(json_serialize(reg_request))

	user = get_db().get_user(reg_request.email)

	if user is not None:
		return "This email is already used ... ", status.HTTP_200_OK
	
	new_user = User(username = reg_request.username,
					email = reg_request.email,
					pwd_hash = hashpw(reg_request.password.encode(), gensalt()))

	ret_obj = get_db().save_user(new_user)

	if ret_obj is not None:
		return ret_obj.to_json(), status.HTTP_200_OK
	else:
		return "Failed to crate new user ... ", status.HTTP_500_INTERNAL_SERVER_ERROR
		

@app.route("/authenticate", methods=["POST"])
def authenticate():

	if USER_SESSION_VAR in session:
		print(f"User was already authenticated ... ")
		user_data = session[USER_SESSION_VAR]
		res = AuthResponse(user_data.username)
		return jsonpickle.encode(res, unpicklable=False ), status.HTTP_200_OK

	if request.data is None:
		return "No data provided ...", status.HTTP_400_BAD_REQUEST
	
	if not request.is_json:
		return "Json data required ... ", status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
	
	try:
		auth_request = AuthRequest(**request.get_json())

		if auth_request is None:
			raise Exception("Failed to parse data ... ")
	except (TypeError, Exception) as e:
		print("Unable to parse incoming data: ")
		print(f"Err: {e}")
		print(f"Data: \n{request.get_json()}")
		return "Error parsing data ... ", status.HTTP_400_BAD_REQUEST

	user: User = get_db().get_user(auth_request.email)

	if user is None:
		return "User doesn't exists ... ", status.HTTP_401_UNAUTHORIZED
	
	if not checkpw(auth_request.password.encode(), user.pwd_hash):
		print("Wrong password ... ")
		return "Failed to authenticate ... ", status.HTTP_401_UNAUTHORIZED
	
	print(f"Successfully authenticated {auth_request.email} ... ")

	user.last_authenticated = datetime.now()
	res_data = get_db().save_user(user)
	session[USER_SESSION_VAR] = res_data
	
	res = AuthResponse(username=res_data.username)
	return jsonpickle.encode(res, unpicklable=False), status.HTTP_200_OK

@app.route("/get_key", methods=["GET"])
def get_key():
	if USER_SESSION_VAR not in session:
		return "User not authenticated ... ", status.HTTP_403_FORBIDDEN
	
	user: User = session[USER_SESSION_VAR]
	key: StreamKey = get_db().get_key_with_owner(user)

	if key is None:
		print("Key not found, will generates new ... ")
		key = StreamKey()
		key.owner = user

	if key.is_expired():
		print("Key is or expired, will genreate new ... ")
		
		key.value = gen_stream_key()
		key.exp_date = gen_exp_date()
		
	get_db().save_key(key)
		
	return key.value, status.HTTP_200_OK
	# TODO Return value should be some kind of object and not just ... text.
		

# def is_expired(key_time: datetime)->bool:
# 	return datetime.now() > key_time

# TODO not used, should be removed 
# Accessed by nginx-rtmp module from the on_publish directive.
# @app.route("/match_key", methods=["POST"])
# def match_key_post():

# 	args = url_decode(str(request.get_data()))

# 	key = args.get("name")
# 	user = get_db().get_by_key(key)

# 	if user is None or is_expired(user.key_exp_date):
# 		return "Invalid key ... ", status.HTTP_404_NOT_FOUND

# 	print(f"Successfully redirected to: {user.username}")

# 	resp = Response(status=302)
# 	resp.headers["Location"] = user.username
# 	return resp

# Accessed by the stream_registry api.
@app.route("/match_key/<req_key>", methods=["GET"])
def match_key_get(req_key: str):

	if req_key is None or req_key == "":
		return "Please provide a key ... ", status.HTTP_400_BAD_REQUEST

	key = get_db().get_key_with_val(req_key)
	
	if key is None or key.is_expired():
		print("Invalid/expired key provided ... ")
		return "Invalid/expired key provided ... ", status.HTTP_404_NOT_FOUND

	return key.owner.username, status.HTTP_200_OK

def url_decode(data:str):
	return { pair.split("=")[0]:pair.split("=")[1]  for pair in data.split("&")}


@app.route("/authorize", methods=["GET"])
def authorize():

	print("Authorization request header ... ")
	print(request.headers)

	stream_name = request.headers.get(config["stream_name_h_field"])
	print(f"X-Stream-Name (extracted): {stream_name}")
	
	if USER_SESSION_VAR not in session:
		print("No user session, not authorized ... ")
		return 'Not authorized ... ', status.HTTP_403_FORBIDDEN
		
	print("User session found ... ")
	user_name = session[USER_SESSION_VAR].username
	print(f"user_name (from session ): {user_name}")

	if is_authorized(user_name, stream_name):
		return user_name, status.HTTP_200_OK
	else:
		return user_name, status.HTTP_401_UNAUTHORIZED 
		# redirect to login or just ... discard
		

def is_authorized(user: str, stream: str) -> bool:
	# either db check
	# or with authenticate save user permissions as well in session
	print(f"Authorized: {user} for {stream} stream ... ")
	return True

if __name__ == '__main__':
	app.run(host="0.0.0.0", port='8003')