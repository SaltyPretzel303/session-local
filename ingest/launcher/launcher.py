import os
from subprocess import check_output
import sys
import signal
# from subprocess import check_output
from jsonpickle import decode, dumps
from requests import get, post, Response
from threading import Event

CONFIG = {
	"start_server_cmd": "nginx &",
	"stop_server_cmd":"nginx -s stop", 
	"reset_policy": False,
	"initial_interval": 5,
	"initial_retries": 5,
	"check_interval": 20,
	"hc_port":8080,
	"hc_path":"health_check",
	"registration_path": "http://session-ingest-manager:8001/register",
	"unregistration_path": "http://session-ingest-manager:8001/unregister",
	"ip": "session-ingest",
	"port": 9090,
	"path": "ingest",
	"max_streams": 2
}

def stop_handler(signo, _frame):
	if quit_event is not None:
		quit_event.set()

	print(f"Handling signal: {signal.Signals(signo).name}")

	stop_server()

	unregister_ingest()

	print(f"Signal {signal.Signals(signo).name} handled ...")

	exit(0)

def stop_server():
	os.system(CONFIG['stop_server_cmd'])

	# nginx_pids = check_output(["pidof","nginx"])\
	# 	.decode()\
	# 	.strip("\n")\
	# 	.split(" ")

	# print(f"NGINX pids: {nginx_pids}")

	# if nginx_pids is not None or len(nginx_pids) !=0:
	# 	for pid in nginx_pids:
	# 		print(f"\tkilling: {pid}")
	# 		os.system(f"kill {pid}")

def form_hc_url():
	return f'http://{CONFIG["ip"]}:{CONFIG["hc_port"]}/{CONFIG["hc_path"]}'

def form_register_request():
	return {
		"ip" : CONFIG["ip"],
		"port": CONFIG["port"],
		"ingest_path": CONFIG["path"],
		"health_check_path": form_hc_url(),
		"streams_cnt": 0,
		"max_streams": CONFIG["max_streams"]
	}

def form_id():
	return f'{CONFIG["ip"]}:{CONFIG["port"]}'

def register_ingest():
	register_request = form_register_request()
	try:
		reg_res = post(url=CONFIG["registration_path"], json=register_request)

		if reg_res.status_code == 200:
			return True

		if reg_res.status_code != 200:
			raise Exception("Failed to register ... ")
		
	except Exception as e: 
		print(f"Registration failed: {e}")
		return False

def form_unreg_url():
	return f'{CONFIG["unregistration_path"]}/{form_id()}'

def unregister_ingest():
	unreg_url = form_unreg_url()
	try: 
		unreg_res = get(url=unreg_url)

		if unreg_res.status_code != 200:
			raise Exception("Unregistration unsuccessfull ... ")
		
		return True
	except:
		print("Failed to unregister ingest ... ")

		return False


def launch( quit_event):

	server_running = False
	initial_start = True

	while (CONFIG["reset_policy"] or initial_start) and not server_running and \
		not quit_event.is_set():

		initial_start = False

		print("Launching server ...")
		os.system(CONFIG["start_server_cmd"])

		retry_count = CONFIG["initial_retries"]

		while not server_running and retry_count>=0 and not quit_event.is_set():
			print("Checking availability ... ")
			try:
				print(f"hc_url: {form_hc_url()}")
				resp:Response = get(form_hc_url())

				if resp.status_code == 200:
					server_running = True
					print("Server available ... ")

			except: 
				print("Server unavailable ... ")
				quit_event.wait(CONFIG["initial_interval"])
				retry_count -= 1

		if server_running and not quit_event.is_set():
			registration_complete = register_ingest()

			if not registration_complete:
				print("Failed to register ingest ... ")
				stop_server()
				return 
			else:
				print("Ingest registered ... ")

		while server_running and not quit_event.is_set():
			print("Health check ... ")
			try:
				resp = get(form_hc_url())

				if resp.status_code != 200:
					print(f"Health check returned status code: {resp.status_code} ")
					raise Exception("Server unavailable ...")
				else:
					print("Server healthy ... ")
				
				quit_event.wait(CONFIG["check_interval"])
			except Exception as e:
				print("Healthckeck failed ... ")
				print(f"Reason: {e}")

				server_running = False

				unregister_complete = unregister_ingest()
				if not unregister_complete:
					print("Failed to unregister ingest ... ")
				else:
					print("Ingest unregistered ... ")


if __name__ == "__main__":

	signal.signal(signal.SIGINT, stop_handler)
	signal.signal(signal.SIGTERM, stop_handler) 

	quit_event = Event()

	if len(sys.argv) == 2:
		try:
			partial_conf = decode(sys.argv[1])
			for key in partial_conf:
				if key in CONFIG:
					CONFIG[key] = partial_conf[key]
				else:
					print(f"Passed conf key is not valid: {key}={partial_conf[key]}")

		except:
			print("Failed to parse provided configuration ... ")
			print(sys.argv[1])

	print("Active config: ")
	print(dumps(CONFIG, unpicklable=False, indent=4 ))

	launch(quit_event)

	print("Leaving launcher ... ")

			