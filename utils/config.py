DOMAIN_NAME = 'session.com'

get_key_url = f'http://{DOMAIN_NAME}/auth/get_key'
remove_user_url = f"http://{DOMAIN_NAME}/user/remove"
signup_url = f"http://{DOMAIN_NAME}/auth/signup"
signin_url = f"http://{DOMAIN_NAME}/auth/signin"

local_ingest_url = f"rtmp://{DOMAIN_NAME}:9000/ingest"
docker_ingest_url = f'rtmp://ingest-proxy.{DOMAIN_NAME}/ingest'
update_stream_url = f"http://{DOMAIN_NAME}/stream/update"
stream_info_url = f"http://{DOMAIN_NAME}/stream/stream_info"

ws_chat_url = f'ws://{DOMAIN_NAME}/chat'

# Not used but could be if docker_deployment deploys viewer farms outside the
# session-net network and default docker dns cant resolve cdn domain names. 
CDN_HOSTS = [	
			f"172.19.0.20	eu-0-cdn.{DOMAIN_NAME}",
			f"172.19.0.21	na-0-cdn.{DOMAIN_NAME}",
			f"172.19.0.22 	as-0-cdn.{DOMAIN_NAME}",
			f"172.19.0.14	{DOMAIN_NAME}"
		]