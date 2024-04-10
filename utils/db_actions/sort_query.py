#!/usr/bin/python 

from models import StreamData, ViewerData
from mongoengine import connect 
from random import randrange

connect(db="mockup_data")

def cat(i: int):
	cats = ['chatting', 'gaming', 'working']
	return cats[randrange(0,len(cats))]

# def get_stream(i: int):
# 	return StreamData(title=f"stream_{i}",
# 				creator=f"creator_{i}",
# 				category=cat(i),
# 				ingest_ip=123123,
# 				stream_key="some_strong_key",
# 				media_servers=[],
# 				is_public=True)

# streams = [ get_stream(i)  for i in range(0,10) ]

# for s in streams: 
# 	s.save()

# for s in StreamData.objects():
# 	v_count = ViewerData(stream_id=s.id, count=randrange(0,1000))
# 	v_count.save()


scores = {
	'chatting': 10,
	'gaming': 9,
	'working': 2 
}

def gen_scores():
	return [
		{'case': {"$eq": ['$category', 'chatting']}, 'then':10},
		{'case': {"$eq": ['$category', 'gaming']}, 'then':9},
		{'case': {"$eq": ['$category', 'working']}, 'then':2}
	]

# pipeline = [
# 	{'$match': {}},
# 	{'$addFields': {
# 		"cat_score": {
# 			"$switch": {
# 				'branches': gen_scores()
# 			}
# 		}
# 	}},
# 	{'$sort': {'cat_score': -1}},
# 	{'$project':{"category": True, "cat_score":True}}
# ]

# add stream data to viewers document
# pipeline = [
# 	{'$lookup': {
# 		'from': "stream_data",
# 		'localField': "stream_id",
# 		'foreignField': '_id',
# 		'as': 'stream'
# 	}},
# 	{'$addFields': {'streamer': "$stream.creator"}}	
# ]

pipeline = [
	# {'$match',{}}
	{'$lookup':{
		'from': "viewer_data",
		'localField': '_id',
		'foreignField': 'stream_id',
		'as': 'view_count'
	}},
	{'$addFields': {"count": '$view_count.count'}},
	{'$project': {"stream_name": True, 'count': True}}
]

# q_result = StreamData.objects().aggregate(pipeline)
# q_result = ViewerData.objects().aggregate(pipeline)
q_result = StreamData.objects().aggregate(pipeline)

for d in q_result: 
	print(d)
