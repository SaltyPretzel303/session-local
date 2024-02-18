#!/usr/bin/python

import pickle
import sys
import subprocess
from ffpyplayer.player import  MediaPlayer 
from requests import post, get, Response, Session

# USERNAME = "viewer"
# EMAIL = "viewer@session.com"
# PASSWORD = "view_password"

USERNAME = "user_1"
EMAIL = "email_1"
PASSWORD = "pwd_1"

REGISTER_URL = "http://localhost:8003/register"
AUTH_URL = "http://localhost:8003/authenticate"

VIEWER_SESSION_PATH = "./viewer_session"
VIEWER_COOKIE_PATH = "./viewer_cookie"

PLAYER_WIDTH = 500
PLAYER_HEIGHT = int(PLAYER_WIDTH*0.56)

DEFAULT_STREAM_NAME = "user0"
# QUALITY_EXT = "hd"
QUALITY_EXT = "subsd"
STREAM_URL = "http://localhost:10000/live/"
# STREAM_URL = "http://localhost/watch/live/"

def authenticate(username, email, password):
	register_data = {
		"username": username, 
		"password": password,
		"email": email
	}

	print(f"Registering: {register_data['username']} ... ")

	reg_response: Response = post(REGISTER_URL, json=register_data)
	
	if reg_response.status_code != 200:
		print("Failed to register ...")
		return None
	
	s = Session()

	print("Reading session file ... ")
	session_file = None
	try:
		session_file = open(VIEWER_SESSION_PATH, "rb")
		if not session_file.read():
			print("Session file empty ... ")
		else:
			session_file.seek(0)
			s.cookies.update(pickle.load(session_file))
			session_file.close()
			
	except Exception as e:
		print("Failed to read session ... ")

		if session_file is not None:
			session_file.close()


	auth_data = {
		"username": register_data["username"],
		"password": register_data["password"],
	}

	print("Doing authentication ... ")

	auth_response: Response = s.post(AUTH_URL, json=auth_data)

	if auth_response.status_code != 200:
		print("Authentication failed ... ")
		return None
	
	try:
		session_file = open(VIEWER_SESSION_PATH, "wb")
		pickle.dump(auth_response.cookies, session_file)
		session_file.close()

		cookie_file = open(VIEWER_COOKIE_PATH, "w")
		cookie_file.write(auth_response.cookies.get("session"))
		cookie_file.close()

	except Exception as e:

		print("Exception in writing session/cookie file ... ")
		print(e)

		if session_file is not None:
			session_file.close()
		
		if cookie_file is not None:
			cookie_file.close()

		return None
	

	return auth_response.cookies.get("session")


if __name__ == "__main__":

	stream_name = DEFAULT_STREAM_NAME

	cookie = authenticate(USERNAME, EMAIL, PASSWORD)

	if cookie is None:
		print("Failed to obtain valid cookie ... ")
		exit(1)

	print(f"Will watch: {stream_name} at {STREAM_URL}")
	full_stream_name = f"{stream_name}_{QUALITY_EXT}"
	full_stream_url = f"{STREAM_URL}{full_stream_name}/index.m3u8"
	cookie_header = f'Cookie: session="{cookie}"'

	subprocess.call(f"ffplay -fflags nobuffer \
					-headers '{cookie_header}' \
					-x {PLAYER_WIDTH} \
					-y {PLAYER_HEIGHT} {full_stream_url}", shell=True)