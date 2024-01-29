from datetime import datetime, timedelta
from ipaddress import ip_address

from flask import Flask, Response, g, request
from flask_api import status
from flask_restful import Api
from requests import get, post

import jsonpickle

from app_config import AppConfig

from shared_model.media_server_request import MediaServerRequest
from shared_model.media_server_info import MediaServerInfo
from shared_model.stream_info import StreamInfo
from shared_model.update_request import UpdateRequest

from db import Db


JSON_CONTENT_TYPE = 'application/json'
CDN_MANAGER_ADDR = "session-cdn-manager:8004"
MATCH_REGION_PATH = "/match_region"

app = Flask(__name__)
api = Api(app)


def json_serialize(content) -> str:
	return jsonpickle.encode(content, unpicklable=False)


def get_db() -> Db:
	if 'db' not in g:
		config = AppConfig.get_instance()
		address = config["db_address"]
		port = config["db_port"]
		db = config["db_name"]
		user = config["db_user"]
		pwd = config["db_password"]
		g.db = Db(f"mongodb://{user}:{pwd}@{address}:{port}/{db}")

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
	print("Start stream request ... ")

	args = url_decode(request.get_data().decode())
	key = args.get("name")
	ingest_ip = args.get("addr") # this is gonna be the ip of nginx reverse proxy 

	print(f"Key: {key}")
	print(f"Source: {ingest_ip}")

	try:
		print("Sending match requst to auth service.")
		match_res = get(form_match_key_url(key))
		print("Received auth service response.")

		if match_res.status_code != 200:
			raise Exception(f"Auth service returned: {match_res.status_code}")

		match_data = match_res.json()

		print("Saving empty stream to db.")
		db_res = get_db().save_empty(match_data["value"], ingest_ip, key)
		if db_res is None:
			return "Failure.", status.HTTP_400_BAD_REQUEST
		print("Stream saved.")

		response = Response(status=302)
		response.headers["Location"] = match_data["value"]
		print(f"match result: {key} -> {match_data['value']}")
		return response

	except Exception as e:
		print("Failed to match key ... ")
		print(e)

		return "Failure ... ", status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route("/add_media_server", methods=["POST"])
def add_media_server():
	print("Processing media server request.")

	if request.data is None:
		return "No data provided ...", status.HTTP_400_BAD_REQUEST
	
	req_data = None
	try:
		req_data = MediaServerRequest(**jsonpickle.decode(request.get_json()))
		if req_data is None:
			raise Exception("Data parsed but appears to be empty ... ")
		
	except Exception as e: 
		print(f"err: {e}")
		return "Failed to parse data ...", status.HTTP_400_BAD_REQUEST
	
	print(f"Requesting to add media server:{req_data.media_server} to:{req_data.content_name}")

	add_res = get_db().add_media_server(req_data.content_name, req_data.media_server)

	if add_res is None:
		return "Failed to add media server ... ", status.HTTP_500_INTERNAL_SERVER_ERROR
	else:
		return "Success ... ", status.HTTP_200_OK

@app.route("/remove_media_server", methods=["POST"])
def remove_media_server():
	if request.data is None:
		return "No data provided ...", status.HTTP_400_BAD_REQUEST
	
	req_data = None
	try:
		req_data = MediaServerRequest(**jsonpickle.decode(request.get_json()))
		if req_data is None:
			raise Exception("Data parsed but appears to be empty ... ")
		
	except Exception as e: 
		print(f"err: {e}")
		return "Failed to parse data ...", status.HTTP_400_BAD_REQUEST
	
	print(f"Requesting to remove mediaIp: {req_data.media_server} from: {req_data.content_name}")

	get_db().remove_media_server(req_data.content_name, req_data.media_server)

	return "Success ... ", status.HTTP_200_OK


@app.route("/stream_info/<streamer>", methods=["GET"])
def get_stream_info(streamer: str):

	region = request.args.get("region", default="eu")

	print(f"Request for stream: {streamer} region: {region}")

	stream_data = get_db().get_stream(streamer)

	if stream_data is None:
		return "No such stream ... ", status.HTTP_404_NOT_FOUND

	if not stream_data.is_public:
		print("This is not public stream ... ")
		return "No such stream ... ", status.HTTP_404_NOT_FOUND

	match_res = get(f"http://{CDN_MANAGER_ADDR}/{MATCH_REGION_PATH}/{region}")

	if match_res.status_code != status.HTTP_200_OK:
		print(f"Failed to match region {region} ... ")
		return "Failed to match region ...", match_res.status_code
	
	print(f"RegionServer: {match_res.json()}")

	print(f"StreamServers: {stream_data.media_servers}")
	print(f"StreamServers: {list(map(int_to_ip,stream_data.media_servers))}")

	region_info = MediaServerInfo(**match_res.json())

	server = region_info if ip_to_int(region_info.ip) in stream_data.media_servers else None

	stream_info = StreamInfo(title=stream_data.title,
						  creator=stream_data.creator,
						  category=stream_data.category,
						  media_server = server)

	return json_serialize(stream_info), status.HTTP_200_OK

@app.route("/get_explore", methods=["GET"])
def get_explore():

	resp = Response()
	resp.status_code = status.HTTP_200_OK
	# resp.headers.add("Access-Control-Allow-Credentials","true")
	# resp.headers.add("Access-Control-Allow-Origin","http://localhost:3000")
	# resp.headers.add("Access-Control-Allow-Headers","Content-type")
	# resp.headers.add("Content-type", "application/json")
	resp.data = json_serialize(list(map(gen_stream_info,range(0, 10))))

	return resp

@app.route("/since/<isodate>", methods=["GET"])
def get_since(isodate: str):
	date = datetime.fromisodate(isodate)
	now = datetime.now()




@app.after_request
def after_request(resp):
	resp.headers.add("Access-Control-Allow-Credentials","true")
	resp.headers.add("Access-Control-Allow-Origin","http://localhost:3000")
	resp.headers.add("Access-Control-Allow-Headers","Content-type")

	return resp

def gen_stream_info(ind: int):
	return StreamInfo(f"title_{ind}", 
				f"creator_{ind}", 
				f"chatting",
				MediaServerInfo("127.0.0.1", 10000, "live","http://localhost:10000/live/streamer_subsd/index.m3u8") )

def ip_to_int(ip: str):
	print(f"ip: {ip} to: {int(ip_address(ip))}")
	return int(ip_address(ip))

def int_to_ip(ip: int):
	return str(ip_address(ip))

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

	print(f"Removing stream with the key: {stream_key}")

	get_db().remove_stream(stream_key)

	return "Stream removed ... ", status.HTTP_200_OK

if __name__ == '__main__':
	app.run(host='0.0.0.0', port='8002') 
