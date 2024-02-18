#!/usr/bin/python 

from mongoengine import connect
from models import StreamKeyDoc
from jsonpickle import encode, decode

connect(host="mongodb://localhost:37017/session_auth")

for key in StreamKeyDoc.objects():
	print(encode(decode(key.to_json()),indent=4))