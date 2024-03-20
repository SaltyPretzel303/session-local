from mongoengine import EmbeddedDocument, StringField, LongField

class MediaServerData(EmbeddedDocument):
	quality = StringField(required=True)
	ip = LongField(required=True)
	region = StringField(required=True)
	media_url = StringField(required=True)