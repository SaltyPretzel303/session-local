from datetime import datetime, timedelta, UTC
import random
import string
from typing import Any, Dict, List
from requests import post
import uvicorn
from httpx import AsyncClient 

from config import config

from shared_model.continue_view_request import ContinueViewRequest
import users_db

from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python import get_all_cors_headers

from supertokens_python.types import GeneralErrorResponse

from supertokens_python.recipe import emailpassword
from supertokens_python.recipe import session
from supertokens_python.recipe.emailpassword.types import FormField, InputFormField
from supertokens_python.recipe.emailpassword import InputSignUpFeature
from supertokens_python.recipe.emailpassword.interfaces import SignInPostOkResult, SignUpPostOkResult
from supertokens_python.recipe.emailpassword.interfaces import APIInterface, APIOptions

from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
# from supertokens_python.recipe.session.syncio import get_session

from supertokens_python.asyncio import delete_user

# from supertokens_python.framework.flask import Middleware as TokensMiddleware
from supertokens_python.framework.fastapi import get_middleware as get_fast_api_middleware

from shared_model.user import User as PublicUser
from shared_model.following_info import FollowingInfo
from shared_model.key_response import KeyResponse
from shared_model.stream_key import StreamKey
from shared_model.user import User

from tokens_api.db_model import FollowingDoc, StreamKeyDoc, UserDoc 

from fastapi.encoders import jsonable_encoder
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi import status as code
from starlette.middleware.cors import CORSMiddleware

def jsonify(obj):
	return jsonable_encoder(obj)

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
		api_domain=f"http://tokens-api.{config.domain_name}",
		api_base_path="/auth", # I thinks this is per documentation.
		website_domain=f"http://{config.domain_name}",
		website_base_path="/" # default is /auth, don't know why
	),
	supertokens_config=SupertokensConfig(
		connection_uri=f"http://tokens-core.{config.domain_name}:3567",
	),
	framework='fastapi',
	mode='wsgi', # required for uvicorn
	recipe_list=[
		emailpassword.init(
			sign_up_feature=InputSignUpFeature(form_fields=[
				InputFormField(id="username", validate=validate_username),
			]),
			override=emailpassword.InputOverrideConfig(
				apis=override_default_emailpassword
			)
		),
		
		session.init(
			# Also this can't be single word ...
			cookie_domain=f'.{config.domain_name}',
			# cookie_secure=True
			# For local development, you should not set the cookieDomain to an
			# IP address based domain, or .localhost - browsers will reject
			# these cookies. Instead, you should alias localhost to a named
			# domain and use that. 
		)
	],
	# debug=True,
)


app = FastAPI()
app.add_middleware(
	get_fast_api_middleware()
)
app.add_middleware(
	CORSMiddleware,
	allow_origins=[f'http://{config.domain_name}'],
	allow_credentials=True,
	allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "cookies"] + get_all_cors_headers(),
)

def gen_stream_key(len) -> StreamKeyDoc:
	chars = string.ascii_letters+string.digits
	return "".join(random.choice(chars) for i in range(len))

def gen_exp_date(longevity) -> datetime:
	return datetime.now(UTC) + timedelta(seconds=longevity)

@app.get("/auth/get_key")
def get_key(session: SessionContainer = Depends(verify_session())):
	print("Processing get key request.")

	if session is None: 
		raise HTTPException(status_code=code.HTTP_401_UNAUTHORIZED)

	tokens_id = session.user_id
	user = users_db.get_user_by_tokens_id(tokens_id)
	# I guess this has to be not None as well.

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
		print(f"Key date: {key.exp_date}")

	print(f"Key generated: {key.value}")
	users_db.save_key(key)

	return KeyResponse.success(value=key.value, expiration_date=key.exp_date)

# Nginx cant' forward cookies and this is used in on_publish callback.
# This should be guarded somehow but at this point ... it's fine.
@app.get("/match_key/{req_key}")
def match_key(req_key:str):

	print(f"Processing match key request with: {req_key}")

	if not req_key: # not None and not empty
		print("Invalid/no key provided.")
		res_data = KeyResponse.failure("Invalid/no key provider.")
		raise HTTPException(status_code=code.HTTP_400_BAD_REQUEST, detail=res_data)
		return jsonify(res_data), status.HTTP_400_BAD_REQUEST

	stream_key = users_db.get_key_by_value(req_key)

	if stream_key is None: 
		print("No such key.")
		# res_data = KeyResponse.failure("No such key")
		raise HTTPException(status_code=code.HTTP_404_NOT_FOUND, detail="No such key.")
	
	if stream_key.is_expired():
		print("Key invalid/expired.")
		# res_data = KeyResponse.failure("Key invalid.")
		raise HTTPException(status_code=code.HTTP_404_NOT_FOUND, detail="No such key.")

	users_db.invalidata_key(stream_key)

	res_data = KeyResponse.success(value=stream_key.owner.username)
	print(f"Key successfully matched with: {res_data.value}")

	return res_data

def to_public_user(model: UserDoc)->User:
	return User(username=model.username, email=model.email)

def to_publick_key(model: StreamKeyDoc)->StreamKey:
	return StreamKey(value=model.value,
				  exp_data=model.exp_date.isoformat())

def to_public_follow_record(record: FollowingDoc)->FollowingInfo:
	return FollowingInfo(username=record.owner.username,
					following=record.following.username, 
					from_date=record.followed_at)

@app.get("/get_user/{username}")
def get_user(username:str):

	print(f"Processing get user request for: {username}")

	if username is None or username == "":
		raise HTTPException(status_code=code.HTTP_400_BAD_REQUEST, 
					  	detail="Username not provided")

	user_data = users_db.get_user_by_username(username)

	if user_data is None: 
		raise HTTPException(status_code=code.HTTP_404_NOT_FOUND)

	return PublicUser(username=user_data.username, email=user_data.email)
	
@app.get("/get_user_from_tokensid/{tokensid}")
def get_user_from_tokensid(tokensid: str):
	print(f"Processing get user from tokensid for: {tokensid}")

	user_data = users_db.get_user_by_tokens_id(tokensid)
	if user_data is None:
		print("No user for such token.")
		raise HTTPException(status_code=code.HTTP_404_NOT_FOUND, 
					  	detail="No such user.")

	return to_public_user(user_data)

@app.get("/get_following")
def get_following(session: SessionContainer = Depends(verify_session())):
	print(f"Processing (session verified) get followed request.")

	if session is None: 
		raise HTTPException(status_code=code.HTTP_401_UNAUTHORIZED)
	
	tokens_id = session.user_id
	user = users_db.get_user_by_tokens_id(tokens_id)

	follow_data = users_db.get_following(user.username)
	if follow_data is None:
		print(f"Following query failed for: {user.username}")
		raise HTTPException(status_code=code.HTTP_500_INTERNAL_SERVER_ERROR)

	return list(map(to_public_follow_record, follow_data))

@app.get("/is_following/{whom}")
def is_following(whom: str, session: SessionContainer = Depends(verify_session())):
	if session is None: 
		raise HTTPException(status_code=code.HTTP_401_UNAUTHORIZED)

	follow_res = users_db.is_following(session.user_id, whom)
	if follow_res:
		return "Success, is following."
	else:
		raise HTTPException(status_code = code.HTTP_404_NOT_FOUND)

# not protected, used just for bots
@app.get("/remove/{username}")
async def remove_user(username: str):
	user:UserDoc = users_db.get_user_by_username(username)
	if user is None: 
		print("No such user.")
		raise HTTPException(status_code=code.HTTP_404_NOT_FOUND, 
					  	detail="No such user.")

	print(f"Found user: {user.to_json()}")

	await delete_user(user.tokens_id) # returns None
	print("User removed from tokens db.")

	users_db.remove_follow_rec_for(user)
	print("Follow records removed.")

	users_db.remove_user(user)
	print("User removed from session db.")

	return "Should be success."

@app.get("/is_authenticated")
def check_session(session: SessionContainer = Depends(verify_session())):
	print("Processing is authorized request.")
	if session is None: 
		print("Unauthorized")
		raise HTTPException(status_code=code.HTTP_401_UNAUTHORIZED)
	
	print("Authorized")
	return to_public_user(users_db.get_user_by_tokens_id(session.user_id))

@app.get("/auth/authorize_viewer")
async def authorize_viewer(request:Request, 
		session: SessionContainer = Depends(verify_session())):

	print("Processing authorize viewer request.")

	if session is None: 
		print("Unauthorized.")
		raise HTTPException(status_code=code.HTTP_401_UNAUTHORIZED)

	user = users_db.get_user_by_tokens_id(session.user_id)
	stream_name = request.headers.get("X-Stream-Username")
	# Lets just assume that the stream name is actually gonna be provided ... 

	print(f"Authorizing: {user.username} for: {stream_name}'s stream.")

	# TODO check stream limits at this point

	# Kinda fire and forget, still nice to have some return value.
	update_res = await update_view_count(user.username, stream_name)

	return to_public_user(user)

@app.get("/auth/authorize_chatter/{channel}")
async def authorize_chatter(request:Request, 
				channel: str,
				session: SessionContainer = Depends(verify_session())):
	
	print(f"Processing authorize chatter request for: {channel} channel.")

	if session is None: 
		print("Unauthorized.")
		raise HTTPException(status_code=code.HTTP_401_UNAUTHORIZED)

	user = users_db.get_user_by_tokens_id(session.user_id)

	print(f"Authorizing chatter: {user.username} for: {channel}")

	# everyone is authorized
	return to_public_user(user)

@app.get('/follow/{channel}')
async def follow(channel:str, session: SessionContainer = Depends(verify_session())):
	if session is None: 
		raise HTTPException(status_code=code.HTTP_401_UNAUTHORIZED)
	
	res = users_db.follow(session.user_id, channel)
	if res is None: 
		raise HTTPException(code.HTTP_500_INTERNAL_SERVER_ERROR)
	else: 
		return to_public_follow_record(res)
	
@app.get('/unfollow/{channel}')
async def unfollow(channel:str, session: SessionContainer = Depends(verify_session())):
	if session is None: 
		raise HTTPException(status_code=code.HTTP_401_UNAUTHORIZED)
	
	res = users_db.unfollow(session.user_id, channel)
	
	return "Success."

async def update_view_count(username, stream):
	print(f"Will update view count for: {stream}")

	async with AsyncClient() as client: 
		update_data = ContinueViewRequest(username, stream).__dict__
		resp = await client.post(url=config.view_update_url, json=update_data)
		if resp.status_code != code.HTTP_200_OK:
			print(f"View count update failed with code: {resp.status_code}")
			return False
		
	return True



# TODO remove 
@app.get("/fetch")
def fetch_cookie():

	resp = Response()
	resp.set_cookie(key="some_random_key", value='some_random_value')

	return resp

if __name__ == "__main__":
	uvicorn.run("api:app", host="0.0.0.0", port=80)
	# app.run(host="0.0.0.0", port=80)