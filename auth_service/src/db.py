from follow_record_doc import FollowRecordDoc
from stream_key_doc import StreamKeyDoc
from user_doc import UserDoc
from mongoengine import connect as mongo_connect
from mongoengine import disconnect as mongo_disconnect 

class Db:

	def __init__(self, conn_string:str):
		self.conn_string = conn_string
		self.connect()

	def connect(self):
		print(f"Connecting with mongo on: {self.conn_string}")
		mongo_connect(host=self.conn_string)

	def close(self):
		mongo_disconnect()

	def get_user(self, user_name:str) -> UserDoc:
		return UserDoc.objects(username=user_name).first()
	
	# Looks stupid but ensures that connection is established before calling 
	# user.save at some random point.
	def save_user(self, user: UserDoc) -> UserDoc:
		return user.save()
	# Even more stupid is that connection failure is never handled ... :)

	def save_key(self, key: StreamKeyDoc) -> StreamKeyDoc:
		return key.save()

	def get_key_with_val(self, key_val:str) -> StreamKeyDoc:
		return StreamKeyDoc.objects(value=key_val).first()

	def get_key_with_owner(self, user: UserDoc) -> StreamKeyDoc:
		return StreamKeyDoc.objects(owner=user).first()

	def invalidate_key(self, key: StreamKeyDoc) -> StreamKeyDoc:
		key.exp_date = None
		return key.save()
	
	def get_followers_of(self, of_user: UserDoc, from_ind:int, count:int):
		end_ind:int = from_ind + count
		foll_doc = FollowRecordDoc.objects\
			.filter(user=of_user)\
			.fields(slice__following=[from_ind, end_ind])\
			.first()

		if foll_doc is None:
			return []
		else:
			return foll_doc.following
		
		