import json
from jsonpickle import encode

from instance_conf import InstanceConf

class AppConfig:

	instance = {
		"eu": [
			InstanceConf(ip="localhost",
				hls_port=10000,
				hc_port=10000,
				hls_path="live",
				hc_path="health_check")
		],
		"na": [
			InstanceConf(ip="localhost",
				hls_port=10001,
				hc_port=10000,
				hls_path="live",
				hc_path="health_check")
		],
		"as": [
			InstanceConf(ip="localhost",
				hls_port=10002,
				hc_port=10000,
				hls_path="live",
				hc_path="health_check")
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
		AppConfig.instance = {}
		parsed = json.loads(config)
		for region in parsed:
			AppConfig.instance[region] = [InstanceConf(**c) for c in parsed[region]]

		print(encode(AppConfig.instance, unpicklable=False, indent=4))
			
