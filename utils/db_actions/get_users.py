#!/usr/bin/python 

from mongoengine import connect
from models import User
from jsonpickle import encode, decode

connect(host="mongodb://localhost:37017/session_auth")

for u in User.objects():
	print(encode(decode(u.to_json()),indent=4))