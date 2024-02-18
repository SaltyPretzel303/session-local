#!/usr/bin/python 

import argparse
from time import sleep
import pickle
from threading import Thread
import ffmpeg # pip install ffmpeg-python NOT JUST FFMPEG !!!

from jsonpickle import encode
from requests import Response, Session, post
import signal 
import sys

DESCRIPTION = "Parameterized streamer."

NAME_ARG = 'name'
MAIL_ARG = 'email'
PASSWORD_ARG = 'pwd'
TITLE_ARG = "title"
CATEGORY_ARG = "category"
SOURCE_FILE_ARG = "file"
INGEST_ARG = "ingest"
AUTH_ROUTE_ARG = "auth_on"
REG_ROUTE_ARG = "reg_on"
GET_KEY_ROUTE_ARG = 'get_key_on'
UPDATE_PATH_ARG = 'update_on'
COOKIE_PATH_ARG = "cookie_at"

def setup_arg_parser():
	
	parser = argparse.ArgumentParser(description=DESCRIPTION)

	parser.add_argument(f'--{NAME_ARG}', 
						action='store', 
						default='user0')

	parser.add_argument(f'--{MAIL_ARG}',
						action='store',
						default='email0')

	parser.add_argument(f'--{PASSWORD_ARG}',
						action='store',
						default='pwd0')

	parser.add_argument(f'--{TITLE_ARG}',
						action='store',
						default='some_stream_title')

	parser.add_argument(f'--{CATEGORY_ARG}',
						action='store',
						default='chatting')

	parser.add_argument(f'--{SOURCE_FILE_ARG}', 
						action='store', 
						default='/home/nemanja/Videos/clock.mp4')

	parser.add_argument(f'--{INGEST_ARG}', 
						action='store', 
						default='rtmp://localhost:9000/ingest')

	parser.add_argument(f'--{AUTH_ROUTE_ARG}', 
						action='store', 
						default='http://localhost:8003/authenticate')

	parser.add_argument(f'--{REG_ROUTE_ARG}', 
						action='store', 
						default='http://localhost:8003/register')

	parser.add_argument(f'--{GET_KEY_ROUTE_ARG}',
						action='store',
						default='http://localhost:8003/get_key')

	parser.add_argument(f'--{UPDATE_PATH_ARG}',
						action='store',
						default='http://localhost:8002/update')

	parser.add_argument(f'--{COOKIE_PATH_ARG}',
						action='store',
						default='./publisher_session')

	return parser.parse_args()

def json_serialize(data):
	return encode(data, unpicklable=False)

def get_reg_data(email, username, password):
	return {
		'email': email,
		'username': username,
		'password': password
	}

def get_auth_data(username, password):
	return {
		'username': username,
		'password': password
	}

# TODO this should be done using supertokens -_-
def authenticate(username: str, 
				email: str, 
				password:str, 
				reg_route:str,
				auth_route: str,
				session_path: str):

	register_data = get_reg_data(email, username, password)

	print("Trying to register with: ")
	print(encode(register_data, indent=4))

	reg_response : Response = post(url=reg_route, json=register_data) 
		
	if reg_response.status_code !=  200:
		print(f"Registration failed with: {reg_response.status_code}")
		return None

	print("Registration successfull.")

	print("Trying to read session cookie.")
	s = Session()
	try:
		cookie_file = open(session_path, "rb") 
		if not cookie_file.read():
			print("Session file empty.")
		else:
			print(f"Session found in: {session_path}")
			cookie_file.seek(0)
			s.cookies.update(pickle.load(cookie_file))
			cookie_file.close()

	except IOError as err:
		print(f"Failed to read cookie: {err}")
		 
	auth_data = get_auth_data(username, password)

	print("Trying to authenticate with: ")
	print(encode(auth_data, indent=4))
	auth_response : Response = s.post(url=auth_route, json=auth_data)

	if auth_response.status_code != 200:
		print("Authentication failed.")
		print(auth_response.json())
		return None

	try:
		print("Writing cookie.")
		cookie_file = open(session_path, "wb") 
		pickle.dump(auth_response.cookies, cookie_file)
		cookie_file.close()

		# plain_cookie = open(PLAIN_COOKIE_PATH, "w")
		# plain_cookie.write(auth_response.cookies.get("session"))
		# plain_cookie.close()

	except IOError as err:
		print(f"Failed to write cookie: {err}")

	return auth_response.cookies.get("session")

def request_key(session_path, get_key_route):

	s = Session()
	try:
		cookie_file = open(session_path, "rb") 
		if not cookie_file.read():
			print("Cookie file empty ... ")
		else:
			print(f"Found session in: {session_path}")
			cookie_file.seek(0)
			s.cookies.update(pickle.load(cookie_file))
			cookie_file.close()

	except IOError as err:
		print(f"Failed to read cookie: {err}")
		return None

	key_res:Response = s.get(url=get_key_route)

	if key_res.status_code != 200:
		print("Failed to obtain stream key: " + key_res.text)
		return None
	
	return key_res.json()

def get_key_from_data(data):
	return data['value']

def title(index):
	return "Generic title: {index}"

def publish_stream(video_path, ingest_path, stream_name):

	return ffmpeg\
		.input(video_path, re=None)\
		.output(
			f"{ingest_path}/{stream_name}",
			format='flv',
			flvflags="no_duration_filesize",
			loglevel="warning",
			vcodec="libx264",
			acodec="aac",
			g=60
		)\
		.run_async(pipe_stdin=True)

def stream(username, 
		   email, 
		   password, 
		   reg_route, 
		   auth_route, 
		   cookie_path, 
		   key_route,
		   source_file,
		   ingest_url):

	cookie = authenticate(username=username, 
					   email=email, 
					   password=password, 
					   reg_route=reg_route, 
					   auth_route=auth_route, 
					   session_path=cookie_path)
	
	if cookie is None: 
		print("Failed to authenticate, aborting.")
		return None

	key_data = request_key(cookie_path, key_route)
	if key_data is None:
		print("Failed to obtain stream key, aborting.")
		return None

	stream_key = get_key_from_data(key_data)
	print(f"Obtained key: {stream_key}")

	print("Starting stream.")
	pub_proc = publish_stream(source_file,ingest_url, stream_key)

	return pub_proc

def get_update_request(title, category, is_public):
	return {
		'title': title, 
		'category': category,
		'is_public': is_public
	}

def update_stream_info(title, category, session_path):

	s = Session()
	try:
		cookie_file = open(session_path, "rb") 
		if not cookie_file.read():
			print("Cookie file empty ... ")
		else:
			print(f"Found session in: {session_path}")
			cookie_file.seek(0)
			s.cookies.update(pickle.load(cookie_file))
			session_id = s.cookies.get("session")
			cookie_file.close()
			print(f"read cookie: {s.cookies}")
			print(f"sessionId: {session_id}")

	except IOError as err:
		print(f"Failed to read cookie: {err}")
		return False

	update_data = get_update_request(args[TITLE_ARG],
								args[CATEGORY_ARG],
								True)

	try:
		# TODO This is hack that will work just on legacy auth service. 
		# Cookie returned from auth service (once streamer is authenticated) 
		# is restricted to auth-service only, stream-registry will discard it
		# and wont even be able to pass it along with auth request inside of 
		# update request handler ... 
		cookies = {'session': session_id}
		update_res = post(url=args[UPDATE_PATH_ARG], json=update_data, cookies=cookies)
		# update_res = s.post(url=args[UPDATE_PATH_ARG], json=update_data)

		if update_res is None: 
			raise Exception("Got None as update result.")
		
		if update_res.status_code != 200:
			raise Exception(f"Stream registry returned: {update_res.status_code}")
	except Exception as e:
		print(f"Failed to update stream info: {e}")
		return False

	return True

def delayed_update(delay, title, category, session_path):
	print(f"Called delayed update, will wait for: {delay}")
	sleep(delay)
	print("Done waiting, will perform update.")

	update_res = update_stream_info(title, category, session_path)
	
	if update_res:
		print("Update successfull.")
	else:
		print("Filed to update stream info.")

if __name__ == '__main__':

	args = setup_arg_parser()
	args = vars(args)

	proc = stream(args[NAME_ARG],
			args[MAIL_ARG],
			args[PASSWORD_ARG],
			args[REG_ROUTE_ARG],
			args[AUTH_ROUTE_ARG],
			args[COOKIE_PATH_ARG],
			args[GET_KEY_ROUTE_ARG],
			args[SOURCE_FILE_ARG],
			args[INGEST_ARG])

	if proc is None:
		print("Failed to stream.")

		print("Exiting.")
		exit(1)

	update_args = (5, args[TITLE_ARG], args[CATEGORY_ARG], args[COOKIE_PATH_ARG])
	update_thread = Thread(target=delayed_update, args=update_args)
	update_thread.start()
	

	def signal_handler(sig, frame):
		print("Processing singal.")

		if sig == signal.SIGINT or sig==signal.SIGTERM:
			print("Signal is sigint or sigterm.")
			if proc is not None:
				print("Terminating streaming processe.")
				proc.terminate()
			else:
				print("Streaming process is None.")
				exit(1)

	print("Adding signal handlers.", flush=True)
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)

	# input("Press ENTER or ctrl+C to stop streaming ...")
	proc.wait()

	print("Stream stopped.")
	print("Exiting.")
	exit(0)

