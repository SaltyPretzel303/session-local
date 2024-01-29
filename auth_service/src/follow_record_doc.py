from mongoengine import Document, ReferenceField, ListField

from auth_service.src.user_doc import UserDoc

class FollowRecordDoc(Document):
	meta = {'collection':'follow_record'}

	user = ReferenceField(UserDoc)
	following = ListField(ReferenceField(UserDoc)) 

	def follower_ids(self):
		return list(map(lambda userRef: userRef['id'], self.following))
	