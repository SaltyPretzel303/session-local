#!/usr/bin/python

from mongoengine import connect
from models import StreamData

connect('streams')

name_query = "streamer"

data = StreamData.objects.aggregate([
			{'$match': {
				"$or": [
					{'$expr': {'$gt': [{'$indexOfCP': ["$title", name_query]}, -1]}},
					{'$expr': {'$gt': [{'$indexOfCP': ["$creator", name_query]}, -1]}},
				]
			}},
			{'$project': {
				'media_servers': { 
					'$filter': {
						'input': '$media_servers',
						'as': 'server',
						'cond': {"$eq": ['$$server.region', 'eu']}
					}
				},
				'_id':False
			}},
			{'$match': {'media_servers.0': {'$exists': True}}}
		])

for d in data: 
	print(d)