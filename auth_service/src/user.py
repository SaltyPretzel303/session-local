from mongoengine import Document, StringField, DateTimeField

class User(Document):
	username = StringField(required=True)
	email = StringField(required=True)
	# I guess if logged in with google it wont be required ... ? 
	password = StringField() 
	stream_key = StringField(required=True)
	key_exp_date = DateTimeField()
	last_authenticated = DateTimeField()
