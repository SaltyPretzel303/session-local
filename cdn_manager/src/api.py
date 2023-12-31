from sys import argv
from flask import Flask
from flask_restful import Api
from flask_api import  status
from requests import get

from app_config import AppConfig
from instance_conf import InstanceConf
from jsonpickle import encode


app = Flask(__name__)
api = Api(app)

@app.route("/match_region/<region>", methods=["GET"])
def match_region(region:str):
	config = AppConfig.instance

	if region not in config:
		return "Region not available ... ", status.HTTP_404_NOT_FOUND
	
	if is_available(config[region][0]):
		return form_hls_path(config[region][0]), status.HTTP_200_OK
	else:
		print(f"Region's ({region}) main instance is not available ... ")

		alt_instance = next(filter(is_available, config[region][1:]), None)

		if alt_instance is not None:
			return form_hls_path(alt_instance), status.HTTP_200_OK
		else:
			return "Region not available ... ", status.HTTP_404_NOT_FOUND

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
	

if __name__ == '__main__':

	print(argv)
	if len(argv) > 1:
		print("External cdn configuration passed: ")
		print(argv[1])

		AppConfig.load_config(argv[1])

	app.run(host="0.0.0.0", port='8004')
