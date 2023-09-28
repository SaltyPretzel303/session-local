import json
import os


class AppConfig:

    # Required instead of just app_config.json because the app is gonna be run
    # from the parent dir ...
    CONFIG_PATH = "client_gateway/app_config.json"

    STAGE_ENV_VAR = "GATEWAY_STAGE"
    DEV_STAGE = "dev"
    PROD_STAGE = "prod"

    INSTANCE = None

    @staticmethod
    def get_instance():
        if AppConfig.INSTANCE == None:
            AppConfig.INSTANCE = AppConfig.load_config()

        return AppConfig.INSTANCE

    @staticmethod
    def load_config():
        file = open(AppConfig.CONFIG_PATH, "r")
        raw_content = file.read()
        # print(f"config: \n{raw_content}")
        json_content = json.loads(raw_content)

        stage = AppConfig.reslove_stage()
        print(f"Config stage resolved to: {stage}")

        if stage == AppConfig.PROD_STAGE:
            return json_content[AppConfig.PROD_STAGE]
        else:
            return json_content[AppConfig.DEV_STAGE]

    @staticmethod
    def reslove_stage() -> str:
        if AppConfig.STAGE_ENV_VAR in os.environ:
            return os.environ[AppConfig.STAGE_ENV_VAR]

        else:
            return AppConfig.DEV_STAGE
