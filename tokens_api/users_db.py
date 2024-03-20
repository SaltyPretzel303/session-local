from typing import List
import mongoengine
from config import config
from tokens_api.db_model import FollowingDoc, UserDoc, StreamKeyDoc

def connect():
	host_url = config.users_db_conn_string

	print(f"Connecting with mongo on: {host_url}")
	mongoengine.connect(host=host_url)

def get_user_by_username(username: str)->UserDoc:
	connect()
	print(f"Quering user with username: {username}")
	return UserDoc.objects(username=username).first()

def get_user_by_tokens_id(id: str)->UserDoc:
	connect()
	print(f"Quering user with token id: {id}")
	return UserDoc.objects(tokens_id=id).first()

def get_key_for_user(user: UserDoc)->StreamKeyDoc:
	connect()
	print(f"Quering stream key for: {user.username}")
	return StreamKeyDoc.objects(owner=user).first()

def save_key(key: StreamKeyDoc)->StreamKeyDoc:
	connect()
	print(f"Saving key for: {key.owner.username}")
	return key.save()

def save_user(user: UserDoc)->UserDoc:
	connect()
	print(f"Saving new user: {user.username}")
	return user.save()

def get_key_by_value(key_value:str)->StreamKeyDoc:
	connect()
	return StreamKeyDoc.objects(value=key_value).first()

def invalidata_key(key: StreamKeyDoc)->StreamKeyDoc:
	connect()
	key.exp_date=None
	return key.save()

def remove_user_by_username(username: str):
	connect()
	user = get_user_by_username(username)
	return user.delete() if user is not None else None

def remove_user(user: UserDoc):
	connect()
	return user.delete()

def remove_follow_rec(user:UserDoc):
	connect()
	return FollowingDoc.objects()

# TODO Page this maybe
def get_following(username: str)->List[FollowingDoc]:
	connect()

	user_doc = get_user_by_username(username)
	if user_doc is None: 
		return None
	
	return FollowingDoc.objects(owner=user_doc.id)