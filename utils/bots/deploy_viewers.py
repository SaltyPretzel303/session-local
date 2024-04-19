#!/usr/bin/python 

from argparse import ArgumentParser
from viewer import watch
import signal
from deploy_config import DeployConfig
import docker

DESCRIPTION = "Will deploy specific amount of parameterized viewers."
DOCKER_IMAGE = 'session/viewer'

# Not used but could be if docker_deployment deploys viewer farms outside the
# session-net network and default docker dns cant resolve cdn domain names. 
HOSTS = [	
			"172.19.0.20	eu-0-cdn.session.com",
			"172.19.0.21	na-0-cdn.session.com",
			"172.19.0.22 	as-0-cdn.session.com",
			"172.19.0.14	session.com"
		]

def setup_argument_parser():
	parser = ArgumentParser(DESCRIPTION)

	parser.add_argument("--farms", action='store', default=3)
	parser.add_argument("--per_farm", action='store', default=1)
	parser.add_argument("--local", action='store_const', const=True, default=False)
	parser.add_argument("--show", action='store_const', const=True, default=False)

	parser.add_argument("--username", action='store', default='viewer')
	parser.add_argument("--email", action='store', default='viewer@session.com')
	parser.add_argument("--password", action='store', default='viewer_pwd_1')


	return parser.parse_args()

def get_username(base, ind):
	return f"{base}_{ind}"

def get_email(base:str, ind):
	parts = base.split("@")
	return f"{parts[0]}_inst_{ind}@{parts[1]}"

def get_stream(streams, ind):
	return streams[ind%len(streams)]

def local_deployment(args, streams):
	print("Local deployment.")

	instance_cnt = int(args.farms) * int(args.per_farm)
	config = DeployConfig.local()

	procs = []

	for i in range(0, instance_cnt):
		stream = get_stream(streams, i)
		proc_cluster = watch(get_username(args.username, i), 
			   get_email(args.email, i), 
			   args.password,
			   config.remove_url,
			   config.reg_url,
			   config.auth_url,
			   config.registry_url,
			   stream, 
			   400,
			   300, 
			   1, 
			   args.show)
		for proc_id in proc_cluster: 
			procs.append(proc_cluster[proc_id])
	
	def stop_method():
		if procs is None: 
			print("Local stop method found no processes to stop.")
			return 
		
		for p in procs:
			p.terminate()

	return stop_method


def get_farm_name(index):
	return f"view_farm_{index}"

def get_farm_email(base: str, index: int):
	bases = base.split("@")
	return f"{bases[0]}_{index}@{bases[1]}"

def docker_deployment(args, streams):
	print("Docker deployment.")

	doker = docker.from_env()
	ids = []

	for farm_ind in range(0, int(args.farms)):

		entry = f"python3 -u ./viewer.py \
			--username {args.username}_{farm_ind} \
			--email {get_farm_email(args.email, farm_ind)} \
			--stream {get_stream(streams, farm_ind)} \
			--count {args.per_farm}"
		try: 
			container_name = get_farm_name(farm_ind)
			container = doker.containers.run(image=DOCKER_IMAGE, 
									detach=True, 
									network='session-net',
		 							auto_remove=True, 
									name=container_name, 
									entrypoint=entry)
			
		except Exception as e:
			print(f"Failed to start viewer farm: {e}")

		if not doker.containers.get(container.id):
			print(f"Failed to start: {get_farm_name(farm_ind)}")
		else:
			print(f"Farm deployed: {get_farm_name(farm_ind)}")
			ids.append(container.id)
		
	def stop_method():
		print("Stopping docker deployed farms.")

		if len(ids) == 0:
			print("No viewer farms running.")
			return 
		
		doker = docker.from_env()
		for id in ids: 
			print(f"Stopping farm: {id}")
			farm = doker.containers.get(id)

			if farm is None: 
				print(f"Farm: {id} not found.")
			else: 
				farm.stop()


	return stop_method


if __name__ == '__main__':
	args = setup_argument_parser()

	deploy_method = local_deployment if args.local else docker_deployment

	streams = ['streamer-0']

	stop_method = deploy_method(args, streams)

	if stop_method is None: 
		print("Failed to deploy.")
		exit(1)

	def signal_handler(sig, frame):
		print(f"Handling signal: {sig}")
		if stop_method is not None:
			stop_method()

		print("Signal handler, exiting with 0.")
		exit(0)


	signal.signal(signal.SIGTERM, signal_handler)
	signal.signal(signal.SIGINT, signal_handler)

	input("Press enter or ctrl+c to stop viewers ...")

	stop_method()
	
	print("Exiting.")
	exit(0)