from flask import Flask, Response, g, request
from flask_api import status
from flask_restful import Api
from requests import get, post

import jsonpickle

from app_config import AppConfig
from stream_data import StreamData
from shared_model.stream_info import StreamInfo
from shared_model.update_request import UpdateRequest
from db import Db


JSON_CONTENT_TYPE = 'application/json'

app = Flask(__name__)
api = Api(app)


def json_serialize(content) -> str:
	return jsonpickle.encode(content, unpicklable=False)


def get_db() -> Db:
	if 'db' not in g:
		print("creating request scoped db ... ")
		config = AppConfig.get_instance()
		address = config["db_address"]
		port = config["db_port"]
		db = config["db_name"]
		user = config["db_user"]
		pwd = config["db_password"]
		g.db = Db(f"mongodb://{user}:{pwd}@{address}:{port}/{db}")

	print("returning request scoped db ... ")
	return g.db


def close_db():
	db = g.pop('g', None)
	if db is not None:
		db.close()


def get_db_url() -> str:
	config = AppConfig.get_instance()
	return f"mongodb://{config.db_address}:{config.db_port}/{config.db_table}"


@app.route('/by_creator/<creator>', methods=['GET'])
def get_by_creator(creator: str):
	print(f"by_creator request: {creator}")

	stream_info = get_db().get_by_creator(creator)
	if stream_info is None:
		return "This creator is not live ... ", status.HTTP_404_NOT_FOUND

	return json_serialize(stream_info), status.HTTP_200_OK

@app.route('/update', methods=['POST'])
def update():
	print("Received update request .. ")

	content_type = request.headers.get('Content-type')
	if content_type != JSON_CONTENT_TYPE:
		return f"Content-type not supported.", status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

	try:
		update_request = UpdateRequest(**request.get_json())
		if update_request is None:
			raise Exception("Failed to parse info.")
		
	except TypeError as e:
		print("Error while parsing update request.")
		print(f"Err: {e}")
		return "Error while parsing update request. ", status.HTTP_400_BAD_REQUEST

	try:
		auth_res: Response = post(url=form_auth_url(), cookies=request.cookies)
		print(f"Auth stat_code: {auth_res}")
		if auth_res.status_code != 200:
			raise Exception("Failed to authenticate ... ")
	except:
		print("User not authenticated ... ")
		return "User not authenticated ... ", status.HTTP_401_UNAUTHORIZED

	auth_data = auth_res.json()

	res = get_db().update(auth_data["username"], update_request)

	if res is None:
		print("Failed to update stream info ... ")
		return "Failed to perform update ... ", status.HTTP_500_INTERNAL_SERVER_ERROR
	
	return json_serialize(res), status.HTTP_200_OK
			

def form_auth_url():
	config = AppConfig.get_instance()
	auth_ip = config["auth_service_ip"]
	auth_port = config["auth_service_port"]
	auth_path = config["authenticate_path"]
	return  f"http://{auth_ip}:{auth_port}/{auth_path}"

@app.route("/by_category/<category>", methods=['GET'])
def get_by_category(category: str):
	print(f"by_category request: {category}")

	from_ind = request.args.get(key="from", type=int)
	to_ind = request.args.get(key="to", type=int)

	streams = get_db().get_by_category(category, from_ind, to_ind)
	if streams is None:
		return "No such category ... ", status.HTTP_200_OK

	return json_serialize(streams), status.HTTP_200_OK

# This is used by the ingest instance so therefore
# request.ip should be the ingest instance's ip.
@app.route("/start_stream", methods=["POST"])
def start_stream():
	
	args = url_decode(request.get_data().decode())
	key = args.get("name")
	ingest_ip = args.get("addr")

	try:
		match_res = get(form_match_key_url(key))

		if match_res.status_code != 200:
			raise Exception(f"Auth service returned: {match_res.status_code}")

		db_res = get_db().save_empty(match_res.text, ingest_ip, key)
		if db_res is None:
			return "Failure.", status.HTTP_400_BAD_REQUEST

		response = Response(status=302)
		response.headers["Location"] = match_res.text
		print(f"match result: {key} -> {match_res.text}")
		return response

	except Exception as e:
		print("Failed to match key ... ")
		print(e)

		return "Failure ... ", status.HTTP_500_INTERNAL_SERVER_ERROR

def form_match_key_url(key:str):
	config = AppConfig.get_instance()
	ip = config["auth_service_ip"]
	port = config["auth_service_port"]
	match_key_path = config["match_key_path"]
	return f'http://{ip}:{port}/{match_key_path}/{key}'

# IT IS REQUIRED that data is str and not byte or byte[] !!!
# To translate byte/byte[] to string use .decode() method. 
def url_decode(data:str):
	return { pair.split("=")[0]:pair.split("=")[1]  for pair in data.split("&")}

@app.route("/stop_stream", methods=["POST"])
def stop_stream():
	args = url_decode(request.get_data().decode())
	stream_key = args['name']

	get_db().remove_stream(stream_key)

	return "Stream removed ... ", status.HTTP_200_OK

if __name__ == '__main__':
	# app.run(port='8002')
	app.run(host='0.0.0.0', port='8002')  # possibly will be required

# check out this link
# how to create/start/stop containers over rest
# https://docs.docker.com/engine/api/v1.19/#/inside-docker-run