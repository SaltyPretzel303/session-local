from mongoengine import Document, StringField, BinaryField

class User(Document):
	# tokens id 
	username = StringField(required=True)
	email = StringField(required=True)
	pwd_hash = BinaryField()
	# I guess not required in the case of google login or such ... ? 

	# stream_key = ReferenceField(StreamKey)
	