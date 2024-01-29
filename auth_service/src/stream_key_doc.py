from mongoengine import Document, StringField, DateTimeField, ReferenceField
from datetime import datetime
from user_doc import UserDoc

class StreamKeyDoc(Document):
	meta={'collection': 'stream_key'}

	value = StringField(required=True)
	exp_date = DateTimeField()
	owner = ReferenceField(UserDoc)

	def is_expired(self) -> bool:
		return self.exp_date is None or datetime.now() > self.exp_date