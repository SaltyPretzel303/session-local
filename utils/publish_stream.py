import sys
import ffmpeg
import pickle
from requests import post, get,  Response
from requests import Session

CONTENT_PATH = '/home/nemanja/Videos/clock.mp4'
INGEST_URL = 'rtmp://localhost:9090/ingest' 

USERNAME = "streamer"
EMAIL = "some_streamer@session.com"
PASSWORD = "strong_password"

AUTH_ROUTE = "http://localhost:8003/authenticate"
REGISTER_ROUTE = "http://localhost:8003/register"
GETKEY_ROUTE = "http://localhost:8003/get_key"
GET_INGEST_ROUTE="http://localhost:8001/get_ingest"

COOKIE_PATH = "./cookie"

def get_cookie_path(user: str):
	return f"{user}_cookie"

def authenticate(username: str, email: str, password:str ):

	register_data = {
		"username": username,
		"password": password,
		"email": email
	}

	print("Doing register ... ")

	reg_response : Response = post(url=REGISTER_ROUTE, json=register_data) 
		
	if reg_response.status_code !=  200:
		return None

	s = Session()
	try:
		cookie_file = open(COOKIE_PATH, "rb") 
		if not cookie_file.read():
			print("Cookie file empty ... ")
		else:
			cookie_file.seek(0)
			s.cookies.update(pickle.load(cookie_file))
			cookie_file.close()

	except IOError as err:
		print("Failed to read cookie ... ")
		 
	auth_data = {
		"email": register_data["email"],
		"password": register_data["password"]
	}

	print("Doing authenticate ... ")

	auth_response : Response = s.post(url=AUTH_ROUTE, json=auth_data)

	if auth_response.status_code != 200:
		return None
	
	print(f'Session_id: {auth_response.cookies.get("session")}')

	try:
		cookie_file = open(COOKIE_PATH, "wb") 
		pickle.dump(auth_response.cookies, cookie_file)
		cookie_file.close()

	except IOError as err:
		print("Failed to write cookie ... ")
		print(err)

	return auth_response.cookies.get("session")


def request_key():
	s = Session()
	try:
		cookie_file = open(COOKIE_PATH, "rb") 
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


def get_ingest_url():
	ingest = None
	try:
		ingest_res = get(GET_INGEST_ROUTE)

		if ingest_res.status_code != 200:
			raise Exception("Return code is not 200 ... ")
		
		ingest = ingest_res.text

	except Exception as e:
		print(f"Failed to optain free ingest: {e}")
	
	return ingest


def publish_stream(video_path, ingest_path, stream_name):

	# process = (
	# 	ffmpeg
	# 	.input(video_path)
	# 	.output(
	# 		f"{ingest_path}/{stream_name}",
	# 		codec="copy",  # use same codecs of the original video
	# 		format='flv',  # force format
	# 		flvflags="no_duration_filesize",
	# 		# ^ will prevent: 'Failed to update header with correct duration.'
	# 		# https://stackoverflow.com/questions/45220915
	# 		# vcodec='libx264',
	# 		# pix_fmt='yuv420p',
	# 		# preset='veryfast',
	# 		# r='20',
	# 		# g='50',
	# 		# video_bitrate='1.4M',
	# 		# maxrate='2M',
	# 		# bufsize='2M',
	# 		# segment_time='6' # don't know what is this, maybe delay or buffer_size ?
	# 	)
	# 	.global_args("-re")  # argument to act as a live stream
	# 	.run_async()
	# )

	cmd = ffmpeg\
		.input(video_path, re=None)\
		.output(
			f"{ingest_path}/{stream_name}",
			format='flv',  # force format
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

	ingest_url = get_ingest_url()
	if ingest_url is None: 
		print("Failed ot obtain free ingest ... ")
		exit(3)

	print(f"publishing : {CONTENT_PATH} to: {ingest_url}/{stream_key}")

	# process = publish_stream(CONTENT_PATH, INGEST_URL, stream_key)

	process = publish_stream(CONTENT_PATH, INGEST_URL, "stream")
	input("Press Enter to stop publisher ...")
	process.terminate()
	process.wait()
