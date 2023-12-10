from flask import Flask, request
from flask_restful import Api
from flask_api import status

import jsonpickle
import requests

from app_config import AppConfig

from shared_model.start_stream_request import StartStreamRequest
from shared_model.start_stream_response import StartStreamResponse
from shared_model.start_stream_response import ResponseStatus as GatewayResponseStatus
from shared_model.stream_info import StreamInfo
from shared_model.ingest_response import IngestResponse
from shared_model.ingest_response import ResponseStatus as IngestResponseStatus

JSON_CONTENT_TYPE = 'application/json'

app = Flask(__name__)
api = Api(app)


def json_serialize(content) -> str:
    return jsonpickle.encode(content, unpicklable=False)


def get_registry_url() -> str:
    address = AppConfig.get_instance().registry_address
    port = AppConfig.get_instance().registry_port
    return f"http://{address}:{port}"


@app.route('/start_stream', methods=['POST'])
def start_stream():

    content_type = request.headers.get('Content-type')
    if content_type != JSON_CONTENT_TYPE:
        return f"Content-type not supported (only {JSON_CONTENT_TYPE} allowed) ... ", status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    req_data = StartStreamRequest(**request.get_json())
    print("Request: ")
    print(jsonpickle.dumps(req_data, unpicklable=False, indent=4))

    registry_url = form_get_stream_url(req_data.creator)
    registry_response = requests.get(registry_url)

    response_obj = StartStreamResponse(GatewayResponseStatus.ERROR, None)
    response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

    if registry_response.status_code == status.HTTP_200_OK and registry_response.json() is not None:
        print("Creator is already live ... ")

        live_data = StreamInfo(**registry_response.json())

        response_obj.data = live_data
        response_obj.status = GatewayResponseStatus.ALREADY_STREAMING
        response_status = status.HTTP_200_OK
    else:
        print("Will try to spawn stream ingest ... ")

        ingest_url = form_spawn_ingest_url()
        ingest_params = [
            ('creator', req_data.creator),
            ('title', req_data.title),
            ('category', req_data.category)
        ]
        ingest_res = requests.get(ingest_url, ingest_params)

        if ingest_res.status_code == status.HTTP_200_OK and ingest_res.json() is not None:
            print("Ingest gateway returned result ... ")
            ingest_data = IngestResponse(**ingest_res.json())
            print(json_serialize(ingest_data))

            if ingest_data.status == IngestResponseStatus.SUCCESS:
                print("Ingest successfully spawned ... ")
                res_data = ingest_data_to_info(req_data.title,
                                               req_data.creator,
                                               req_data.category,
                                               ingest_data,
                                               [])

                response_obj.data = res_data
                response_obj.status = GatewayResponseStatus.STARTED
                response_status = status.HTTP_200_OK

            else:
                print("Ingest manager returned error ... ")
                response_obj.status = GatewayResponseStatus.ERROR
                response_obj.data = None
                response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        else:
            response_obj.status = GatewayResponseStatus.ERROR
            response_obj.data = None
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

    return json_serialize(response_obj), response_status


# def stream_data_to_info(live_data) -> StreamInfo:
#     return StreamInfo(live_data[1]['title'],
#                       live_data[1]['creator'],
#                       live_data[1]['category'],
#                     #   live_data[1]['stream_id'],
#                       live_data[1]['ingest_ip'],
#                       live_data[1]['media_servers'])


def ingest_data_to_info(title: str,
                        creator: str,
                        category: str,
                        ing_data: IngestResponse,
                        media_servers: [str]) -> StreamInfo:

    return StreamInfo(title,
                      creator,
                      category,
                      ing_data.stream_key,
                      f"{ing_data.ip}:{ing_data.port}",
                      media_servers)


def form_get_stream_url(creator: str):
    address = AppConfig.get_instance()["registry_address"]
    port = AppConfig.get_instance()["registry_port"]
    resource = AppConfig.get_instance()["registry_by_creator"]

    return f"http://{address}:{port}/{resource}/{creator}"


def form_spawn_ingest_url():
    config = AppConfig.get_instance()

    return f'http://{config["ingest_address"]}:{config["ingest_port"]}/{config["ingest_spawn"]}'


@app.route('/list/<category>', methods=['GET'])
def list_streams(category: str):
    from_ind = request.args.get(key="from", default=0, type=int)
    to_ind = request.args.get(key="to", default=None, type=int)

    print(category)
    print(request.args)

    if to_ind != None and from_ind >= to_ind:
        return "from_index greater or equal to to_index", status.HTTP_400_BAD_REQUEST

    url = f"{form_get_category_url()}/{category}"
    response = requests.get(url, {"from": from_ind, "to": to_ind})

    if response.status_code != status.HTTP_200_OK:
        return "Registry returned bad value ... ", status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        return json_serialize(response.json()), status.HTTP_200_OK


def form_get_category_url():
    config = AppConfig.get_instance()
    host = config["registry_address"]
    port = config["registry_port"]
    list_cat_res = config["registry_by_cat"]

    return f"http://{host}:{port}/{list_cat_res}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000')  # possibly will be required
