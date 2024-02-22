from dataclasses import dataclass
import os
from typing import Callable

@dataclass
class Config:
	db_url: str
	match_key_url: Callable[[str], str]
	authorize_url: Callable[[str],str]
	tnail_path: Callable[[str], str]

class AppConfig:

	INSTANCE: Config = None

	DEV_INSTANCE = Config(
		db_url="mongodb://registry_user:registry_password@localhost:27017/streams",
		match_key_url=lambda key: f"http://localhost:8100/match_key/{key}",
		authorize_url=lambda user: f"http://localhost:8100/verify/{user}",
		tnail_path = lambda tnail: f"/tnails/{tnail}.jpeg",
	)

	PROD_INSTANCE = Config(
		db_url="mongodb://registry_user:registry_password@registry-db.session:27017/streams",
		match_key_url=lambda key: f"http://tokens-api.session:8100/match_key/{key}",
		authorize_url=lambda user: f"http://tokens-api.session:8100/verify/{user}",
		tnail_path=lambda tnail: f"/tnails/{tnail}.jpeg",
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
