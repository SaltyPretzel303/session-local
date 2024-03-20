from flask import Flask, Response, request
from flask_restful import Api
from flask_api import status
from requests import get


app = Flask(__name__)
api = Api(app)

@app.after_request
def after_request(resp):
	# resp.headers.add("Access-Control-Allow-Credentials","true")
	# resp.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
	# resp.headers.add("Access-Control-Allow-Origin", f"{request.origin}")
	resp.headers.add("Access-Control-Allow-Headers","Content-type")
	# resp.headers.add("Access-Control-Allow-Headers","Set-cookie")
	resp.headers.add("Access-Control-Allow-Headers","Cookie")
	# resp.headers.add("Access-Control-Allow-Headers","X-Cookie")
	# resp.headers.add("Access-Control-Allow-Headers","credentials")

	return resp

auth_api = 'http://tokens-api.session.com:8100/appid-react_app/recipe/session/verify'

@app.route('/verify', methods=["GET"])
def verify():
	print("------")
	print("Will send verify request.")

	resp:Response = get(auth_api,cookies=request.cookies,headers=request.headers)

	if resp is not None and resp.status_code == 200:
		print("Received valid response.")
		return resp.text, status.HTTP_200_OK
	else: 
		print("Received invalid response.")
		return "", status.HTTP_200_OK

@app.route("/cookies", methods=['GET'])
def cookie_path():

	print("COOKIES:")
	print(request.cookies)

	return 'Success.', status.HTTP_200_OK

@app.route("/host",methods=["GET"])
def return_host():
	return f"addr: {request.remote_addr} user: {request.remote_user}", status.HTTP_200_OK

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
# @app.route("/k", methods=["GET", "POST"])
def key_match(path):
	print("========================")
	
	print("")
	print(f"PATH: {path}")
	print(f"URL: {request.url}")

	print("\tHEADERS:")
	print(request.headers)

	print("\tARGS:")
	print(request.args)

	print("\tDATA:")
	print(request.data)
	print("")
	print("========================")

	resp = Response(status=status.HTTP_200_OK, response="All good.")
	
	# resp.headers.add("Access-Control-Allow-Credentials","true")
	# # resp.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
	# resp.headers.add("Access-Control-Allow-Origin", f"{request.origin}")
	# resp.headers.add("Access-Control-Allow-Headers","Content-type")
	
	return resp

if __name__ == '__main__':
	app.run(host="0.0.0.0", port='80')
