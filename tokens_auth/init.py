from requests import get
import supertokens_python
from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import thirdpartyemailpassword, session
from supertokens_python.recipe.session.framework.flask import verify_session
from supertokens_python.recipe.session import SessionContainer

from supertokens_python.recipe.emailpassword.syncio import get_user_by_id
from supertokens_python.recipe.emailpassword.syncio import get_user_by_email
from flask import g, request

from supertokens_python.recipe.thirdparty.provider import ProviderInput, ProviderConfig, ProviderClientConfig
from supertokens_python.recipe import thirdpartyemailpassword

from supertokens_python import get_all_cors_headers
from flask import Flask, abort
from flask_cors import CORS 
from supertokens_python.framework.flask import Middleware as TokensMiddleware

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
		session.init(),# initializes session features
		thirdpartyemailpassword.init(
		   # TODO: See next step
		)
	],
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


# TODO Get_user_by_id or by_email will result in error stating supertokens.init()
# is not called when clearly it is. 
# If this gets fixed it will be the simplest solution to stream viewer 
# authorization required by the nginx hls encryption.
@app.route('/verify', methods=['GET'])
@verify_session()
def verify():

	print("Processing verify session request.")

	session: SessionContainer = g.supertokens
	
	if session is None:
		print("No session found")
		return "No session found.", 401
		
	print("Session found.")

	id = session.get_user_id()
	if id is None:
		print("Failed to obtain user id.")
		return "Failed to obtain user id.", 401

	print(f"User id obtained: {id}")

	return "User authenticated (everyone is authorize)", 200

	# user = get_user_by_email("public","some@some.com")

	# if user is None:
	# 	print("Got NONE as a user.")
	# 	return "", 200

	# print("GOT AN USER")
	# print(user)
	# return "", 200

	# core_res = get("http://session-tokens-core:3567/user",
	#  	params={'userId':id},
	# 	headers={
	# 			'rid': 'emailpassword',
	# 			'cdi-version': "2.9"
	# 		})
	
	# if core_res is not None:
	# 	if core_res.status_code == 200:
	# 		print("Core success.")
	# 		print(core_res.text)
	# 	else:
	# 		print("Did core request but not 200 code.")
	# 		print(core_res.text)
	# else:
	# 	print("Core request failed.")

	# return id, 200

	# data = None
	# try:
	# 	data = await session.get_session_data_from_database()
	# 	if data is None:
	# 		raise Exception("Data is None.")
	# except:
	# 	print("Exception ih get session data.")
	# 	return "Exception ih get session data.", 200



	# user_info = None
	# try:
	# 	user_info = get_user_by_id("publics",id)
	# except Exception as e:
	# 	print("Exception while getting user info")
	# 	print(e)

	# 	return "Exception in get_user", 200

	# if user_info is None:
	# 	print("Failed to obtain user info ")
	# 	return "Failed to obtain user info.", 200

	# print("We got user info.")
	# print(user_info)

	# return "Placeholder value.", 200


# This is required since if this is not there, then OPTIONS requests for
@app.route('/', defaults={'u_path': ''})  
@app.route('/<path:u_path>')  
@verify_session()
def catch_all(u_path: str):
	abort(404)
	
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8100)