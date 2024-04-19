#!/usr/bin/python 

import argparse
import docker
from streamer import stream 
from deploy_config import DeployConfig, LOCAL_VIDEO_PATH

DESCRIPTION = "Will deploy specific amount of parameterized streamers."
DOCKER_IMAGE = "session/streamer"

COUNT_ARG = 'count'
LOCAL_ARG = 'local'

CATEGORIES = ['chatting', 'gaming', 'music', 'work']
STREAMER_BASE_NAME = 'streamer'
STREAMER_BASE_EMAIL = 'stream_mail'
PWD_BASE = 'some_long_pwd'


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
	return f"{get_name(index)}.session.com"

def get_title(index):
	return f"Generic but not default title for stream: {index}"

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
			--title '{get_title(index)}' \
			--category {get_category(index)} \
			--update_on {config.update_url}"

def docker_deployment(count: int):
	dckr = docker.from_env()
	ids = []

	config = DeployConfig.docker()

	for index in range(0, count):
		volumes = {
			f"{LOCAL_VIDEO_PATH}": {
				"bind": config.source_file,
				"mode": "ro"
			}
		}

		try:
			entry = get_container_entrypoint(index)
			container_name = get_container_name(index)
			container = dckr.containers.run(image=DOCKER_IMAGE,
									detach=True, 
									network='session-net',
									auto_remove=True,
									name=container_name,
									# labels=DOCKER_STREAMER_LABEL,
									# mounts=[video_mount],
									volumes=volumes,
									entrypoint=entry)
		except Exception as e:
			print("Error while starting container: ")
			print(e)
			return None
		
		streamer = dckr.containers.get(container.id)
		if not streamer: 
			print(f"Failed to start streamer: {container_name}")
		else:
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
