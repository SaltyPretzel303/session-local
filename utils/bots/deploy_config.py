from dataclasses import dataclass

# Will be used in docker deployment as well ... 
LOCAL_VIDEO_PATH = '/home/nemanja/Videos/clock.mp4'
LOCAL_VIDEO_PATH = "/home/nemanja/workspace/session-local/sample.mp4"

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
					remove_url='http://session.com/remove',
					key_route='http://session.com/auth/get_key',
					source_file=LOCAL_VIDEO_PATH,
					ingest_url='rtmp://session.com:9000/ingest',
					update_url='http://session.com/stream/update',
					registry_url='http://session.com/stream/stream_info')
					

	def docker():
		auth_server = "tokens-api.session.com"
		ingest_server = "ingest-proxy.session.com"
		registry_server = 'stream-registry.session.com'

		domain = 'session.com'
		return DeployConfig(reg_url=f'http://{domain}/auth/signup',
					  auth_url=f'http://{domain}/auth/signin',
					  remove_url=f"http://{domain}/remove",
					  key_route=f'http://{domain}/auth/get_key',
					  source_file='/sample.mp4',
					  ingest_url=f'rtmp://{ingest_server}:9000/ingest',
					  update_url=f'http://{domain}/stream/update',
					  registry_url=f'http://{domain}/stream/stream_info')
