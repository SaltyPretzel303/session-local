from mongoengine import Document, StringField, ListField, LongField
from mongoengine import BooleanField, EmbeddedDocumentField, IntField

from ipaddress import ip_address

from stream_registry.src.media_server_data import MediaServerData

class StreamData(Document):

	# will enable searching streams by title and creator_name
	# meta = {'indexes': [
	# 				{'fields': ['$title', "$creator"],
	# 				'default_language': 'english',
	# 				'weights': {'title': 2, 'creator': 10}
	# 				}
	# 			]
	# 		}

	title = StringField(required=True, max_length=120)
	creator = StringField(required=True, max_length=20)
	category = StringField(required=True, max_length=40)

	ingest_ip = LongField(required=True)
	stream_key = StringField(required=True)
	
	# ip is stored as an number in order to allow queries on it
	media_servers = ListField(EmbeddedDocumentField(MediaServerData))

	is_public = BooleanField(required=True, default=False)

	viewer_count = IntField()

	@staticmethod
	def empty(streamer:str, ingest_ip:str, stream_key:str):
		return StreamData(title=f"{streamer}'s live",
					creator=streamer, 
					category="chatting",
					ingest_ip=int(ip_address(ingest_ip)),
					stream_key=stream_key,
					media_servers=[],
					is_public=False)
