#!/usr/bin/python 

from dataclasses import dataclass
import ffmpeg
import pickle
from requests import post, get,  Response
from requests import Session
from jsonpickle import encode, decode

# Register user to be sure it exists, authenticate with those creds, 
# request stream key and publish stream to ingest-loadbalancer.

CONTENT_PATH = '/home/nemanja/Videos/clock.mp4'
INGEST_URL = 'rtmp://localhost:9000/ingest' 

USERNAME = "user0"
EMAIL = "email0"
PASSWORD = "pwd0"

AUTH_ROUTE = "http://localhost:8003/authenticate"
REGISTER_ROUTE = "http://localhost:8003/register"
GETKEY_ROUTE = "http://localhost:8003/get_key"

SESSION_PATH = "./publisher_session"
PLAIN_COOKIE_PATH = "./publisher_cookie"

UPDATE_INFO_PATH = "http://localhost:8002/update"

def json_serialize(obj):
	return encode(obj, unpicklable=False)

@dataclass
class UpdateRequest:
	title: str
	category: str
	is_public: bool


def authenticate(username: str, email: str, password:str ):

	register_data = {
		"username": username,
		"password": password,
		"email": email
	}

	print("Trying to register ... ")
	print(encode(register_data, indent=4))

	reg_response : Response = post(url=REGISTER_ROUTE, json=register_data) 
		
	if reg_response.status_code !=  200:
		print(f"Register failed and returned {reg_response.status_code}")
		return None

	print("Register successfull ... ")

	print("Trying to read cookie ... ")
	s = Session()
	try:
		cookie_file = open(SESSION_PATH, "rb") 
		if not cookie_file.read():
			print("Session file empty ... ")
		else:
			cookie_file.seek(0)
			s.cookies.update(pickle.load(cookie_file))
			cookie_file.close()
			print(f"Cookie read: {s.cookies}")

	except IOError as err:
		print("Failed to read cookie ... ")
		 
	auth_data = {
		"username": register_data["username"],
		"password": register_data["password"]
	}

	print("Trying to authenticate.")
	print(encode(auth_data, indent=4))
	auth_response : Response = s.post(url=AUTH_ROUTE, json=auth_data)

	if auth_response.status_code != 200:
		print("Authentication failed.")
		print(auth_response.json())
		return None

	try:
		print("Writing cookie.")
		cookie_file = open(SESSION_PATH, "wb") 
		pickle.dump(auth_response.cookies, cookie_file)
		cookie_file.close()
		print(f"Wrote cookie: {auth_response.cookies}")

		plain_cookie = open(PLAIN_COOKIE_PATH, "w")
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

	key_res:Response = s.get(url=GETKEY_ROUTE)

	if key_res.status_code != 200:
		print("Failed to obtain stream key: " + key_res.text)
		return None
	
	return key_res.json()

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


def update_stream_info(title, category, session_id):
	data = json_serialize(UpdateRequest(title, category))
	update_res:Response = post(url=UPDATE_INFO_PATH, json=data)

	if update_res is None or update_res.status_code!=200:
		print("Failed to send update_stream request.")
		if update_res is not None:
			print("Update result: ")
			print(update_res.json())
		return 


if __name__ == "__main__":

	session_id = authenticate(USERNAME, EMAIL, PASSWORD)	
	if session_id is None: 
		print("Failed to register or authenticate ... ")
		exit(1)
	print(f"Authenticated: {session_id}")

	key_data = request_key()
	if key_data is None:
		print("Failed to obtain stream key ... ")
		exit(2)
	print(f"Obtained key: {key_data}")

	stream_name = key_data['value']
	print(f"publishing : {CONTENT_PATH} to: {INGEST_URL}/{stream_name}")
	process = publish_stream(CONTENT_PATH, INGEST_URL, stream_name)
	# process = publish_stream(CONTENT_PATH, INGEST_URL, "BtuvCHgOgulyvZO")
	

	input("Press Enter to stop publisher ...")
	process.terminate()
	process.wait()
	