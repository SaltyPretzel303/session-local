#!/usr/bin/python 

from argparse import ArgumentParser
from typing import Callable
from viewer import watch
import signal
from deploy_config import DeployConfig

DESCRIPTION = "Will deploy specific amount of parameterized viewers."
DOCKER_IMAGE = 'session/viewer'

def setup_argument_parser():
	parser = ArgumentParser(DESCRIPTION)

	parser.add_argument("--farms", action='store', default=3)
	parser.add_argument("--per_farm", action='store', default=1)
	parser.add_argument("--local", action='store_const', const=True, default=False)
	parser.add_argument("--show", action='store_const', const=True, default=False)

	return parser.parse_args()


def get_username(base, ind):
	return f"{base}_{ind}"

def get_email(base:str, ind):
	parts = base.split("@")
	return f"{parts[0]}_inst_{ind}@{parts[1]}"

def get_stream(streams, ind):
	return streams[ind%len(streams)]

def local_deployment(args, streams):

	instance_cnt = int(args.farms) * int(args.per_farm)
	config = DeployConfig.local()

	procs = []

	for i in range(0,instance_cnt):
		stream = get_stream(streams, i)
		proc = watch(get_username(args.username, i), 
			   get_email(args.email, i), 
			   args.password,
			   config.remove_url,
			   config.reg_url,
			   config.auth_url,
			   config.registry_url,
			   stream['creator'], 
			   'subsd',
			   400,
			   300, 
			   1, 
			   args.show)
		
		procs.append(proc)
	
	def stop_method():
		if procs is None: 
			print("Local stop method found no processes to stop.")
			return 
		
		for p in procs:
			p.terminate()

	return stop_method


def docker_deployment():

	

	def stop_method():

		return None

	return stop_method()


if __name__ == '__main__':
	args = setup_argument_parser()

	deploy_method = local_deployment if args.local else docker_deployment

	stop_method = deploy_method(args)

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