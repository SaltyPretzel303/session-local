import random
import string

from flask import Flask, Response, request, session, g
from flask_api import status
from flask_restful import Api
from flask_session import Session
from flask_cors import CORS

from auth_request import AuthRequest
from auth_response import AuthResponse,AuthStatus
from key_response import KeyResponse, KeyStatus

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

# CORS(app, support_credentials=True)
# CORS(app)

app.secret_key = config["session_secret_key"]
app.config["SESSION_TYPE"] = config["session_type"]
# TODO switch to redis as a session_type

# app.config["SESSION_COOKIE_SAMESITE"] = "None"
# app.config["SESSION_COOKIE_SAMESITE"] = "Strict" # should be this 
# app.config["SESSION_COOKIE_SECURE"] = True # this will require https 

Session(app)

def json_serialize(content):
	return jsonpickle.encode(content, unpicklable=False, indent=4)


def gen_stream_key(len) -> StreamKey:
	chars = string.ascii_letters+string.digits
	return "".join(random.choice(chars) for i in range(len))

def gen_exp_date(longevity) -> datetime:
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


@app.after_request
def header_filler(resp):
	resp.headers.add("Access-Control-Allow-Credentials","true")
	resp.headers.add("Access-Control-Allow-Origin","http://localhost:3000")
	resp.headers.add("Access-Control-Allow-Headers","Content-type")
	
	return resp



@app.route("/register", methods=["POST"])
def register():

	if request.data is None:
		
		res = AuthResponse(status=AuthStatus.BAD_REQUEST, message="No data provided ...")
		return json_serialize(res), status.HTTP_400_BAD_REQUEST # bad request
	
	if not request.is_json:
		res = AuthResponse(status=AuthStatus.BAD_REQUEST, message="Json data required ...")
		return json_serialize(res), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE # unsupported media type 
	
	try:
		reg_request = RegisterRequest(**request.get_json())
		if reg_request is None:
			raise Exception("Error parsing data ... ")
	except TypeError:
		print("Unable to parse incoming data: ")
		print(request.get_json())

		res = AuthResponse(status=AuthStatus.BAD_REQUEST, message="Error parsing data ...")
		return json_serialize(res), status.HTTP_400_BAD_REQUEST
		# Should return 422 but this one is not defined in status.
	
	print("Register request ... ")
	(json_serialize(reg_request))

	user = get_db().get_user(reg_request.email)

	if user is not None:
		print("Email already in use ... ")
		res = AuthResponse(status=AuthStatus.ALREADY_EXISTS, message="This email already exists ...")
		return json_serialize(res), status.HTTP_200_OK
	
	new_user = User(username = reg_request.username,
					email = reg_request.email,
					pwd_hash = hashpw(reg_request.password.encode(), gensalt()))

	ret_obj = get_db().save_user(new_user)

	if ret_obj is not None:
		print("User successfully registered ... ")
		res = AuthResponse(status=AuthStatus.SUCCESS,
					username=ret_obj.username,
					email=ret_obj.email)
		return json_serialize(res), status.HTTP_200_OK
	else:
		res = AuthResponse(status=AuthStatus.FAILED, message="Failed to create new user ...")
		return json_serialize(res), status.HTTP_500_INTERNAL_SERVER_ERROR
		

@app.route("/authenticate", methods=["POST"])
def authenticate():

	print("Auth request: ")
	print(request.headers)


	if USER_SESSION_VAR in session:
		print(f"User was already authenticated ... ")
		user_data: User = session[USER_SESSION_VAR]
		res_data = AuthResponse(status=0,
					username=user_data.username, 
					email=user_data.email)


		response = Response()
		response.status = status.HTTP_200_OK
		# response.headers.add("Access-Control-Allow-Credentials","true")
		# response.headers.add("Access-Control-Allow-Origin","http://localhost:3000")
		response.content_type = "application/json"
		response.set_data(json_serialize(res_data))

		return response

	if request.data is None:
		res_data = AuthResponse(status=AuthStatus.BAD_REQUEST, 
					message = "No data provided ...")
		return json_serialize(res_data), status.HTTP_400_BAD_REQUEST
	
	if not request.is_json:
		res_data = AuthResponse(status=AuthStatus.BAD_REQUEST, message="Json data required ...")
		return json_serialize(res_data), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
	
	try:
		auth_request = AuthRequest(**request.get_json())

		if auth_request is None:
			raise Exception("Failed to parse data ... ")
	except (TypeError, Exception) as e:
		print("Unable to parse incoming data: ")
		print(f"Err: {e}")

		res_data = AuthResponse(status=AuthStatus.BAD_REQUEST, message="Failed to parse data ...")
		return json_serialize(res_data), status.HTTP_400_BAD_REQUEST

	user: User = get_db().get_user(auth_request.email)

	if user is None:
		res_data = AuthResponse(status=AuthStatus.FAILED, message="User doesn't exists ...")
		return json_serialize(res_data), status.HTTP_401_UNAUTHORIZED
	
	if not checkpw(auth_request.password.encode(), user.pwd_hash):
		print("Wrong password ... ")

		res_data = AuthResponse(status=AuthStatus.FAILED, message="Wrong password ... ")
		return json_serialize(res_data), status.HTTP_401_UNAUTHORIZED
	
	print(f"Successfully authenticated {auth_request.email} ... ")

	user.last_authenticated = datetime.now()
	res_data = get_db().save_user(user)
	session[USER_SESSION_VAR] = res_data

	res_data = AuthResponse(status=0,
				username=res_data.username, 
				email=res_data.email)
	# return json_serialize(res), status.HTTP_200_OK

	response = Response()
	response.status = status.HTTP_200_OK
	# response.headers.add("Access-Control-Allow-Credentials","true")
	# response.headers.add("Access-Control-Allow-Origin","http://localhost:3000")
	response.content_type = "application/json"
	response.set_data(json_serialize(res_data))

	return response

@app.route("/get_key", methods=["GET"])
def get_key():
	print("Request cookies ... ")
	print(request.cookies)
	print("Request header ... ")
	print(request.headers)

	if USER_SESSION_VAR not in session:
		res = KeyResponse(status=KeyStatus.FAILED, message="Not authorized ...")
		return json_serialize(res), status.HTTP_403_FORBIDDEN
	
	user: User = session[USER_SESSION_VAR]
	key: StreamKey = get_db().get_key_with_owner(user)

	if key is None:
		print("Key not found, will generates new ... ")
		key = StreamKey()
		key.owner = user

	if key.is_expired():
		print("Key missing or expired, will genreate new ... ")
		
		key.value = gen_stream_key(config["stream_key_len"])
		key.exp_date = gen_exp_date(config['stream_key_longevity'])
		
	get_db().save_key(key)

	res = KeyResponse(status=KeyStatus.SUCCESS, 
				value=key.value, 
				exp_data=key.exp_date.isoformat() )
	
	return json_serialize(res), status.HTTP_200_OK
		

# Accessed by the stream_registry api.
@app.route("/match_key/<req_key>", methods=["GET"])
def match_key_get(req_key: str):

	if req_key is None or req_key == "":
		res = KeyResponse(status=KeyStatus.FAILED, message="No key provided ...")
		return json_serialize(res), status.HTTP_400_BAD_REQUEST

	key = get_db().get_key_with_val(req_key)
	
	if key is None or key.is_expired():
		print("Invalid/expired key provided ... ")
		res = KeyResponse(status=KeyStatus.FAILED, message="Invalid/Expired key provided ...")
		return json_serialize(res), status.HTTP_404_NOT_FOUND

	get_db().invalidate_key(key)

	res = KeyResponse(status=KeyStatus.SUCCESS, value=key.owner.username)
	return json_serialize(res), status.HTTP_200_OK

def url_decode(data:str):
	return { pair.split("=")[0]:pair.split("=")[1]  for pair in data.split("&")}


@app.route("/authorize", methods=["GET"])
def authorize():

	print("Authorization request header ... ")
	print(request.headers)

	stream_name = request.headers.get(config["stream_name_h_field"])
	print(f"X-Stream-Name (extracted): {stream_name}")
	# TODO this name will contain quality extension as well 
	
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
	# Return value is ignored, only the status code is checked.
	

def is_authorized(user: str, stream: str) -> bool:
	# either db check
	# or with authenticate save user permissions as well in session
	print(f"Authorized: {user} for {stream} stream ... ")
	return True

if __name__ == '__main__':
	app.run(host="0.0.0.0", port='8003')