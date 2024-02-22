#!/usr/bin/python 

import argparse
from dataclasses import dataclass
import docker
from docker.types import Mount
from streamer import stream 

DESCRIPTION = "Will deploy specific amount of parameterized streamers."

COUNT_ARG = "count"
LOCAL_ARG = 'local'

CATEGORIES = ['chatting', 'gaming', 'music', 'work']
STREAMER_BASE_NAME = 'streamer'
STREAMER_BASE_EMAIL = 'stream_mail'
PWD_BASE = 'some_long_pwd'

LOCAL_VIDEO_PATH = '/home/nemanja/Videos/clock.mp4'
LOCAL_VIDEO_PATH = "/home/nemanja/workspace/session-local/sample.mp4"
DOCKER_VIDEO_PATH = '/sample.mp4'

DOCKER_IMAGE = "session/streamer"
DOCKER_STREAMER_LABEL = 'session_streamer'

COOKIE_BASE_PATH = './cookies'

@dataclass
class DeployConfig:
	reg_url: str
	auth_url: str
	remove_url: str
	key_route: str
	source_file: str
	ingest_url: str
	update_url: str

	def local():
		return DeployConfig(reg_url='http://localhost:8100/auth/signup',
					  auth_url='http://localhost:8100/auth/signin',
					  remove_url='http://localhost:8100/remove',
					  key_route='http://localhost:8100/get_key',
					  source_file=LOCAL_VIDEO_PATH,
					  ingest_url='rtmp://localhost:9000/ingest',
					  update_url='http://localhost:8002/update')

	def docker():
		auth_server = "tokens-api.session"
		ingest_server = "ingest-proxy.session"
		registry_server = 'stream-registry.session'
		return DeployConfig(reg_url=f'http://{auth_server}:8100/auth/signup',
					  auth_url=f'http://{auth_server}:8100/auth/signin',
					  remove_url=f"http://{auth_server}:8100/remove",
					  key_route=f'http://{auth_server}:8100/get_key',
					  source_file=DOCKER_VIDEO_PATH,
					  ingest_url=f'rtmp://{ingest_server}:9000/ingest',
					  update_url=f'http://{registry_server}:8002/update')


def setup_arguments():
	parser = argparse.ArgumentParser(description=DESCRIPTION)

	parser.add_argument(f'--{COUNT_ARG}',
					action='store',
					default=1)
	
	parser.add_argument(f'--{LOCAL_ARG}',
					action='store_const',
					const=True,
					default=False)

	return parser.parse_args()

def get_name(index):
	return f"{STREAMER_BASE_NAME}-{index}"

def get_mail(index):
	return f"{STREAMER_BASE_EMAIL}_{index}@mail.com"

def get_pwd(index):
	return f"{PWD_BASE}_{index}"

def get_cookie_path(index):
	return f"{COOKIE_BASE_PATH}_{get_name(index)}"

def local_deployment(count: int):
	config = DeployConfig.local()

	procs = []

	for index in range(0, count):
		new_proc = stream(username=get_name(index),
				email=get_mail(index),
				password=get_pwd(index),
				reg_route=config.reg_url,
				auth_route=config.auth_url,
				remove_route=config.remove_url,
				# cookie_path=get_cookie_path(index),
				key_url=config.key_route,
				source_file=config.source_file,
				ingest_url=config.ingest_url,
				update_url=config.update_url,
				title=get_title(index),
				category=get_category(index))
		
		if new_proc is None:
			print(f"Failed to start stream for: {get_name(index)}")
		else:
			print(f"Started stream for: {get_name(index)}")
			procs.append(new_proc)

	def close_method():
		if procs is None:
			return
		
		for proc in procs:
			proc.terminate()
			proc.wait()

	return close_method

def get_container_name(index):
	return f"{get_name(index)}.session"

def get_title(index):
	return f"Generic title for stream: {index}"

def get_category(index):
	return CATEGORIES[index % len(CATEGORIES)]

def get_container_entrypoint(index):
	config = DeployConfig.docker()
	return f"python3 -u /streamer.py --name {get_name(index)} \
			--email {get_mail(index)} \
			--pwd {get_pwd(index)} \
			--file {config.source_file} \
			--ingest {config.ingest_url} \
			--auth_on {config.auth_url} \
			--remove_on {config.remove_url} \
			--reg_on {config.reg_url} \
			--get_key_on {config.key_route} \
			--cookie_at {get_cookie_path(index)} \
			--title '{get_title(index)}' \
			--category {get_category(index)} \
			--update_on {config.update_url}"

def docker_deployment(count: int):
	dckr = docker.from_env()
	ids = []

	for index in range(0, count):
		volumes = {
			f"{LOCAL_VIDEO_PATH}": {
				"bind": DOCKER_VIDEO_PATH,
				"mode": "ro"
			}
		}

		try:
			entry = get_container_entrypoint(index)
			container = dckr.containers.run(image=DOCKER_IMAGE,
									detach=True, 
									network='session-net',
									auto_remove=True,
									name=get_container_name(index),
									# labels=DOCKER_STREAMER_LABEL,
									# mounts=[video_mount],
									volumes=volumes,
									entrypoint=entry)
		except Exception as e:
			print("Error while starting container: ")
			print(e)
			return None

		ids.append(container.id)

	print("Streamers deployed.")

	def stop_method():
		if ids is None: 
			return
		
		d = docker.from_env()
		for id in ids:
			try:
				container = d.containers.get(id)
				if container is None:
					raise Exception("Returned container is None")
				
				container.stop()
			except Exception as e:
				print(f"Container: {id} not found.")

	return stop_method


def resolve_deployment(is_local):
	return local_deployment if is_local else docker_deployment


if __name__ == '__main__':
	args = setup_arguments()
	args = vars(args)

	deploy_method = local_deployment if args[LOCAL_ARG] else docker_deployment

	stop_method = deploy_method(int(args[COUNT_ARG]))

	if stop_method is None:
		print("Failed to deploy streams.")
		exit(1)

	print("Streams deployed.")
	input("Press ENTER to stop streams.")

	stop_method()

	print("Streams stopped.")

	print("Exiting.")
	exit(0)
