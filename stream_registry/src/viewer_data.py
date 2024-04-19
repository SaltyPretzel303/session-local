from mongoengine import Document, ObjectIdField, BooleanField
from mongoengine import StringField,  DateTimeField

class ViewerData(Document):
	meta = {
			'indexes': 
			[
            	{'fields': ['expire_at'], 'expireAfterSeconds': 0}
        	]
	}

	stream = StringField()
	viewer = StringField()

	expire_at = DateTimeField()
	