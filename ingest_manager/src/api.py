from multiprocessing import Event
from threading import Thread
from flask import Flask, request, jsonify, send_file
from flask_restful import Resource, Api
from flask_api import status
from requests import get
# from flask_api import status
import jsonpickle

from shared_model.ingest_response import IngestResponse, ResponseStatus
from shared_model.spawn_stream_request import SpawnStreamRequest
from shared_model.ingest_data import IngestData

import signal 

INGEST_SERVICE_IMAGE = "session/ingest"
INGEST_PATH = 'live/stream'

app = Flask(__name__)
api = Api(app)

# TODO repace this with some kind of db 
active_ingests = {}

quit_event = Event()

def log_ingests():
	json_serialize(active_ingests)

def json_serialize(content) -> str:
	return jsonpickle.encode(content, unpicklable=False)

@app.route('/register', methods=['POST'])
def register():
	if request.data is None: 
		return "No data provided ... ", status.HTTP_400_BAD_REQUEST
	
	if not request.is_json: 
		return "Json data required ... ", status.HTTP_400_BAD_REQUEST

	try: 
		reg_request = IngestData(**request.get_json())
	except TypeError: 
		print("Unable to parse incoming data ... ")
		
		return "Error parsing data ... ", status.HTTP_400_BAD_REQUEST

	if reg_request.form_id() in active_ingests:
		return "Ingest already registered ... ", status.HTTP_200_OK
	else:
		active_ingests[reg_request.form_id()] = reg_request
		log_ingests()

		return "Ingest registered ... ", status.HTTP_200_OK

@app.route('/unregister/<id>', methods=['GET'])
def unregister(id):
	if id is None or id == "":
		return status.HTTP_400_BAD_REQUEST

	if id in active_ingests:
		del active_ingests[id]
		return status.HTTP_200_OK
	else:
		return status.HTTP_404_NOT_FOUND

def is_free(key_value):
	return key_value[1].streams_cnt < key_value[1].max_streams

def get_free_ingest():
	ingest = next(filter(is_free, active_ingests.items()), None)
	if ingest is not None:
		ingest = ingest[1]

	return ingest

def form_url(data:IngestData):
	return f"rtmp://{data.ip}:{data.port}/{data.ingest_path}"

@app.route("/get_ingest", methods=["GET"])
def get_ingest():
	free_ingest:IngestData = get_free_ingest()

	if free_ingest is None:
		print("Free ingest not fount ... ")
		return "No free ingests ...", status.HTTP_404_NOT_FOUND
	
	log_ingests()

	return form_url(free_ingest), status.HTTP_200_OK

def hc_check(ing_data: IngestData):
	url = ing_data.health_check_path
	try:
		hc_resp = get(url)

		if hc_resp.status_code != 200:
			raise Exception("Received not-200 code  ... ")
		
		return True
	except:
		print(f"Failed to do hc on: {url}")
		return False

# TODO add list ingest 

HC_CHECK_INTERVAL = 600

def poller():
	while not quit_event.is_set():
		global active_ingests
		active_ingests= { key:active_ingests[key] \
					for key in active_ingests \
					if hc_check(active_ingests[key]) }


		print(f"Active configs cnt: {len(active_ingests)} ")
		# TODO externalize this to config

		quit_event.wait(HC_CHECK_INTERVAL)


def quit_handler(signo, _frame):
	print(f"Handling {signo} ... ")

	if not quit_event.is_set():
		quit_event.set()

	print(f"{signo} handled ... ")

	exit(0)

if __name__ == '__main__':

	signal.signal(signal.SIGINT, quit_handler)
	signal.signal(signal.SIGTERM, quit_handler)

	poll_thread = Thread(target=poller)
	poll_thread.start()
	app.run(host='0.0.0.0', port='8001')
