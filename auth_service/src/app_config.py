import json
import os

class AppConfig:

    INSTANCE = None

    CONFIG_PATH = "auth_service/src/app_config.json"
    STAGE_ENV_VAR = "AUTH_STAGE"
    DEV_STAGE = "dev"
    PROD_STAGE = "prod"

    @staticmethod
    def get_instance():
        if AppConfig.INSTANCE == None:
            AppConfig.INSTANCE = AppConfig.load_config()

        return AppConfig.INSTANCE

    @staticmethod
    def load_config():
        file = open(AppConfig.CONFIG_PATH, "r")

        raw_content = file.read()
        json_content = json.loads(raw_content)

        stage = AppConfig.resolve_stage()
        print(f"Config stage resolved to: {stage}")

        if stage == AppConfig.PROD_STAGE:
            return json_content[AppConfig.PROD_STAGE]
        else:
            return json_content[AppConfig.DEV_STAGE]

    @staticmethod
    def resolve_stage() -> str:
        if AppConfig.STAGE_ENV_VAR in os.environ:
            return os.environ[AppConfig.STAGE_ENV_VAR]

        else:
            return AppConfig.DEV_STAGE
