from mongoengine import Document, ObjectIdField, BooleanField, DateTimeField

class ViewerData(Document):
	stream_id = ObjectIdField()
	authorized = BooleanField()
	viewer_id = ObjectIdField()
	expire_at = DateTimeField()
	# mongo _id will be used as an unique identifier for unauthorized viewers