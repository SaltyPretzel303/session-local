import random
import string

from flask import Flask, Response, request, session, g
from flask_api import status
from flask_restful import Api
from flask_session import Session

from auth_request import AuthRequest
from register_request import RegisterRequest
from user import User
from app_config import AppConfig
from db import Db

import jsonpickle

from datetime import datetime, timedelta
# from dateutil.parser import isoparse

USER_SESSION_VAR = "user"

config = AppConfig.get_instance()

app = Flask(__name__)
api = Api(app)

app.secret_key = config["session_secret_key"]
app.config["SESSION_TYPE"] = config["session_type"]

Session(app)

def json_serialize(content):
	return jsonpickle.encode(content, unpicklable=False, indent=4)


def gen_key(len: int):
	letters = string.ascii_letters
	token = "".join(random.choice(letters) for i in range(len))
	return token

def get_db()->Db:
	if 'db' not in g:
		print("creating request scoped db ... ")
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
	else:
		new_user = User(username = reg_request.username,
						email = reg_request.email,
						password = reg_request.password,
						stream_key = gen_key(config["stream_key_len"]))

		ret_obj = get_db().save(new_user)

		if ret_obj is not None:
			return ret_obj.to_json(), status.HTTP_200_OK
		else:
			return "Failed to crate new user ... ", status.HTTP_500_INTERNAL_SERVER_ERROR
		

@app.route("/authenticate", methods=["POST"])
def authenticate():

	if USER_SESSION_VAR in session:
		print(f"User was already authenticated ... ")
		user_data = session[USER_SESSION_VAR]
		return user_data.to_json(), status.HTTP_200_OK

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

	print(json_serialize(auth_request))

	user = get_db().get_user(auth_request.email)

	if user is None:
		return "User doesn't exists ... ", status.HTTP_401_UNAUTHORIZED
	
	if user.password != auth_request.password:
		print("Wrong password ... ")
		return "Wrong password ... ", status.HTTP_401_UNAUTHORIZED
	
	print(f"Successfully authenticated {auth_request.email} ... ")

	user.last_authenticated = datetime.now().isoformat()
	res_data = get_db().save(user)
	session[USER_SESSION_VAR] = res_data
	
	return res_data.to_json(), status.HTTP_200_OK


@app.route("/get_key", methods=["GET"])
def get_key():
	if USER_SESSION_VAR not in session:
		return "User not authenticated ... ", status.HTTP_403_FORBIDDEN
	
	s_user = session[USER_SESSION_VAR]
	exp_date = s_user.key_exp_date

	if exp_date is None or is_expired(exp_date):
		print("Key is none or expired ... ")
		
		s_user.stream_key = gen_key(config["stream_key_len"])

		now = datetime.now()
		longevity = config["stream_key_longevity"]
		s_user.key_exp_date = now + timedelta(seconds=longevity)
		
		get_db().save(s_user)
		
	# TODO Return value should be some kind of object and not just ... text.
	return s_user.stream_key, status.HTTP_200_OK
		

def  is_expired(key_time: datetime)->bool:
	return datetime.now() > key_time

# Accessed by nginx-rtmp module from the on_publish directive.
@app.route("/match_key", methods=["POST"])
def match_key_post():

	args = url_decode(str(request.get_data()))

	key = args.get("name")
	user = get_db().get_by_key(key)

	if user is None or is_expired(user.key_exp_date):
		return "Invalid key ... ", status.HTTP_404_NOT_FOUND

	print(f"Successfully redirected to: {user.username}")

	resp = Response(status=302)
	resp.headers["Location"] = user.username
	return resp

@app.route("/match_key/<key>", methods=["GET"])
def match_key_get(key: str):

	if key is None or key == "":
		return "Please provide a key ... ", status.HTTP_400_BAD_REQUEST

	user = get_db().get_by_key(key)
	
	if user is None or is_expired(user.key_exp_date):
		return "Invalid key provided ... ", status.HTTP_404_NOT_FOUND

	return user.username, status.HTTP_200_OK

def url_decode(data:str):
	return { pair.split("=")[0]:pair.split("=")[1]  for pair in data.split("&")}


@app.route("/authorize", methods=["GET"])
def authorize():

	stream_name = request.headers.get(config["stream_name_h_field"])
	print(f"X-Stream-Name (extracted): {stream_name}")
	
	if USER_SESSION_VAR in session:
		print("Session has user ... ")
		user_name = session[USER_SESSION_VAR].username
		print(f"user_name (from session ): {user_name}")

		if is_authorized(user_name, stream_name):
			return status.HTTP_200_OK
		else:
			return status.HTTP_401_UNAUTHORIZED  # redirect to login or just ... discard
	else:
		print("No user session ... ")
		return 'Not authorized ... ', status.HTTP_403_FORBIDDEN

def is_authorized(user: str, stream: str) -> bool:
	# either db check
	# or with authenticate save user permissions as well in session
	print(f"Authorized: {user} for {stream} stream ... ")
	return True

# old stuff down there ... 

# thi can be removed i guess ? 
@app.route("/validate", methods=["GET"])
def validate():
	stream_name = request.headers.get(config["stream_name_h_field"])
	# session_id = request.cookies.get(SESSION_ID_FIELD)
	s_user = session.get("user")

	# if is_authorized(s_user.username, stream_name):
	#     return status.HTTP_200_OK
	# else:
	#     return status.HTTP_403_FORBIDDEN

	print(f"stream: {stream_name}")
	# print(f"sessionId: {session_id}")
	print(f"user_session: {s_user}")

	if s_user is not None:
		username = s_user.username
		print(f"usernameFromSession: {username}")
		if is_authorized(username, stream_name):
			return status.HTTP_200_OK
		else:
			return status.HTTP_403_FORBIDDEN

	else:
		return status.HTTP_403_SEE_OTHER



@app.route("/stop_stream", methods=["POST"])
def stop_stream():
	print(request.headers)
	print("stream stopped")

	return status.HTTP_200_OK

if __name__ == '__main__':
	app.run(host="0.0.0.0", port='8003')
