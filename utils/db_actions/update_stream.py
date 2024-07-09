#!/usr/bin/python 

from mongoengine import connect 
from argparse import ArgumentParser
from models import StreamData

parser = ArgumentParser()
parser.add_argument('--stream', action='store', required=True)
parser.add_argument("--title", action='store', default='Not-default-title')
parser.add_argument("--category", action='store', default='chatting')
args = parser.parse_args()

connect(db='streams')

update_res = StreamData.objects(creator=args.stream)\
	.update_one(set__title=args.title, 
			 set__category=args.category,
			 set__is_public=True)

if update_res > 0:
	print("Success.")
else: 
	print("Failed to update.")