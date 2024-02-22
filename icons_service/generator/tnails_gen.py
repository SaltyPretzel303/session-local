from jsonpickle import decode 
from dataclasses import dataclass

from threading import Event 
from requests.api import get
from datetime import datetime, timedelta

POLL_PERIOD = 10
SINCE_QUERY_URL = "http://stream-registry.session:8002/stream/since"
TNAILS_SAVE_PATH = "/var/icons/tnails"
TNAILS_FORMAT = "jpg"

def form_since_query(url:str, time:datetime):
	return f"{url}/{datetime.isoformat()}"


timer = Event()
timer.clear()

last_check = datetime.now()

while not timer.is_set(): 
	print("Polling streams ... ")

	try: 
		streams = get(SINCE_QUERY_URL)

	except Exception as e:
		print("Failed to poll active streams ... ")
		print(e)
		exit(1)




