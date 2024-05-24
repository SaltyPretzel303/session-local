from dataclasses import dataclass
import os
from typing import Callable
from datetime import timedelta

@dataclass 
class Category: 
	name: str
	displayName: str
	low_icon_path: str
	high_icon_path: str

@dataclass
class Config:
	db_url: str
	match_key_url: Callable[[str], str]
	is_authenticated_url: str
	tnail_path: Callable[[str], str]
	unavailable_path: str
	match_region_url: Callable[[str], str]
	followingUrl: str
	viewer_longevity :timedelta
	categories: list[Category]

DOMAIN_NAME='session.com'

class AppConfig:

	INSTANCE: Config = None

	DEV_INSTANCE = Config(
		db_url="mongodb://registry_user:registry_password@localhost:27017/streams",
		match_key_url=lambda key: f"http://localhost:8100/match_key/{key}",
		is_authenticated_url="http://localhost:8100/is_authenticated",
		tnail_path=lambda streamer: f"./app/tnails/{streamer}.jpeg",
		unavailable_path="tnails/unavailable.png",
		match_region_url=lambda region: f"http://localhost:8004/match_region/{region}",
		followingUrl="http://localhost:8100/get_following",
		# viewer_longevity=timedelta(minutes=1),
		viewer_longevity=timedelta(seconds=20),
		categories = [
			Category(name='chatting',
				displayName="Chatting",
				low_icon_path='/app/categories/chatting_icon.png',
				high_icon_path='/app/categories/chatting_icon.png'
			),
			Category(name='gaming',
				displayName="Gaming",
				low_icon_path='/app/categories/gaming_icon.png',
				high_icon_path='/app/categories/gaming_icon.png'
			),
			Category(name='music',
				displayName="Music",
				low_icon_path='/app/categories/music_icon.png',
				high_icon_path='/app/categories/music_icon.png'
			),
			Category(name='art',
				displayName="Art",
				low_icon_path='/app/categories/art_icon.png',
				high_icon_path='/app/categories/art_icon.png'
			),
			Category(name='sport',
				displayName="Sport",
				low_icon_path='/app/categories/sport_icon.png',
				high_icon_path='/app/categories/sport_icon.png'
			),
			Category(name='science',
				displayName="Science",
				low_icon_path='/app/categories/science_icon.png',
				high_icon_path='/app/categories/science_icon.png'
			)
		]
				
	)

	PROD_INSTANCE = Config(
		db_url=f"mongodb://registry_user:registry_password@registry-db.{DOMAIN_NAME}:27017/streams",
		match_key_url=lambda key: f"http://tokens-api.{DOMAIN_NAME}/match_key/{key}",
		is_authenticated_url=f"http://tokens-api.{DOMAIN_NAME}/is_authenticated",
		tnail_path=lambda streamer: f"/app/tnails/{streamer}.jpg",
		unavailable_path="tnails/unavailable.png",
		match_region_url=lambda region: f"http://cdn-manager.{DOMAIN_NAME}/match_region/{region}",
		followingUrl=f"http://tokens.api.{DOMAIN_NAME}/get_following",
		# viewer_longevity=timedelta(minutes=1)
		viewer_longevity=timedelta(seconds=20),
		categories=[
			Category(name='chatting',
				displayName="Chatting",
				low_icon_path='/app/categories/chatting_icon.png',
				high_icon_path='/app/categories/chatting_icon.png'
			),
			Category(name='gaming',
				displayName="Gaming",
				low_icon_path='/app/categories/gaming_icon.png',
				high_icon_path='/app/categories/gaming_icon.png'
			),
			Category(name='music',
				displayName="Music",
				low_icon_path='/app/categories/music_icon.png',
				high_icon_path='/app/categories/music_icon.png'
			),
			Category(name='art',
				displayName="Art",
				low_icon_path='/app/categories/art_icon.png',
				high_icon_path='/app/categories/art_icon.png'
			),
			Category(name='sport',
				displayName="Sport",
				low_icon_path='/app/categories/sport_icon.png',
				high_icon_path='/app/categories/sport_icon.png'
			),
			Category(name='science',
				displayName="Science",
				low_icon_path='/app/categories/science_icon.png',
				high_icon_path='/app/categories/science_icon.png'
			)
		]
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
