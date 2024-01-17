from flask import Flask, request
from flask_restful import Api
from flask_api import status

import jsonpickle
import requests

from app_config import AppConfig

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
