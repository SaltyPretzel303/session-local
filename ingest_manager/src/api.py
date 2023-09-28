from flask import Flask, request, jsonify, send_file
from flask_restful import Resource, Api
from flask_api import status
import jsonpickle
import docker

from shared_model.ingest_response import IngestResponse, ResponseStatus
from shared_model.spawn_stream_request import SpawnStreamRequest

INGEST_SERVICE_IMAGE = "session/ingest"
INGEST_PATH = 'live/stream'

app = Flask(__name__)
api = Api(app)

docker_client = docker.from_env()

# TODO somehow get some available port ...
OUTSIDE_INGEST_PORT = '9991'
OUTSIDE_WATCH_PORT = '9992'


def json_serialize(content) -> str:
    return jsonpickle.encode(content, unpicklable=False)


@app.route('/create', methods=['GET'])
def create_stream_ingest():

    ing_request = SpawnStreamRequest(**request.args)

    print("Will try to spawn some ingest for you ... ")

    # TODO Read from config
    container_name = "ingest_for_" + ing_request.title
    port_mapping = {
        OUTSIDE_INGEST_PORT+'/tcp': '9991',
        OUTSIDE_WATCH_PORT+'/tcp': '9992'
        # 9992 should be exposed on media server or cdn
    }

    container = docker_client.containers.run(INGEST_SERVICE_IMAGE,
                                             command=None,
                                             auto_remove=True,
                                             detach=True,
                                             name=container_name,
                                             ports=port_mapping,
                                             volumes=None)

    if container is None:
        print("Failed to spawn ingest ... ")
        return IngestResponse(ResponseStatus.ERROR, "", "", ""), status.HTTP_500_INTERNAL_SERVER_ERROR

    cont_info = docker_client.containers.get(container_name)

    cont_ip = cont_info.attrs \
        .get('NetworkSettings') \
        .get('Networks') \
        .get('bridge') \
        .get('IPAddress')
    cont_id = cont_info.attrs.get("Id")

    inge_response = IngestResponse(ResponseStatus.SUCCESS,
                                   cont_ip,
                                   OUTSIDE_INGEST_PORT,
                                   cont_id)

    print(json_serialize(inge_response))

    return json_serialize(inge_response), status.HTTP_200_OK


if __name__ == '__main__':
    app.run(port='8001')
    # app.run(host='0.0.0.0', port='8001')  # possibly will be required
