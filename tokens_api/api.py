from datetime import datetime, timedelta
import random
import string
from typing import Any, Dict, List
import jsonpickle
from requests import post

from config import config

from shared_model.continue_view_request import ContinueViewRequest
import users_db

from flask_restful import Api
from flask import Response, g, request, Flask, abort
from flask_cors import CORS
from flask_api import status

from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python import get_all_cors_headers

from supertokens_python.types import GeneralErrorResponse

from supertokens_python.recipe import emailpassword
from supertokens_python.recipe import session
from supertokens_python.recipe.emailpassword.types import FormField, InputFormField
from supertokens_python.recipe.emailpassword import InputSignUpFeature
from supertokens_python.recipe.emailpassword.interfaces import SignInPostOkResult, SignUpPostOkResult
from supertokens_python.recipe.emailpassword.interfaces import APIInterface, APIOptions
from supertokens_python.recipe.session.framework.flask import verify_session
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.syncio import get_session

from supertokens_python.recipe.jwt.interfaces import CreateJwtOkResult

from supertokens_python.asyncio import delete_user

from supertokens_python.framework.flask import Middleware as TokensMiddleware
from shared_model.user import User as PublicUser
from shared_model.following_info import FollowingInfo
from shared_model.key_response import KeyResponse
from shared_model.stream_key import StreamKey
from shared_model.user import User

from tokens_api.db_model import FollowingDoc, StreamKeyDoc, UserDoc 

def jsonify(obj):
	return jsonpickle.encode(obj, unpicklable=False)

def override_default_emailpassword(defaultImp: APIInterface)->APIInterface: 

	default_sign_in = defaultImp.sign_in_post
	default_sign_up = defaultImp.sign_up_post

	# TODO this actually doesn't have to be overridden
	async def custom_sign_in(form_fields: List[FormField],
						  tenant_id: str,
						  api_options: APIOptions,
						  user_context: Dict[str, Any]):

		print("Doing some custom signIn logic.")

		result = await default_sign_in(form_fields=form_fields,
									tenant_id=tenant_id,
									api_options=api_options,
									user_context=user_context)

		if not isinstance(result, SignInPostOkResult):
			print(f"Sign in failed with: {result.status}")
		else:
			print("SignIn successfull.")

		return result

	async def custom_sign_up(form_fields: List[FormField],
						tenant_id: str, 
						api_options: APIOptions, 
						user_context: Dict[str, Any]):

		print("Processing supertoken signUp request (including custom logic).")

		username_field = filter_username_field(form_fields)
		if username_field is None: 
			print("SignUp form had no username field.")

			return GeneralErrorResponse(message="Username not provided.")

		print(f"Passed username: {username_field.value}")

		result = await default_sign_up(form_fields, 
								tenant_id, 
								api_options, 
								user_context)
		
		if not isinstance(result, SignUpPostOkResult):
			print(f"Tokens signup failed with: {result.status}")	
			return result
		
		print("Signup successfull")
		new_user = UserDoc(tokens_id=result.user.user_id,
					username=username_field.value,
					email=result.user.email)
		users_db.save_user(new_user)
		
		return result

	defaultImp.sign_in_post = custom_sign_in
	defaultImp.sign_up_post = custom_sign_up

	return defaultImp

def filter_username_field(fields: List[FormField])->FormField:
	return next(filter(lambda f: f.id == config.username_field, fields), None)

async def validate_username(username: str, tenant: str):
	print(f"Doing username validation on: {username}.")
	return None

init(
	app_info=InputAppInfo(
		app_name="react_app",
		# Has to be exact domain name, can't be patterns (can't start with .) 
		# like cookie_domain.
		# Domain name of the service exposing auth api.
		# https://supertokens.com/docs/emailpassword/common-customizations/sessions/multiple-api-endpoints
		api_domain="http://tokens-api.session.com",
		api_base_path="/auth", # I thinks this is per documentation.
		website_domain="http://session.com",
		website_base_path="/" # default is /auth, don't know why
	),
	supertokens_config=SupertokensConfig(
		connection_uri="http://tokens-core.session.com:3567",
	),
	framework='flask',
	recipe_list=[
		emailpassword.init(
			sign_up_feature=InputSignUpFeature(form_fields=[
				InputFormField(id="username", validate=validate_username),
			]),
			override=emailpassword.InputOverrideConfig(
				apis=override_default_emailpassword
			)
		),
		# thirdpartyemailpassword.init(
		# 	override=thirdpartyemailpassword.InputOverrideConfig(
		# 	   functions=override_default_emailpassword
		# 	)
		# ),
		session.init(
			# Also this can't be single word ...
			cookie_domain='.session.com',
			# cookie_secure=True
			# For local development, you should not set the cookieDomain to an
			# IP address based domain, or .localhost - browsers will reject
			# these cookies. Instead, you should alias localhost to a named
			# domain and use that. 
		)
	],
	# debug=True,
	mode='asgi' # use wsgi if you are running using gunicorn
)

app = Flask(__name__)
TokensMiddleware(app)
api = Api(app)

CORS(
	app=app,
	origins = 'http://session.com',
	# origins=[
	# 	"http://session.com", # This should be gateway ... ? 
	# 	# "http://localhost:3000",
	# 	# "http://session.com:3000",

	# 	# "http://session.com:[0-9]+",
	# 	# "http://session.com",
	# 	# "http://stream-registry.session.com:[0-9]+",
	# 	# "http://stream-registry.session.com"
	# 	# "http://localhost:3000",
	# 	# "http://stream-registry.session.com:8002"
	# ],
	supports_credentials=True,
	allow_headers=["Content-Type", "someField", "cookies"] + get_all_cors_headers(),
)

# This is required since if this is not there, then OPTIONS requests for
@app.route('/', defaults={'u_path': ''})  
@app.route('/<path:u_path>')  
@verify_session()
def catch_all(u_path: str):
	abort(404)
	
def gen_stream_key(len) -> StreamKeyDoc:
	chars = string.ascii_letters+string.digits
	return "".join(random.choice(chars) for i in range(len))

def gen_exp_date(longevity) -> datetime:
	return datetime.now() + timedelta(seconds=longevity)

@app.route("/auth/get_key", methods=["GET"])
@verify_session()
def get_key():
	print("Processing get key request.")

	# Session has to exists since method is decorated with @verify_session()
	session: SessionContainer = g.supertokens
	tokens_id = session.get_user_id()

	# I guess this has to be not None as well.
	user = users_db.get_user_by_tokens_id(tokens_id)
	print("Found user : ")
	print(user.to_json() if user is not None else "User is None.")
	key = users_db.get_key_for_user(user)

	if key is None:
		print("Key not found, will generate new.")
		key = StreamKeyDoc(owner=user)
	
	if key.is_expired():
		print("Key expired or not initialized, reinitialize.")
		key.value = gen_stream_key(config.stream_key_len)
		key.exp_date = gen_exp_date(config.stream_key_longevity)

	print(f"Key generated: {key.value}")
	users_db.save_key(key)

	key_resp = KeyResponse.success(value=key.value,
							expiration_date=key.exp_date)

	return jsonify(key_resp), 200

# Nginx cant' forward cookies and this is used in on_publish callback.
# This should be guarded somehow but at this point ... it's fine.
@app.route("/match_key/<req_key>", methods=["GET"])
# @verify_session()
def match_key(req_key:str):

	print(f"Processing match key request with: {req_key}")

	if not req_key: # not None and not empty
		print("Invalid/no key provided.")
		res_data = KeyResponse.failure("Invalid/no key provider.")
		return jsonify(res_data), status.HTTP_400_BAD_REQUEST

	stream_key = users_db.get_key_by_value(req_key)

	if stream_key is None: 
		print("No such key.")
		res_data = KeyResponse.failure("No such key")
		return jsonify(res_data), status.HTTP_404_NOT_FOUND
	
	users_db.invalidata_key(stream_key)

	res_data = KeyResponse.success(value=stream_key.owner.username)
	print(f"Key successfully matched with: {res_data.value}")

	return jsonify(res_data), status.HTTP_200_OK

def to_public_user(model: UserDoc)->User:
	return User(username=model.username, email=model.email)

def to_publick_key(model: StreamKeyDoc)->StreamKey:
	return StreamKey(value=model.value,
				  exp_data=model.exp_date.isoformat())

def to_public_follow_record(record: FollowingDoc)->FollowingInfo:
	return FollowingInfo(username=record.owner.username,
					following=record.following.username, 
					from_date=record.followed_at)

@app.route("/get_user/<username>", methods=["GET"])
def get_user(username:str):
	response = Response()

	try:
		user_data = users_db.get_user_by_username(username)

		if user_data is not None: 
			public_data = PublicUser(username=user_data.username,
									email=user_data.email)
			
			response.status_code=status.HTTP_200_OK
			response.set_data(jsonify(public_data))
		else:
			response.status_code=status.HTTP_404_NOT_FOUND

	except Exception as e:
		print(f"Exception in get_user query: {e}")
		response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR

	return response

@app.route("/get_user_from_tokensid/<tokensid>", methods=["GET"])
def get_user_from_tokensid(tokensid: str):
	print(f"Processing get user from tokensid for: {tokensid}")

	user_data = users_db.get_user_by_tokens_id(tokensid)
	if user_data is None:
		print("No user for such token.")
		return 'No such user', status.HTTP_404_NOT_FOUND

	public_data = PublicUser(username=user_data.username,
						email=user_data.email)
	print(f"Found user: {jsonify(public_data)}")
	return jsonify(to_public_user(public_data)), status.HTTP_200_OK

@app.route("/get_following", methods=["GET"])
@verify_session()
def get_following():
	print(f"Processing (session verified) get followed request.")

	session = g.supertokens
	tokens_id = session.get_user_id()
	user = users_db.get_user_by_tokens_id(tokens_id)

	follow_data = users_db.get_following(user.username)
	if follow_data is None:
		print(f"Following query failed for: {user.username}")
		return "Query failed.", status.HTTP_500_INTERNAL_SERVER_ERROR

	public_data = list(map(to_public_follow_record, follow_data))
	return jsonify(public_data), status.HTTP_200_OK

# not protected, used just for bots
@app.route("/remove/<username>", methods=["GET"])
async def remove_user(username: str):
	user:UserDoc = users_db.get_user_by_username(username)
	if user is None: 
		print("No such user.")
		return "No such user.", status.HTTP_404_NOT_FOUND

	print(f"Found user: {user.to_json()}")

	await delete_user(user.tokens_id) # returns None
	print("User removed from tokens db.")

	users_db.remove_follow_rec(user)
	print("Follow records removed.")

	users_db.remove_user(user)
	print("User removed from session db.")

	return "Should be success.", status.HTTP_200_OK

# TODO Refactor with fastapi so that the method can be async 
# since it will require viewers count update.
# TODO Split in two endpoints, one for user authentication and one for stream
# authorization and possibly one for non-viewer stream authorization if someone
# just want to search channel or something like that.
@app.route("/verify", methods=["GET"])
def authorize():
	print(f"Processing authorization.")

	# print("==== header ====")
	# print(request.headers)
	# print("==== header ====")

	print("==== cookies ====")
	print(request.cookies)
	print("==== cookies ====")

	session = get_session(request)

	if session is None: 
		print("No session.")
		return "Not authorized.", status.HTTP_403_FORBIDDEN

	tokens_id = session.get_user_id()
	stream_name = request.headers.get("X-Stream-Username")

	# User has to be not None, if session exists there has to be 
	# a valid user associated with it.
	user = users_db.get_user_by_tokens_id(tokens_id)
	if user is None: 
		print("Not authorized, token ip might be wrong/missing.")
		return "No such user.", status.HTTP_404_NOT_FOUND

	# Check stream limits. (these are not yet implemented)
 
	# Update viewer count. 
	if stream_name is not None: 
		# stream_name is gonna be None in the case some service is just trying
		# to verify users auth token. 
		print("Will update viewer count.")
		view_cnt_update = ContinueViewRequest(user.username, stream_name)
		try:
			update_res = post(url=config.view_update_url, json=view_cnt_update.__dict__)
			if update_res.status_code != 200:
				raise Exception(f"Status code: {update_res.status_code}")
			
		except Exception as e:
			print(f"Failed to update viewer count for {user.username}: {e}.")
			# User can still be authorized, failure reason could be just server error.
	else:
		print("Stream name not provided, simple token verification.")

	print(f"Authorized: {user.username} for {stream_name}.")
	return "Authorized.", status.HTTP_200_OK


@app.route("/chat/authorize")

@app.route("/fetch", methods=["GET"])
def fetch_cookie():

	resp = Response()
	resp.set_cookie(key="some_random_key", value='some_random_value')

	return resp, status.HTTP_200_OK

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=80)