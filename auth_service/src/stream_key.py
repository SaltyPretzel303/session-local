from mongoengine import Document, StringField, DateTimeField, ReferenceField
from datetime import datetime, timedelta
from user import User

class StreamKey(Document):
	value = StringField(required=True)
	exp_date = DateTimeField()
	owner = ReferenceField(User)

	def is_expired(self) -> bool:
		return self.exp_date is None or datetime.now() > self.exp_date