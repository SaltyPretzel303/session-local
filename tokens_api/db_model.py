from mongoengine import Document, StringField, DateTimeField
from mongoengine import ListField, ReferenceField
from datetime import datetime

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
