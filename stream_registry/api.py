from flask import Flask, request, jsonify, send_file
from flask_restful import Resource, Api
import json


app = Flask(__name__)
api = Api(app)


@app.route('/add', methods=['POST'])
def create_stream_ingest():

    return


@app.route('/list', methods=['GET'])
def lits_streams():

    return


if __name__ == '__main__':
    app.run(port='8002')


# check out this link
# how to craete/start/stop containers over rest
# https://docs.docker.com/engine/api/v1.19/#/inside-docker-run
