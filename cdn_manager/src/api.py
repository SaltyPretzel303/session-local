from threading import Event, Thread
from flask import Flask
from flask_restful import Api
from requests import get
from flask_api import  status
import signal


app = Flask(__name__)
api = Api(app)


region_conf = {
	"eu": [
		"127.0.0.1",
		"127.0.0.2" # fallbacks
	],
	"na": [
		"127.0.0.3",
		"127.0.0.4" # fallbacks
	]
	# hc path 
}

@app.route("/match_region/<region>", methods=["GET"])
def match_region(region:str):
	if region not in region_conf:
		return "Region not available ... ", status.HTTP_404_NOT_FOUND
	
	if not is_available(region_conf[region][0]):
		print(f"Region's ({region}) main instance is not available ... ")

		alt_instance = next(filter(is_available, region_conf[region][1:]), default=None)
		if alt_instance is not None:
			return alt_instance, status.HTTP_200_OK

	return region_conf[region][0], status.HTTP_200_OK
		

def is_available(addr:str):
	url = f"{addr}/{region_conf.hc_path}"
	try:
		res = get(url)
		if res.status_code != status.HTTP_200_OK:
			raise Exception(f"Host on: {url} unavailable ... ")
	except: 
		return False

	return True

# HC_CHECK = 10

# quit_event = Event()

# def quit_handler(signo, _frame):
# 	return None

# def poller():
# 	while not quit_event.is_set():



if __name__ == '__main__':

	# signal.signal(signal.SIGTERM, quit_handler)
	# signal.signal(signal.SIGINT, quit_handler)

	# poll_thread = Thread(target=poller)
	# poll_thread.start()
		
	app.run(host="0.0.0.0", port='8004')
