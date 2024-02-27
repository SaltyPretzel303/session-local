from dataclasses import dataclass
import os
from typing import Callable

@dataclass
class Config:
	db_url: str
	match_key_url: Callable[[str], str]
	authorize_url: Callable[[str],str]
	tnail_url: Callable[[str], str]
	match_region_url: Callable[[str], str]

class AppConfig:

	INSTANCE: Config = None

	DEV_INSTANCE = Config(
		db_url="mongodb://registry_user:registry_password@localhost:27017/streams",
		match_key_url=lambda key: f"http://localhost:8100/match_key/{key}",
		authorize_url=lambda user: f"http://localhost:8100/verify/{user}",
		tnail_url = lambda tnail: f"/tnails/{tnail}.jpeg",
		match_region_url = lambda region: f"http://localhost:8004/match_region/{region}"
	)

	PROD_INSTANCE = Config(
		db_url="mongodb://registry_user:registry_password@registry-db.session.com:27017/streams",
		match_key_url=lambda key: f"http://tokens-api.session.com/match_key/{key}",
		authorize_url=lambda user: f"http://tokens-api.session.com/verify/{user}",
		tnail_url=lambda tnail: f"/tnails/{tnail}.jpeg",
		match_region_url = lambda region: f"http://cdn-manager.session.com/match_region/{region}"
	)

	# CONFIG_PATH = "stream_registry/src/app_config.json"
	STAGE_ENV_VAR = "REGISTRY_STAGE"
	DEV_STAGE = "dev"
	PROD_STAGE = "prod"

	@staticmethod
	def get_instance() -> Config:
		if AppConfig.INSTANCE is None: 
			AppConfig.INSTANCE = AppConfig.load_config()
		
		return AppConfig.INSTANCE


	@staticmethod
	def load_config() -> Config:
		stage = AppConfig.resolve_stage()
		print(f"Config stage resolved to: {stage}")

		if stage == AppConfig.PROD_STAGE:
			return AppConfig.PROD_INSTANCE
		else: 
			return AppConfig.DEV_INSTANCE

	@staticmethod
	def resolve_stage() -> str:
		if AppConfig.STAGE_ENV_VAR in os.environ:
			return os.environ[AppConfig.STAGE_ENV_VAR]

		else:
			return AppConfig.DEV_STAGE
