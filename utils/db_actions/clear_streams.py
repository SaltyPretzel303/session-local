#!/usr/bin/python 

from mongoengine import connect
from models import StreamData

connect(db='streams')

for data in StreamData.objects():
	print(data.to_json())


