from datetime import datetime, timedelta
import random
import string
from typing import Any, Dict, List
import jsonpickle

from config import config

from flask import Response, g
from flask import Flask, abort
from flask_cors import CORS
from flask_api import status
from requests import get 

from supertokens_python.recipe import session

from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import emailpassword

# from supertokens_python.recipe import thirdpartyemailpassword
# from supertokens_python.recipe.thirdpartyemailpassword.interfaces import RecipeInterface, SignInOkResult, SignUpOkResult

from supertokens_python.types import GeneralErrorResponse
from supertokens_python.recipe.emailpassword.types import FormField, InputFormField
from supertokens_python.recipe.emailpassword import InputSignUpFeature
from supertokens_python.recipe.emailpassword.interfaces import SignInPostOkResult, SignUpPostOkResult
from supertokens_python.recipe.emailpassword.interfaces import APIInterface, APIOptions
from supertokens_python.recipe.session.framework.flask import verify_session
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.asyncio import delete_user

from supertokens_python import get_all_cors_headers
from supertokens_python.framework.flask import Middleware as TokensMiddleware
from shared_model.key_response import KeyResponse, KeyStatus
from shared_model.stream_key import StreamKey
from shared_model.user import User
from tokens_api.db_model import StreamKeyDoc, UserDoc

import users_db

def jsonify(obj):
	return jsonpickle.encode(obj, unpicklable=False)

def override_default_emailpassword(defaultImp: APIInterface)->APIInterface: 

	default_sign_in = defaultImp.sign_in_post
	default_sign_up = defaultImp.sign_up_post

	# TODO this actually doesn't have to overridden
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
			print(f"Sign in failed with: {result.to_json()}")
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

		print(f"Username found: {username_field.value}")

		result = await default_sign_up(form_fields, 
								tenant_id, 
								api_options, 
								user_context)
		
		if not isinstance(result, SignUpPostOkResult):
			print(f"Tokens signup failed with")
			return result
		
		print("Signup successfull")
		new_user = UserDoc(tokens_id=result.user.user_id,
					username=username_field.value,
					email=result.user.email)
		users_db.save_user(new_user)
		# TODO handle db errors ... 

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
		api_domain="http://localhost:8004",
		api_base_path="/auth",
		website_domain="http://localhost:3000",
		website_base_path="/"
	),
	supertokens_config=SupertokensConfig(
		connection_uri="http://session-tokens-core:3567",
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
		session.init({
			sessionTokenFrontendDomain: ".example.com"
		})
	],
	# debug=True,
	mode='asgi' # use wsgi if you are running using gunicorn
)

app = Flask(__name__)
TokensMiddleware(app)

CORS(
	app=app,
	origins=[
		"http://localhost:3000",
		"http://session-stream-registry:8002"
	],
	supports_credentials=True,
	allow_headers=["Content-Type"] + get_all_cors_headers(),
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

@app.route("/get_key", methods=["GET"])
@verify_session()
def get_key():
	print("Processing get key request.")

	# Session has to exists since method is decorated with @verify_session()
	session: SessionContainer = g.supertokens
	tokens_id = session.get_user_id()

	# I guess this has to be not None as well.
	user = users_db.get_user_by_tokens_id(tokens_id)
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

@app.route("/get_user/<username>", methods=["GET"])
def get_user(username:str):
	response = Response()

	try:
		user:UserDoc = users_db.get_user_by_username(username)

		if user is not None: 
			response.status_code=status.HTTP_200_OK
			response.set_data(jsonify(user))
		else:
			response.status_code=status.HTTP_404_NOT_FOUND

	except Exception as e:
		print(f"Exception in get_user query: {e}")
		response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR

	return response

# not protected, used just for bots
@app.route("/remove/<username>", methods=["GET"])
async def remove_user(username: str):
	user:UserDoc = users_db.get_user_by_username(username)
	if user is None: 
		print("No such user.")
		return "No such user.", status.HTTP_404_NOT_FOUND

	print(f"Found user: {user.to_json()}")

	await delete_user(user.tokens_id) # returns None
	print("User removed from custom db.")
	users_db.remove_user(user)
	print("User removed from tokens db.")

	return "Should be success.", status.HTTP_200_OK

@app.route("/verify/<username>", methods=["GET"])
@verify_session()
def authorize(username):

	session: SessionContainer = g.supertokens
	tokens_id = session.get_user_id()	

	# User has to be not None, if session exists there has to be 
	# a valid user associated with it.
	user = users_db.get_user_by_tokens_id(tokens_id)
	if user.username == username:
		return "ok", status.HTTP_200_OK
	else:
		return "not authorized", status.HTTP_401_UNAUTHORIZED


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8100)