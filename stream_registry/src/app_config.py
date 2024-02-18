from dataclasses import dataclass
import os

@dataclass
class Config:
	db_address: str
	db_port: int
	db_name: str
	db_user: str
	db_password: str
	streams_info: str
	auth_service_ip: str
	auth_service_port: int
	match_key_path: str
	authenticate_path: str
	tnail_path: str
	tnail_ext: str

class AppConfig:

	INSTANCE: Config = None

	DEV_INSTANCE = Config(
		db_address = "localhost",
		db_port = 27017	,
		db_name =  "streams",
		db_user = "registry_user",
		db_password = "registry_password",
		streams_info = "info",
		auth_service_ip = "localhost",
		auth_service_port =  8003,
		match_key_path = "match_key",
		authenticate_path= "authenticate",
		tnail_path = "/tnails",
		tnail_ext = "jpeg"
	)

	PROD_INSTANCE = Config(
		db_address = "session-registry-db",
		db_port = 27017,
		db_name = "streams",
		db_user = "registry_user",
		db_password = "registry_password",
		streams_info = "info",
		auth_service_ip = "session-auth",
		auth_service_port = 8003,
		match_key_path = "match_key",
		authenticate_path = "authenticate",
		tnail_path = "/tnails",
		tnail_ext = "jpeg"
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
