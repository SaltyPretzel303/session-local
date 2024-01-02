#!/usr/bin/python 

import ffmpeg
import pickle
from requests import post, get,  Response
from requests import Session
from jsonpickle import encode, decode

# Register user to be sure it exists, authenticate with those creds, 
# request stream key and publish stream to ingest-loadbalancer.

CONTENT_PATH = '/home/nemanja/Videos/clock.mp4'
INGEST_URL = 'rtmp://localhost:9000/ingest' 

USERNAME = "streamer"
EMAIL = "some_streamer@session.com"
PASSWORD = "strong_password"

AUTH_ROUTE = "http://localhost:8003/authenticate"
REGISTER_ROUTE = "http://localhost:8003/register"
GETKEY_ROUTE = "http://localhost:8003/get_key"

SESSION_PATH = "./publisher_session"
PLAIN_COOKIE_PAT = "./publisher_cookie"

def authenticate(username: str, email: str, password:str ):

	register_data = {
		"username": username,
		"password": password,
		"email": email
	}

	print("Trying to register ... ")

	reg_response : Response = post(url=REGISTER_ROUTE, json=register_data) 
		
	if reg_response.status_code !=  200:
		print(f"Register failed and returned {reg_response.status_code}")
		return None

	print("Register successfull ... ")

	print("Trying read cookie ... ")
	s = Session()
	try:
		cookie_file = open(SESSION_PATH, "rb") 
		if not cookie_file.read():
			print("Session file empty ... ")
		else:
			cookie_file.seek(0)
			s.cookies.update(pickle.load(cookie_file))
			cookie_file.close()
			print("Cookie read ... ")

	except IOError as err:
		print("Failed to read cookie ... ")
		 
	auth_data = {
		"email": register_data["email"],
		"password": register_data["password"]
	}

	print("Trying to authenticate ... ")

	auth_response : Response = s.post(url=AUTH_ROUTE, json=auth_data)

	print("Auth response ... ")
	print(auth_response.json())

	if auth_response.status_code != 200:
		return None
	
	try:
		cookie_file = open(SESSION_PATH, "wb") 
		pickle.dump(auth_response.cookies, cookie_file)
		cookie_file.close()

		plain_cookie = open(PLAIN_COOKIE_PAT,"w")
		plain_cookie.write(auth_response.cookies.get("session"))
		plain_cookie.close()

	except IOError as err:
		print("Failed to write cookie ... ")
		print(err)

	return auth_response.cookies.get("session")


def request_key():
	s = Session()
	try:
		cookie_file = open(SESSION_PATH, "rb") 
		if not cookie_file.read():
			print("Cookie file empty ... ")
		else:
			cookie_file.seek(0)
			s.cookies.update(pickle.load(cookie_file))
			cookie_file.close()

	except IOError as err:
		print("Failed to read cookie ... ")
		return None

	key_res = s.get(url=GETKEY_ROUTE)

	if key_res.status_code != 200:
		print("Failed to obtain stream key ... ")
		return None
	
	return key_res.text

def publish_stream(video_path, ingest_path, stream_name):

	# pix_fmt='yuv420p',
	# preset='veryfast',
	# r='20',
	# g='50',
	# video_bitrate='1.4M',
	# maxrate='2M',
	# bufsize='2M',

	cmd = ffmpeg\
		.input(video_path, re=None)\
		.output(
			f"{ingest_path}/{stream_name}",
			format='flv',
			flvflags="no_duration_filesize",
			loglevel="warning",
			vcodec="libx264",
			acodec="aac",
			g=60
			# codec="copy",  # use same codecs of the original video
		)\
		.run_async(pipe_stdin=True)
	
	return cmd  # I guess this is what I want to return ... ?


if __name__ == "__main__":

	session_id = authenticate(USERNAME, EMAIL, PASSWORD)	
	if session_id is None: 
		print("Failed to register or authenticate ... ")
		exit(1)

	stream_key = request_key()

	if stream_key is None:
		print("Failed to obtain stream key ... ")
		exit(2)

	print(f"publishing : {CONTENT_PATH} to: {INGEST_URL}/{stream_key}")
	process = publish_stream(CONTENT_PATH, INGEST_URL, stream_key)

	input("Press Enter to stop publisher ...")
	process.terminate()
	process.wait()
