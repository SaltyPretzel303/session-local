#!/usr/bin/python 

from dataclasses import dataclass
import json
from flask import Response
from requests import post
from jsonpickle import encode, decode
from sys import argv

def jsonify(obj):
	return encode(obj, unpicklable=False)

@dataclass
class AuthRequest:
	username: str
	password: str

@dataclass
class User: 
	username: str
	email: str

@dataclass
class AuthResponse:
	status: int
	user: User = None
	message: str = ""


if len(argv)<2:
	print("Provide username and password")
	print("eg: ./plain_auth.py user password")

	exit(1)

username = argv[1]
password = argv[2]

req_data = AuthRequest(username, password)

print("Sending auth request")
# response: Response = post("http://localhost:8003/authenticate", json=jsonify(req_data))
# response: Response = post("http://localhost:8003/authenticate", json=req_data.__dict__)
# response: Response = post("http://localhost:8003/authenticate", json=json.dumps(req_data))
response: Response = post("http://localhost:8003/authenticate", json=req_data.__dict__)

if response is None:
	print("Failed to send auth. request.")
	exit(1)

print("Received valid response.")

auth_res = AuthResponse(**response.json())
print("Response")
print(jsonify(auth_res))

