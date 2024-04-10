#!/usr/bin/python 

from mongoengine import connect, Document
from mongoengine import StringField, IntField, ListField
from jsonpickle import encode
from models import StreamData

class Data(Document):
	name=StringField()
	array=ListField()

def get_data(i: int):
	return Data(name=f"data_{i}", 
			#  array=[IntField(value=ind) for ind in range(i*5,i*5+10)]
			array=list(range(i*5,i*5+10)))

# d = [get_data(i) for i in range(0,5)]

# for data in d: 
# 	print(data.to_json())

# for data in d: 
# 	data.save()


# pipeline = [
# 	{'$match': {'array': 10}},
# 	{'$project': {
# 		'array': {
# 			'$filter': {
# 				'input': '$array',
# 				'as': 'value',
# 				'cond': {'$gt': ['$$value', 10]}
# 			}
# 		},
# 		'name':1,
# 		'_id':0
# 	}},
# 	{'$skip': 0},
# 	{'$limit': 2}
	
# ]

# for d in Data.objects().aggregate(pipeline):
# 	print(d)

# pipeline = [
# 	{'$match': {'media_servers.region': 'eu'}},
# 	{'$project': {
# 		'media_servers': {
# 			"$filter": {
# 				'input': "$media_servers",
# 				'as': 'server',
# 				'cond': {'$eq': ['$$server.region', 'na']}
# 			}
# 		}
# 	}}
	
# ]

# connect(db='streams')

# for d in StreamData.objects().aggregate(pipeline):
# 	print(d)

connect(db='mockup_data')

data = StreamData.objects(title='stream_0').update_one(set__creator='mememe',set__category='uncategorized')
print(data)