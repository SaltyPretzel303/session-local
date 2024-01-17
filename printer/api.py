from flask import Flask, request
from flask_restful import Api
from flask_api import status


app = Flask(__name__)
api = Api(app)

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

	return "all good", status.HTTP_200_OK;


if __name__ == '__main__':
	app.run(host="0.0.0.0", port='8010')
