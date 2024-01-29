from flask import Flask, Response, request
from flask_restful import Api
from flask_api import status


app = Flask(__name__)
api = Api(app)

@app.after_request
def after_request(resp):
	resp.headers.add("Access-Control-Allow-Credentials","true")
	# resp.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
	resp.headers.add("Access-Control-Allow-Origin", f"{request.origin}")
	resp.headers.add("Access-Control-Allow-Headers","Content-type")

	return resp
	

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
	app.run(host="0.0.0.0", port='8010')
