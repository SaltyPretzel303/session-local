from dataclasses import dataclass
from config import signin_url, signup_url, remove_user_url, get_key_url
from config import docker_ingest_url, update_stream_url, stream_info_url
from config import DOMAIN_NAME

# Will be used in docker deployment as well.
# Source file in config will just point to the mounted LOCAL_VIDE_PATH inside
# the container.
LOCAL_VIDEO_PATH = '/home/nemanja/Videos/clock.mp4'
LOCAL_VIDEO_PATH = "/home/nemanja/workspace/session-local/sample.mp4"
# LOCAL_VIDEO_PATH = "/home/nemanja/workspace/session-local/fhd.flv"

@dataclass
class DeployConfig:
	signup_url: str
	signin_url: str
	remove_url: str
	key_route: str
	source_file: str
	ingest_url: str
	update_url: str
	stream_info_url: str

	def local():
		return DeployConfig(signup_url=f'http://{DOMAIN_NAME}/auth/signup',
					signin_url=f'http://{DOMAIN_NAME}/auth/signin',
					remove_url=f'http://{DOMAIN_NAME}/user/remove',
					key_route=f'http://{DOMAIN_NAME}/auth/get_key',
					source_file=LOCAL_VIDEO_PATH,
					ingest_url=f'rtmp://{DOMAIN_NAME}:9000/ingest',
					update_url=f'http://{DOMAIN_NAME}/stream/update',
					stream_info_url=f'http://{DOMAIN_NAME}/stream/stream_info')
					

	def docker():
		
		return DeployConfig(signup_url=signup_url,
					signin_url=signin_url,
					remove_url=remove_user_url,
					key_route=get_key_url,
					source_file='/sample.mp4',
	 				# source_file='/fhd.flv',
					ingest_url=docker_ingest_url,
					update_url=update_stream_url,
					stream_info_url=stream_info_url)