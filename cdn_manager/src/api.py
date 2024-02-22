from sys import argv
from flask import Flask, request
from flask_restful import Api
from flask_api import  status
from requests import get, post

from app_config import AppConfig
from instance_conf import InstanceConf
from jsonpickle import encode
from shared_model.media_server_info import MediaServerInfo

from shared_model.media_server_request import MediaServerRequest
import re 


app = Flask(__name__)
api = Api(app)

QUAL_HD = "hd"
QUAL_SD = "sd"
QUAL_SUBSD = "subsd"

STREAM_REGISTRY_ADDR = 'stream-registry.session:8002'
ADD_MEDIA_SERVER_PATH = '/add_media_server'
REMOVE_MEDIA_SERVER_PATH = '/remove_media_server'

@app.route("/ping", methods=["GET"])
def ping():
	return "Pong.", status.HTTP_200_OK

@app.route("/initialize", methods=["POST"])
def initialize():
	AppConfig.load_config(request.get_json())

	return "Configuration loaded ... ", status.HTTP_200_OK

@app.route("/match_region/<region>", methods=["GET"])
def match_region(region:str):
	config = AppConfig.instance

	if region not in config:
		return "Region not available ... ", status.HTTP_404_NOT_FOUND
	
	info = None
	if is_available(config[region][0]):
		info = config[region][0]
	else:
		print(f"Region's ({region}) main instance is not available ... ")

		alt_instance = next(filter(is_available, config[region][1:]), None)

		if alt_instance is not None:
			info = alt_instance

	if info is None:
		return "Failed to match region ...", status.HTTP_503_SERVICE_UNAVAILABLE
	
	server_info = MediaServerInfo(ip=info.ip,
						  port=info.hls_port,
						  media_path=info.hls_path,
						  full_path = form_hls_path(info))
	
	return encode(server_info, unpicklable=False), status.HTTP_200_OK

@app.route("/add_media_server", methods=["POST"])
def add_media_server():
	print("Request to add content ... ")

	args = url_decode(request.get_data().decode())
	content_name = args.get("name")
	instance_ip = request.remote_addr
	

	(creator, quality) = split_name_qual(content_name) 
	if creator is None or quality is None: 
		return "Name and quality in wrong format ...", status.HTTP_500_INTERNAL_SERVER_ERROR
	
	print(f"Content: {content_name} at: {instance_ip}")

	req = MediaServerRequest(content_name=creator,
						quality=quality,
						media_server=instance_ip)
	
	req_data = encode(req,unpicklable=False)
	try:
		print("Doing post towars registry.")
		add_res = post(url=f"http://{STREAM_REGISTRY_ADDR}/{ADD_MEDIA_SERVER_PATH}", json=req_data)
	except Exception as e:
		print("Request toward registry failed.")
		print(e)

	if add_res is None or add_res.status_code != status.HTTP_200_OK:
		print("Failed to add media server ... ")
		return "Failure ... ", status.HTTP_500_INTERNAL_SERVER_ERROR
	
	return "Noted ...", status.HTTP_200_OK

def split_name_qual(value: str):
	pattern = f"(.+)_({QUAL_HD}|{QUAL_SD}|{QUAL_SUBSD})$"
	res = re.search(pattern, value)

	if res is None:
		return (None, None)
	
	return (res[1],res[2])



@app.route("/remove_media_server", methods=["POST"])
def remove_media_server():
	print("Request to remove media server ... ")

	args = url_decode(request.get_data().decode())
	content_name = args.get("name")
	instance_ip = args.get("addr")

	(creator, quality) = split_name_qual(content_name) 
	if creator is None or quality is None: 
		return "name and quality in wrong format ...", status.HTTP_500_INTERNAL_SERVER_ERROR
	
	print(f"Content: {content_name} at: {instance_ip}")

	req = MediaServerRequest(content_name=creator,
						quality=quality,
						media_server=instance_ip)
	
	req_data = encode(req,unpicklable=False)

	add_res = post(url=f"http://{STREAM_REGISTRY_ADDR}/{REMOVE_MEDIA_SERVER_PATH}", json=req_data)
	
	if add_res is None or add_res.status_code != status.HTTP_200_OK:
		print("Failed to remove media server ... ")
		return "Failure ... ", status.HTTP_500_INTERNAL_SERVER_ERROR
	
	return "Noted ...", status.HTTP_200_OK

def form_hls_path(inst: InstanceConf):
	return f"http://{inst.ip}:{inst.hls_port}/{inst.hls_path}"

def is_available(conf: InstanceConf):
	url = form_hc_path(conf)
	print(f"Checking: {url}")
	try:
		res = get(url)
		if res.status_code != status.HTTP_200_OK:
			raise Exception(f"Host on: {url} unavailable ... ")
	except: 
		return False

	return True

def form_hc_path(inst: InstanceConf):
	return f"http://{inst.ip}:{inst.hc_port}/{inst.hc_path}"
	
def url_decode(data:str):
	return { pair.split("=")[0]:pair.split("=")[1]  for pair in data.split("&")}

if __name__ == '__main__':

	if len(argv) > 1:
		print("External cdn configuration passed: ")
		print(argv[1])

		AppConfig.load_config(argv[1])

	app.run(host="0.0.0.0", port='8004')
