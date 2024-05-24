#!/usr/bin/python 
from mongoengine import connect 
from models import StreamData
from argparse import ArgumentParser
from random import randrange

parser = ArgumentParser()
parser.add_argument("--count", action='store', default='1')

args = parser.parse_args()

categories = ['chatting',
			  'gaming',
			  'music',
			  'art',
			  'sport',
			  'science']

template = {
    "title": "streamer-1's live",
    "creator": 'streamer-0',
    "category": 'chatting',
    "ingest_ip": 2886926349,
    "stream_key": 'lerTN7xs60',
    "media_servers": [
      {
        "quality": 'stream',
        "ip": 2886926356,
        "region": 'eu',
        "media_url": 'http://eu-0-cdn.session.com/live/streamer-0.m3u8'
      },
      {
        "quality": 'preview',
        "ip": 2886926356,
        "region": 'eu',
        "media_url": 'http://eu-0-cdn.session.com/preview/streamer-0/index.m3u8'
      }
    ],
    "is_public": True
  }

def get_title(index):
	return f"Streamer-{index}'s live"

def get_creator(index):
	return f"streamer-{index}"

def get_category():
	return categories[randrange(0, len(categories))]

connect('streams')

for i in range(0, int(args.count)):
	data = StreamData(**template)
	data.title = get_title(i)
	data.creator = get_creator(i)
	data.category = get_category()
	print(f"Saving: {data.creator} -> {data.title} -> {data.category}")
	data.save()

