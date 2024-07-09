#!/usr/bin/python 

import argparse
from time import sleep
from threading import Thread
import ffmpeg # pip install ffmpeg-python NOT JUST FFMPEG !!!

from jsonpickle import encode
from requests import Response, Session, post
import signal 
from tokens_auth import StreamKey, tokens_signin, tokens_signup, tokens_get_key, tokens_remove_user
from config import signin_url, signup_url, remove_user_url, get_key_url, update_stream_url, local_ingest_url


DESCRIPTION = "Parameterized streamer."

NAME_ARG = 'name'
MAIL_ARG = 'email'
PASSWORD_ARG = 'pwd'
KEEP_ARG = 'keep'
TITLE_ARG = "title"
CATEGORY_ARG = "category"
SOURCE_FILE_ARG = "file"
INGEST_ARG = "ingest"
REMOVE_ROUTE_ARG = "remove_on"
AUTH_ROUTE_ARG = "auth_on"
REG_ROUTE_ARG = "reg_on"
GET_KEY_ROUTE_ARG = 'get_key_on'
UPDATE_PATH_ARG = 'update_on'

def setup_arg_parser():
	
	parser = argparse.ArgumentParser(description=DESCRIPTION)

	parser.add_argument(f'--{NAME_ARG}', 
						action='store', 
						default='user0')

	parser.add_argument(f'--{MAIL_ARG}',
						action='store',
						default='email0@mail.com')

	parser.add_argument(f'--{PASSWORD_ARG}',
						action='store',
						default='email0pwd')

	parser.add_argument(f'--{KEEP_ARG}',
					 	action='store_true',
						default=False)

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
						default=local_ingest_url)

	parser.add_argument(f'--{REMOVE_ROUTE_ARG}', 
						action='store', 
						default=remove_user_url)

	parser.add_argument(f'--{AUTH_ROUTE_ARG}', 
						action='store', 
						default=signin_url)

	parser.add_argument(f'--{REG_ROUTE_ARG}', 
						action='store', 
						default=signup_url)

	parser.add_argument(f'--{GET_KEY_ROUTE_ARG}',
						action='store',
						default=get_key_url)

	parser.add_argument(f'--{UPDATE_PATH_ARG}',
						action='store',
						default=update_stream_url)

	return parser.parse_args()

def json_serialize(data):
	return encode(data, unpicklable=False)

def jsonify(obj):
	return encode(obj, unpicklable=False, indent=4)

def publish_stream(session, key_url, video_path, ingest_path):

	print("Will try to obtain stream key.", end=" ")
	key_data: StreamKey = tokens_get_key(session, key_url)
	if key_data is None: 
		print(f"Failed to obtain stream key.")
		return None

	ingest_url = f"{ingest_path}/{key_data.value}"
	print(f"Publishing: {video_path} at {ingest_url}")

	return ffmpeg\
		.input(video_path, re=None, stream_loop=-1)\
		.output(
			ingest_url,
			format='flv',
			flvflags="no_duration_filesize",
			loglevel="warning",
			vcodec="libx264",
			acodec="aac",
			# video_bitrate='100k',
			g=60 # number of frames per key frame 
		)\
		.run_async(pipe_stdin=True)

def authenticate(username, 
				email, 
				password, 
				remove_route, 
				reg_route, 
				auth_route,
				keep=False)->Session: 
	if not keep:
		print(f"Will try to remove user: {username}.", end=" ")
		remove_success = tokens_remove_user(username, remove_route)
		if not remove_success:
			print(f"Failed to remove user: {username}.")
			return None
		print("User successfully removed.")
	else: 
		print("User will not be removed (keep == true).")

	if not keep: 
		print("Will try to signup.", end=" ")
		signup_success = tokens_signup(username, email, password, reg_route)
		if not signup_success:
			print(f"Filed to signup with email: {email}.")
			return None
		print("Successfully signedUp.")
	else: 
		print("User will not be signedIp (keep == true).")

	print("Will try to signin (obtain session).", end=" ")
	session = tokens_signin(email, password, auth_route)
	if session is None: 
		print(f"Failed to singin with: {email}.")
		return None
	print("SignIn successfull (session obtained).")

	return session

def get_update_request(username, title, category, is_public):
	return {
		'username': username,
		'title': title, 
		'category': category,
		'is_public': is_public
	}

def update_stream_info(session, username, update_url, title, category):

	if session is None: 
		print("Doing stream info update without session.")
	
	update_data = get_update_request(username, title, category, True)

	try:
		update_res = session.post(url=update_url, json=update_data)

		if update_res is None: 
			raise Exception("Update result is None.")
		
		if update_res.status_code != 200:
			raise Exception(f"Update stream status code: {update_res.status_code}")
		
	except Exception as e:
		print(f"Failed to update stream info: {e}")
		return False

	return True

def delayed_update(delay, session, update_url, username, title, category):
	print(f"Called delayed update, will wait for: {delay}")
	sleep(delay)
	print("Done waiting, will perform update.")

	update_success = update_stream_info(session, username, update_url, title, category)
	
	if update_success:
		print("Update successfull.")
	else:
		print("Filed to update stream info.")

def stream(username, 
		email, 
		password,
		keep, 
		reg_route,
		auth_route, 
		remove_route, 
		key_url, 
		source_file, 
		ingest_url,
		update_url,
		title, 
		category):

	session = authenticate(username=username,
					email=email,
					password=password,
					remove_route=remove_route,
					reg_route=reg_route,
					auth_route=auth_route, 
					keep=keep)

	if session is None: 
		print("Authentication failed.")
		return None

	publish_proc = publish_stream(session=session,
					key_url=key_url,
					video_path=source_file,
					ingest_path=ingest_url)

	if publish_proc is None:
		print("Failed start publishing.")
		return None

	update_args = (10, session, update_url, username, title, category)
	update_thread = Thread(target=delayed_update, args=update_args)
	update_thread.start()

	return publish_proc

if __name__ == '__main__':

	args = setup_arg_parser()
	args = vars(args)

	proc = stream(username=args[NAME_ARG],
			email=args[MAIL_ARG],
			password=args[PASSWORD_ARG],
			keep=args[KEEP_ARG],
			reg_route=args[REG_ROUTE_ARG],
			auth_route=args[AUTH_ROUTE_ARG],
			remove_route=args[REMOVE_ROUTE_ARG],
			key_url=args[GET_KEY_ROUTE_ARG],
			source_file=args[SOURCE_FILE_ARG],
			ingest_url=args[INGEST_ARG],
			update_url=args[UPDATE_PATH_ARG],
			title=args[TITLE_ARG],
			category=args[CATEGORY_ARG])

	if proc is None: 
		print("Streaming failed, exiting.")
		exit(1)

	def signal_handler(sig, frame):
		print("Processing singal.")

		if sig == signal.SIGINT or sig == signal.SIGTERM:
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

	print("Press ctrl+c to stop streaming")
	proc.wait()

	print("Stream stopped.")
	print("Exiting.")
	exit(0)


