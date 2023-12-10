#!/usr/bin/python 

from threading import Event
import docker
import signal

RUNNING = "running"
CREATED = "created"
STOPPED = "exited"

POLL_INTERVAL = 1

api = docker.APIClient()

quit_event = Event()
def quit_handler(signo, _frame):
	print(f"Handling: {signal.Signals(signo).name}")
	quit_event.set()
	exit(0)

signal.signal(signal.SIGINT, quit_handler)
signal.signal(signal.SIGTERM, quit_handler)

def get_state(id: str):
	return api.containers(filters={"id":id}, all=True)[0]['State']

for cdn_cont in api.containers(filters={"label": "cdn_instance"}, all=True):
	id = cdn_cont['Id']
	name = cdn_cont['Names'][0]
	state = cdn_cont['State']
	
	if state == RUNNING:
		print(f"Stopping: {id}")
		api.stop(id)

		while not quit_event.is_set() and get_state(id) == RUNNING:
			print(f"state: {get_state(id)}")
			quit_event.wait(POLL_INTERVAL)

	print(f"Removing:  {name}")
	api.remove_container(id)

for manager_cont in api.containers(filters={"label": "cdn_manager"}, all=True):
	id = manager_cont['Id']
	name = manager_cont['Names'][0]
	state = manager_cont['State']

	if state == RUNNING:
		print(f"Stopping: {id}")
		api.stop(id)

		while not quit_event.is_set() and get_state(id) == RUNNING:
			quit_event.wait(POLL_INTERVAL)

	print(f"Removing: {name} ")
	api.remove_container(id)

