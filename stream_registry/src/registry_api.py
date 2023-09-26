from flask import Flask, g, request
from flask_api import status
from flask_restful import Api

import jsonpickle

from app_config import AppConfig
from shared_model.stream_info import StreamInfo
from stream_data import StreamData
from db import Db


JSON_CONTENT_TYPE = 'application/json'

app = Flask(__name__)
api = Api(app)


def json_serialize(content) -> str:
    return jsonpickle.encode(content, unpicklable=False)


def get_db() -> Db:
    if 'db' not in g:
        print("creating request scoped db ... ")
        config = AppConfig.get_instance()
        address = config["db_address"]
        port = config["db_port"]
        db = config["db_name"]
        user = config["db_user"]
        pwd = config["db_password"]
        g.db = Db(f"mongodb://{user}:{pwd}@{address}:{port}/{db}")

    print("returning request scoped db ... ")
    return g.db


def close_db():
    db = g.pop('g', None)
    if db is not None:
        db.close()


def get_db_url() -> str:
    config = AppConfig.get_instance()
    return f"mongodb://{config.db_address}:{config.db_port}/{config.db_table}"


@app.route('/by_creator/<creator>', methods=['GET'])
def get_by_creator(creator: str):
    print(f"by_creator request: {creator}")

    stream_info = get_db().get_by_creator(creator)
    if stream_info is None:
        return "This creator is not live ... ", status.HTTP_404_NOT_FOUND

    return json_serialize(stream_info), status.HTTP_200_OK


@app.route('/register', methods=['POST'])
def register():
    print("Register request received ... ")

    content_type = request.headers.get('Content-type')
    if content_type != JSON_CONTENT_TYPE:
        return f"Content-type not supported (only {JSON_CONTENT_TYPE} allowed) ... ", status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    info = StreamInfo(**request.get_json())

    res = get_db().save(info)
    if res is not None:
        return json_serialize(res), status.HTTP_200_OK
    else:
        return "Failure ... ", status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route("/by_category/<category>", methods=['GET'])
def get_by_category(category: str):
    print(f"by_category request: {category}")

    from_ind = request.args.get(key="from", type=int)
    to_ind = request.args.get(key="to", type=int)

    streams = get_db().get_by_category(category, from_ind, to_ind)
    if streams is None:
        return "No such category ... ", status.HTTP_200_OK

    return json_serialize(streams), status.HTTP_200_OK


if __name__ == '__main__':
    app.run(port='8002')

# check out this link
# how to create/start/stop containers over rest
# https://docs.docker.com/engine/api/v1.19/#/inside-docker-run
