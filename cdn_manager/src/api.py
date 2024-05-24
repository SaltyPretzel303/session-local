from sys import argv
from typing import Tuple
from flask import Flask, request
from flask_restful import Api
from flask_api import  status
from requests import get, post

from app_config import AppConfig
from app_config import  ADD_MEDIA_SERVER_PATH
from app_config import REMOVE_MEDIA_SERVER_PATH
from app_config import STREAM_REGISTRY_ADDR

from instance_conf import InstanceConf
from jsonpickle import encode
import re 

from shared_model.media_server_request import MediaServerRequest

app = Flask(__name__)
api = Api(app)

QUALITIES = ['sd', 'subsd']
PREVIEW_QUALITY = 'preview'
STREAM_QUALITY = 'stream'

# QUAL_HD = "hd"
# QUAL_SD = "sd"
# QUAL_SUBSD = "subsd"



# TODO ^ move this to the config

# ==================

# In case you wonder why it exists and not just forward all requests to 
# stream registry directly.

# Nginx cdns can't know in which region they are deployed. This service keeps
# track of alive cdn servers and adds region information to each request 
# coming from the cdn instance. Currently those are add_media_server on 
# stream begining and remove_media_server once the stream is stopped.

# Another approach would be to register all deployed cdns in stream-registry.

# Just let it be. 

# ==================

@app.route("/ping", methods=["GET"])
def ping():
	return "Pong.", status.HTTP_200_OK

@app.route("/initialize", methods=["POST"])
def initialize():
	AppConfig.load_config(request.get_json())
	print("Configuration loaded.")

	return "Configuration loaded.", status.HTTP_200_OK

def filter_region_with_ip(ip: str)->Tuple[str, InstanceConf]:
	conf = AppConfig.get_instance()
	for region in conf:
		instance = next(filter(lambda inst: inst.ip == ip, conf[region]), None)
		if instance is not None:
			return (region, instance)
		
	return (None, None)

def form_media_url(server:InstanceConf, content:str):
	# Enforce use of domainName instead of ip:port since suprtokens will look
	# at domain root and decide to send credentials or not.
	return f"http://{server.domainName}/{server.hls_path}/{content}.m3u8"

def form_preview_url(server:InstanceConf, content:str):
	preview_path = server.preview_path
	domain_name = server.domainName
	return f"http://{domain_name}/{preview_path}/{content}/index.m3u8"

@app.route("/add_media_server", methods=["POST"])
def add_media_server():
	print("Processing add media server request.")

	args = url_decode(request.get_data().decode())
	content_name = args.get("name")
	instance_ip = request.remote_addr
	print(f"{content_name} at instance ip: {instance_ip}")

	(creator, quality) = split_name_qual(content_name) 
	if creator is None or quality is None: 
		return "Name and quality in wrong format ...", status.HTTP_500_INTERNAL_SERVER_ERROR
	
	print(f"Streamer: {creator} qual: {quality} at: {instance_ip}")
	print("Quality will be ignored, abr is used.")

	(region, instance) = filter_region_with_ip(instance_ip)
	if region is None:
		print(f"This instance is not the part of cdn: {instance_ip}")
		return "Failed to match region.", status.HTTP_404_NOT_FOUND

	add_request = MediaServerRequest(content_name=creator,
						quality=STREAM_QUALITY,
						media_server_ip=instance_ip,
						region=region, 
						media_url=form_media_url(instance, creator))
	
	# req_data = encode(add_request, unpicklable=False)
	try:
		print("Posting add_media_server towars registry.")
		url = f"http://{STREAM_REGISTRY_ADDR}/{ADD_MEDIA_SERVER_PATH}"
		# add_res = post(url=url, json=req_data)
		add_res = post(url=url, json=add_request.__dict__)

		if add_res is None:
			raise Exception("Add media server response is None.")
		
		if add_res.status_code != status.HTTP_200_OK:
			raise Exception(f"Add media server response coed: {add_res.status_code}")

	except Exception as e:
		print("Request toward registry failed.")
		print(e)
		return "Failure.", status.HTTP_500_INTERNAL_SERVER_ERROR
	
	return "Added.", status.HTTP_200_OK

def split_name_qual(value: str):
	# Ah ... yes ... regex ... lovely 
	# pattern = f"(.+)_({QUAL_HD}|{QUAL_SD}|{QUAL_SUBSD})$"
	pattern = f"(.+)_({match_quality()})$"
	res = re.search(pattern, value)

	if res is None:
		print("Failed to split name_quality.")
		print(f"Tried to split: {value} with: {pattern}")

		return (None, None)
	
	return (res[1], res[2])

def match_quality():
	return "|".join([ f"{q}" for q in QUALITIES ])

@app.route("/add_preview_server", methods=["POST"])
def add_preview_server():
	print("Processing add preview server.")

	args = url_decode(request.get_data().decode())
	content_name = args.get("name")
	instance_ip = request.remote_addr
	print(f"{content_name} at instance ip: {instance_ip}")

	(region, instance) = filter_region_with_ip(instance_ip)
	if region is None:
		print(f"This instance is not the part of cdn: {instance_ip}")
		return "Failed to match region.", status.HTTP_404_NOT_FOUND

	# check bellow

	add_request = MediaServerRequest(content_name=content_name,
						quality=PREVIEW_QUALITY,
						media_server_ip=instance_ip,
						region=region, 
						media_url=form_preview_url(instance, content_name))
	
	print(f"Posting data: {encode(add_request, unpicklable=False, indent=4)}")
	try:
		print("Posting add_media_server (preview) towars registry.")
		url = f"http://{STREAM_REGISTRY_ADDR}/{ADD_MEDIA_SERVER_PATH}"
		# add_res = post(url=url, json=req_data)
		add_res = post(url=url, json=add_request.__dict__)

		if add_res is None:
			raise Exception("Add media server response is None.")
		
		if add_res.status_code != status.HTTP_200_OK:
			raise Exception(f"Add media server response coed: {add_res.status_code}")

	except Exception as e:
		print("Request toward registry failed.")
		print(e)
		return "Failure.", status.HTTP_500_INTERNAL_SERVER_ERROR

	return "Added.", status.HTTP_200_OK

@app.route("/remove_preview_server", methods=["POST"])
def remove_preview_server():
	print("Not implemented, will return 200.")
	return "Not implemented.", status.HTTP_200_OK

@app.route("/remove_media_server", methods=["POST"])
def remove_media_server():
	print("Processing remove media server request.")

	args = url_decode(request.get_data().decode())
	content_name = args.get("name")
	instance_ip = request.remote_addr
	# instance_ip = args.get("addr")
	# print(f"Instance ip from args.get: {instance_ip}")

	(creator, quality) = split_name_qual(content_name) 
	if creator is None or quality is None: 
		return "Name and quality in wrong format.", status.HTTP_500_INTERNAL_SERVER_ERROR

	(region, instance) = filter_region_with_ip(instance_ip)
	if region is None: 
		print("This instance is not the part of cdn.")
		return "Failed to match region.", status.HTTP_404_NOT_FOUND

	req_data = MediaServerRequest(content_name=creator,
						quality=quality,
						media_server_ip=instance_ip,
						region=region,
						media_url=form_media_url(instance, content_name))
	
	add_res = post(url=f"http://{STREAM_REGISTRY_ADDR}/{REMOVE_MEDIA_SERVER_PATH}", json=req_data.__dict__)
	
	if add_res is None or add_res.status_code != status.HTTP_200_OK:
		print("Failed to remove media server.")
		return "Failure. ", status.HTTP_500_INTERNAL_SERVER_ERROR
	
	return "Success.", status.HTTP_200_OK

def form_hls_path(inst: InstanceConf):
	return f"http://{inst.ip}:{inst.hls_port}/{inst.hls_path}"

# Hc is not even active ... ? 

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

	app.run(host="0.0.0.0", port='80')
