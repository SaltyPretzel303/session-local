from flask import Flask, request, jsonify, send_file
from flask_restful import Resource, Api
import jsonpickle
import docker

from shared_model.ingest_request import IngestRequest
from shared_model.ingest_info import IngestInfo

INGEST_SERVICE_IMAGE = "session/rtmp/nginx"
INGEST_PATH = 'live/stream'

app = Flask(__name__)
api = Api(app)

docker_client = docker.from_env()

# TODO somehow get some available port ...
OUTSIDE_INGEST_PORT = '9991'
OUTSIDE_WATCH_PORT = '9992'


@app.route('/create', methods=['POST'])
def create_stream_ingest() -> IngestInfo:

    # TODO use this data to register stream in stream_registry
    data = request.json
    ingest_request: IngestRequest = jsonpickle.decode(data)

    container_name = "ingest_for_" + ingest_request.stream_title
    port_mapping = {
        OUTSIDE_INGEST_PORT+'/tcp': '9991',
        OUTSIDE_WATCH_PORT+'/tcp': '9992'
        }

    container = docker_client.containers.run(INGEST_SERVICE_IMAGE,
                                             command=None,
                                             auto_remove=True,
                                             detach=True,
                                             name=container_name,
                                             ports=port_mapping,
                                             volumes=None)

    if container is None:
        print("Failed to create ingest container ... ")

        return '500'

    cont_info = docker_client.containers.get(container_name)

    cont_ip = cont_info.attrs.get('NetworkSettings').get(
        'Networks').get('bridge').get('IPAddress')

    stream_info = IngestInfo(cont_ip, OUTSIDE_INGEST_PORT, INGEST_PATH)

    return jsonpickle.encode(stream_info, unpicklable=True)


if __name__ == '__main__':
    app.run(port='8001')
