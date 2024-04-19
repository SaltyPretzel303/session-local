from dataclasses import dataclass

# Will be used in docker deployment as well.
# Source file in config will just point to the mounted LOCAL_VIDE_PATH inside
# the container.
LOCAL_VIDEO_PATH = '/home/nemanja/Videos/clock.mp4'
LOCAL_VIDEO_PATH = "/home/nemanja/workspace/session-local/sample.mp4"
# LOCAL_VIDEO_PATH = "/home/nemanja/workspace/session-local/fhd.flv"

@dataclass
class DeployConfig:
	reg_url: str
	auth_url: str
	remove_url: str
	key_route: str
	source_file: str
	ingest_url: str
	update_url: str
	registry_url: str

	def local():
		return DeployConfig(reg_url='http://session.com/auth/signup',
					auth_url='http://session.com/auth/signin',
					remove_url='http://session.com/user/remove',
					key_route='http://session.com/auth/get_key',
					source_file=LOCAL_VIDEO_PATH,
					ingest_url='rtmp://session.com:9000/ingest',
					update_url='http://session.com/stream/update',
					registry_url='http://session.com/stream/stream_info')
					

	def docker():
		ingest_server = "ingest-proxy.session.com"

		domain = 'session.com'
		return DeployConfig(reg_url=f'http://{domain}/auth/signup',
					auth_url=f'http://{domain}/auth/signin',
					remove_url=f"http://{domain}/user/remove",
					key_route=f'http://{domain}/auth/get_key',
					source_file='/sample.mp4',
	 				# source_file='/fhd.flv',
					ingest_url=f'rtmp://{ingest_server}:9000/ingest',
					update_url=f'http://{domain}/stream/update',
					registry_url=f'http://{domain}/stream/stream_info')
