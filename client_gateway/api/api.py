from flask import Flask, request
from flask_restful import Api

import jsonpickle
import requests

# from api.dep_provider import DepProvider
# from shared_model.stream_info import StreamInfo
from shared_model.ingest_request import IngestRequest
from shared_model.ingest_info import IngestInfo

# streams_db = DepProvider.get_streams_db()

app = Flask(__name__)
api = Api(app)

# TODO move to some config
INGEST_SERVICE_URL = "http://localhost:8001/create"


@app.route('/list', methods=['GET'])
def list_streams():
    # TODO implement by reading stream_registry
    # return jsonpickle.encode(streams_db.list_streams(), unpicklable=False)
    return '200'


@app.route('/create', methods=['GET'])
def create_stream():
    args = request.args
    user_id = args.get("user_id", default="0", type=str)
    stream_title = args.get("stream_title", default="", type=str)

    print("Requested to create stream: " + stream_title)
    print("By: " + user_id)

    ingest_request = IngestRequest(user_id, stream_title)
    ingest_response = requests.post(
        INGEST_SERVICE_URL,
        json=jsonpickle.encode(ingest_request, unpicklable=True))

    if ingest_response.status_code != 200:
        print("Ingest request failed")
        print("Response: " + str(ingest_response.status_code))

        # TODO send some errorMessage+code ... or something to client
        return "Ingest request failed"

    print("Ingest request was successful ... ")

    json_content: IngestInfo = jsonpickle.decode(ingest_response.content)
    # this obj. is still not used, but it is here for future use
    # returned value is just passed to the client

    return ingest_response.content


@app.route('/watch', methods=['GET'])
def get_stream():

    # TODO check stream_registry and return stream_info

    return


if __name__ == '__main__':
    app.run(port='8000')
