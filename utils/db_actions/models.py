import datetime
from bcrypt import hashpw, gensalt
from mongoengine import Document
from mongoengine import StringField, ListField, BinaryField, ReferenceField
from mongoengine import DateTimeField

class User(Document):
    username = StringField()
    email = StringField()
    pwd_hash = BinaryField()

class FollowRecord(Document):
	user = ReferenceField(User)
	following = ListField(ReferenceField(User)) 

	def follower_ids(self):
		return list(map(lambda userRef: userRef['id'], self.following))

def hash_pwd(pwd: str):
	return hashpw(pwd.encode(), gensalt())

class StreamKeyDoc(Document):
	meta={'collection': 'stream_key'}

	value = StringField(required=True)
	exp_date = DateTimeField()
	owner = ReferenceField(User)

	def is_expired(self) -> bool:
		return self.exp_date is None or datetime.now() > self.exp_date