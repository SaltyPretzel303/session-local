#!/usr/bin/python 
from mongoengine import connect 
from models import StreamData

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
    "is_public": False
  }

connect('streams')

StreamData(**template).save()