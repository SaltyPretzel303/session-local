from bcrypt import hashpw, gensalt
from mongoengine import Document
from mongoengine import StringField, ListField, BinaryField, ReferenceField

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
