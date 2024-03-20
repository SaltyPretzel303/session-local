from mongoengine import Document, StringField, ListField, LongField, BooleanField, EmbeddedDocumentField

from ipaddress import ip_address

from stream_registry.src.media_server_data import MediaServerData

class StreamData(Document):
	title = StringField(required=True, max_length=120)
	creator = StringField(required=True, max_length=20)
	category = StringField(required=True, max_length=40)

	ingest_ip = LongField(required=True)
	stream_key = StringField(required=True)
	
	# ip is stored as an number in order to allow queries on it
	media_servers = ListField(EmbeddedDocumentField(MediaServerData))

	is_public = BooleanField(required=True, default=False)

	def update(self, title:str, category:str, is_public: bool):
		self.title = title
		self.category = category
		self.is_public = is_public

	@staticmethod
	def empty(streamer:str, ingest_ip:str, stream_key:str):
		return StreamData(title=f"{streamer}'s live",
					creator=streamer, 
					category="chatting",
					ingest_ip=int(ip_address(ingest_ip)),
					stream_key=stream_key,
					media_servers=[],
					is_public=False)
