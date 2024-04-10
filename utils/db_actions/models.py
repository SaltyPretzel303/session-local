import datetime
from ipaddress import ip_address
from bcrypt import hashpw, gensalt
from mongoengine import Document
from mongoengine import StringField, ListField, BinaryField, ReferenceField
from mongoengine import LongField, BooleanField, EmbeddedDocumentField, EmbeddedDocument
from mongoengine import DateTimeField, IntField, ObjectIdField

class UserDoc(Document):
	meta={'collection': 'user'}

	tokens_id = StringField()
	username = StringField(required=True)
	email = StringField(required=True)


class StreamKeyDoc(Document):
	meta = {'collection': 'streamKey'}

	value = StringField(required=True)
	exp_date = DateTimeField()
	owner = ReferenceField(UserDoc)

	def is_expired(self) -> bool:
		return self.exp_date is None or datetime.now() > self.exp_date
	
class FollowingDoc(Document):
	meta = {'collection':'following'}

	owner = ReferenceField(UserDoc)
	following = ReferenceField(UserDoc)
	followed_at = DateTimeField()


class MediaServerData(EmbeddedDocument):
	quality = StringField(required=True)
	ip = LongField(required=True)
	region = StringField(required=True)
	media_url = StringField(required=True)

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

class ViewerData(Document):
	stream_id = ObjectIdField()
	count = IntField()
