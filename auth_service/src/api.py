import random
import string

from flask import Flask, Response, request, session, g
from flask_api import status
from flask_cors import CORS
from flask_restful import Api
from flask_session import Session

from requests import get

from shared_model.auth_request import AuthRequest
from shared_model.user import User
from shared_model.auth_response import AuthResponse
from shared_model.key_response import KeyResponse, KeyStatus
from shared_model.register_request import RegisterRequest
from shared_model.users_query_response import UsersQueryResponse

from user_doc import UserDoc
from app_config import AppConfig
from stream_key_doc import StreamKeyDoc
from db import Db

import jsonpickle

from datetime import datetime, timedelta

from bcrypt import hashpw, checkpw, gensalt

USER_SESSION_VAR = "user"

config = AppConfig.get_instance()

app = Flask(__name__)
api = Api(app)

CORS(app, support_credentials=True)
CORS(app)
 
app.secret_key = config["session_secret_key"] 
app.config["SESSION_TYPE"] = config["session_type"]
# TODO switch to redis as a session_type

Session(app)

def json_serialize(content):
	return jsonpickle.encode(content, unpicklable=False, indent=4)

def json_parse(txt):
	return jsonpickle.decode(txt)

def gen_stream_key(len) -> StreamKeyDoc:
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
	# Maybe do this instead of just localhost:3000
	resp.headers.add("Access-Control-Allow-Origin", f"{request.origin}")
	# resp.headers.add("Access-Control-Allow-Origin","http://localhost:3000")
	resp.headers.add("Access-Control-Allow-Headers","Content-type")

	return resp

@app.route("/register", methods=["POST"])
def register():

	print("Processing register request.")

	if request.data is None:
		print("Data not provided.")
		res = AuthResponse.bad_request("No data provided ...")
		return json_serialize(res), status.HTTP_400_BAD_REQUEST # bad request
	
	if not request.is_json:
		print("Provided data is not in json format.")
		res = AuthResponse.bad_request("Json data required ...")
		return json_serialize(res), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE # unsupported media type 
	
	try:
		reg_request = RegisterRequest(**request.get_json())

		if reg_request is None:
			print("Failed to parse data ")
			print(request.get_json())
			raise Exception("Error parsing data ... ")
		
	except TypeError:
		print("Unable to parse incoming data: ")
		print(request.get_json())

		res = AuthResponse.bad_request("Error parsing data ...")
		return json_serialize(res), status.HTTP_400_BAD_REQUEST
		# Should return 422 but this one is not defined in status.
	
	print("Querying database.")
	user = get_db().get_user(reg_request.username)

	if user is not None:
		print("Username is taken ... ")
		res = AuthResponse.already_exists("Username taken ...")
		return json_serialize(res), status.HTTP_200_OK
	
	print("Creating new user.")
	new_user = UserDoc(username = reg_request.username,
					email = reg_request.email,
					pwd_hash = hashpw(reg_request.password.encode(), gensalt()))

	ret_obj = get_db().save_user(new_user)

	if ret_obj is not None:
		print("User successfully registered ... ")
		res = AuthResponse.success(to_public_user(ret_obj))
		return json_serialize(res), status.HTTP_200_OK
	else:
		print("Failed to create new user.")
		res = AuthResponse.failed("Failed to create new user ...")
		return json_serialize(res), status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route("/authenticate", methods=["POST"])
def authenticate():

	print("Processing authenticate request: ")

	print(request.cookies)

	if USER_SESSION_VAR in session:
		print(f"User was already authenticated ... ")
		user_data: UserDoc = session[USER_SESSION_VAR]

		res_data = AuthResponse.success(to_public_user(user_data))

		response = Response(status=status.HTTP_200_OK, 
						content_type='application/json',
						response=json_serialize(res_data))
		return response

	if request.data is None or request.data == b'':
		print("No data provided.")
		res_data = AuthResponse.bad_request("No data provided.")

		return json_serialize(res_data), status.HTTP_400_BAD_REQUEST

	print("Received data:")
	print(request.data)

	if not request.is_json:
		print("Json data expected.")
		res_data = AuthResponse.bad_request("Json data required.")

		return json_serialize(res_data), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
	
	try:
		auth_request = AuthRequest(**request.get_json())

		if auth_request is None:
			print("Invalid data provided.")
			raise Exception("Failed to parse data ... ")

		print(json_serialize(auth_request))

	except (TypeError, Exception) as e:
		print("Unable to parse incoming data: ")
		print(f"Err: {e}")

		res_data = AuthResponse.bad_request("Failed to parse data ...")

		return json_serialize(res_data), status.HTTP_400_BAD_REQUEST

	user: UserDoc = get_db().get_user(auth_request.username)

	if user is None:
		print("User doesn't exists.")
		res_data = AuthResponse.failed("User doesn't exists.")

		return json_serialize(res_data), status.HTTP_200_OK
	
	if not checkpw(auth_request.password.encode(), user.pwd_hash):
		print("Wrong password ... ")
		res_data = AuthResponse.failed("Wrong password ... ")

		return json_serialize(res_data), status.HTTP_200_OK
	
	print(f"Successfully authenticated {auth_request.username}.")
	session[USER_SESSION_VAR] = user

	res_data = AuthResponse.success(to_public_user(user))
	response = Response(status=status.HTTP_200_OK,
					content_type='application/json',
					response=json_serialize(res_data))

	return response

@app.route("/get_key", methods=["GET"])
def get_key():

	print("Processing get key request.")

	if USER_SESSION_VAR not in session:
		print("Not authorized to obtain key.")
		res = KeyResponse(status=KeyStatus.FAILED, message="Not authorized ...")
		return json_serialize(res), status.HTTP_403_FORBIDDEN
	
	user: UserDoc = session[USER_SESSION_VAR]
	key: StreamKeyDoc = get_db().get_key_with_owner(user)

	print(f"KeyOwner: {user.username}")

	if key is None:
		print("Key not found, will generates new ... ")
		key = StreamKeyDoc()
		key.owner = user

	if key.is_expired():
		print("Key expired or not initialized, will reinitialize ... ")
		
		key.value = gen_stream_key(config["stream_key_len"])
		key.exp_date = gen_exp_date(config['stream_key_longevity'])
		
	get_db().save_key(key)
	print(f"Returning key: {key.value}")

	res = KeyResponse(status=KeyStatus.SUCCESS, 
				value=key.value, 
				exp_data=key.exp_date.isoformat() )
	
	return json_serialize(res), status.HTTP_200_OK

# Accessed by the stream_registry api.
@app.route("/match_key/<req_key>", methods=["GET"])
def match_key_get(req_key: str):

	print("Processing match key request. ")

	if req_key is None or req_key == "":
		res = KeyResponse(status=KeyStatus.FAILED, message="No key provided ...")
		return json_serialize(res), status.HTTP_400_BAD_REQUEST

	key = get_db().get_key_with_val(req_key)
	
	if key is None or key.is_expired():
		print("Invalid/expired key provided ... ")
		res = KeyResponse(status=KeyStatus.FAILED, message="Invalid/Expired key provided ...")
		return json_serialize(res), status.HTTP_404_NOT_FOUND

	# Every key is one time use. 
	# Match key is used by the ingest instance. 
	get_db().invalidate_key(key)

	res = KeyResponse(status=KeyStatus.SUCCESS, value=key.owner.username)
	print(f"Key matched with: {key.owner.username}")
	return json_serialize(res), status.HTTP_200_OK

def url_decode(data:str):
	return { pair.split("=")[0]:pair.split("=")[1]  for pair in data.split("&")}

@app.route("/authorize", methods=["GET"])
def authorize():

	# I could just do tokens-api/verify call to ensure session for this viewer
	# exists ... it's something. 

	print("Processing authorization request ... ")

	stream_name = request.headers.get(config["stream_name_h_field"])
	print(f"Stream name (from header): {stream_name}")
	
	if USER_SESSION_VAR not in session:
		print("No user session, not authorized ... ")
		return forbiden_res()
		
	print("User is authenticated ... ")
	user: UserDoc = session[USER_SESSION_VAR]

	if is_authorized(user.username, stream_name):
		resp = AuthResponse.success(to_public_user(user))
		return json_serialize(resp), status.HTTP_200_OK
	else:
		return forbiden_res()
		# redirect to login or just ... discard

@app.route("/get_user/<username>", methods=["GET"])
def get_user(username: str):

	print(f"Processing get user request for: {username}")

	if USER_SESSION_VAR not in session:
		print("NotAuthenticated user requested user data ... ")
		return forbiden_res()
	
	print("Get user requester is authenticated.")

	user: UserDoc = get_db().get_user(username)
	if user is None: 
		print("Failed to retrieve requested user's data.")	
		data = AuthResponse.failed("Failed to find requested data.")
		return json_serialize(data), status.HTTP_200_OK

	data = AuthResponse.success(to_public_user(user))
	
	return json_serialize(data), status.HTTP_200_OK

@app.route("/get_following/<username>", methods=["GET"])
def get_followers(username: str):

	print(f"Processing get followers request for: {username}")

	from_ind = int(request.args.get("from", default=0))
	count = int(request.args.get("count", default=10))

	if USER_SESSION_VAR not in session:
		print("User is not authenticated ... ")
		return forbiden_res()

	requester: UserDoc = session[USER_SESSION_VAR]

	if requester.username != username:
		print(f"User: {requester.username} is not authorized for this request.")
		return forbiden_res()

	user: UserDoc = get_db().get_user(username)
	if user is None: 
		print(f"Failed to find user: {username}")
		res = AuthResponse.failed("No such user.")
		return json_serialize(res), status.HTTP_200_OK

	followed_docs: [UserDoc] = get_db().get_followers_of(user, from_ind, count)
	if followed_docs is None or len(followed_docs) == 0: 
		print("Failed to obtain followed users.")
		res = UsersQueryResponse(for_user=username, result=[])

		return json_serialize(res), status.HTTP_200_OK
	
	followed_users = list(map(to_public_user, followed_docs))
	res = UsersQueryResponse(for_user=username, result=followed_users)

	return json_serialize(res), status.HTTP_200_OK

def is_authorized(user: str, stream: str) -> bool:
	# either db check
	# or with authenticate save user permissions as well in session
	print(f"Authorized: {user} for {stream} stream ... ")
	return True

def to_public_user(model: UserDoc)->User:
	return User(username=model.username, email=model.email)

def forbiden_res():
	r = Response()
	r.status = status.HTTP_403_FORBIDDEN
	r.content_type = 'Application/json'
	r.set_data(json_serialize(AuthResponse.forbidden()))
	return r

@app.route("/help", methods=["GET"])
def help():

	return "yo yo", status.HTTP_200_OK

	get_res:Response = get("http://session-stream-registry:8002/get_explore")

	if get_res is None: 
		print("Response is None.")
		return "Failed. ", status.HTTP_200_OK
	
	print("Result successfull.")
	return "Yo", status.HTTP_200_OK

if __name__ == '__main__':
	app.run(host="0.0.0.0", port="8003")