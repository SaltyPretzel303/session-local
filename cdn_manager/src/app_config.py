import json
from jsonpickle import encode

from instance_conf import InstanceConf

DOMAIN_NAME = 'session.com'

STREAM_REGISTRY_ADDR = f'stream-registry.{DOMAIN_NAME}'
ADD_MEDIA_SERVER_PATH = 'add_media_server'
REMOVE_MEDIA_SERVER_PATH = 'remove_media_server'

class AppConfig:

	instance = {
		# "eu": [
		# 	InstanceConf(ip="localhost",
		# 		domainName=f"cdn-0.{DOMAIN_NAME}",
		# 		hls_port=80,
		# 		hc_port=10000,
		# 		hls_path="live",
		# 		hc_path="health_check",
		# 		preview_path="preview")
		# ],
		# "na": [
		# 	InstanceConf(ip="localhost",
		# 		domainName=f"cdn-1.{DOMAIN_NAME}",
		# 		hls_port=80,
		# 		hc_port=10000,
		# 		hls_path="live",
		# 		hc_path="health_check",
		# 		preview_path="preview")
		# ],
		# "as": [
		# 	InstanceConf(ip="localhost",
		# 		domainName=f"cdn-2.{DOMAIN_NAME}",
		# 		hls_port=80,
		# 		hc_port=10000,
		# 		hls_path="live",
		# 		hc_path="health_check",
		# 		preview_path="preview")
		# ]
	}

	# CONFIG_PATH = "cdn_manager/src/app_config.json"
	# STAGE_ENV_VAR = "CDN_STAGE"
	# DEV_STAGE = "dev"
	# PROD_STAGE = "prod"

	@staticmethod
	def get_instance():
		return AppConfig.instance

	@staticmethod
	def load_config(config: str):
		# AppConfig.instance = {}
  
		# Next code will just add fields to the existing configuration, thus
		# removing the need to pass irrelevant (to cdn deploy script) fields
		# from the deploy script.
		# ^ handy if configuration actually contains fields irrelevant for the
		# cdn deployment script.
		parsed = json.loads(config)
		for region in parsed:
			AppConfig.instance[region] = [InstanceConf(**c) for c in parsed[region]]

		print(encode(AppConfig.instance, unpicklable=False, indent=4))
			
	@staticmethod
	def add_server(region:str, new_conf: InstanceConf):
		if region in AppConfig.instance and \
			next(filter(lambda c: c.ip==new_conf.ip, AppConfig.instance[region]), None):
			print("This instance is already registered.")
			return
		
		if region not in AppConfig.instance:
			AppConfig.instance[region] = []
			
		AppConfig.instance[region].append(new_conf)