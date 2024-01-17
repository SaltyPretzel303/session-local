from mongoengine import Document, StringField, ListField, LongField, BooleanField

from ipaddress import ip_address

class StreamData(Document):
	title = StringField(required=True, max_length=120)
	creator = StringField(required=True, max_length=20)
	category = StringField(required=True, max_length=40)

	ingest_ip = LongField(required=True)
	stream_key = StringField(required=True)
	
	# ip is stored as an number in order to allow queries on it
	media_servers = ListField(LongField()) 

	is_public = BooleanField(required=True, default=True)
	# TODO default here should be false
	

	# def to_stream_info(self) -> StreamInfo:
	# 	server = self.media_servers[0] if len(self.media_servers) > 0 else None
	# 	return StreamInfo(title=self.title,
	# 					  creator=self.creator,
	# 					  category=self.category,
	# 					  media_server=server)

	def update(self, title:str, category:str, is_public: bool):
		self.title = title
		self.category = category
		self.is_public = is_public

	# @staticmethod
	# def from_stream_info(info: StreamInfo):
	# 	return StreamData(
	# 		title=info.title,
	# 		creator=info.creator,
	# 		category=info.category,
	# 		ingest_ip=int(ip_address(info.ingest_ip)),
	# 		media_servers=(
	# 			list(map(lambda ip: int(ip_address(ip)), info.media_servers))),
	# 		is_public=info.is_public)
	

	@staticmethod
	def empty(streamer:str, ingest_ip:str, stream_key:str):
		return StreamData(creator=streamer, 
					title=f"{streamer}'s live",
					category="chatting",
					ingest_ip=int(ip_address(ingest_ip)),
					stream_key=stream_key)
