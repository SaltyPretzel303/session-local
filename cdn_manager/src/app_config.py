import json
from jsonpickle import encode

from instance_conf import InstanceConf

class AppConfig:

	instance = {
		"eu": [
			InstanceConf(ip="localhost",
				domainName="cdn-0.session.com",
				hls_port=80,
				hc_port=10000,
				hls_path="live",
				hc_path="health_check",
				preview_path="preview")
		],
		"na": [
			InstanceConf(ip="localhost",
				domainName="cdn-1.session.com",
				hls_port=80,
				hc_port=10000,
				hls_path="live",
				hc_path="health_check",
				preview_path="preview")
		],
		"as": [
			InstanceConf(ip="localhost",
				domainName="cdn-2.session.com",
				hls_port=80,
				hc_port=10000,
				hls_path="live",
				hc_path="health_check",
				preview_path="preview")
		]
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
			
