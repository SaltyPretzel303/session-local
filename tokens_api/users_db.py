from typing import List
import mongoengine
from config import config
from tokens_api.db_model import FollowingDoc, UserDoc, StreamKeyDoc
from datetime import datetime as dt

def connect():
	host_url = config.users_db_conn_string

	mongoengine.connect(host=host_url)

# Why are all of these synchronous. ... ... .... ... ... ... ... .

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

def remove_follow_rec_for(user:UserDoc):
	connect()
	return FollowingDoc.objects(owner=user.id).delete()

def get_following(username: str)->List[FollowingDoc]:

	connect()

	user_doc = get_user_by_username(username)
	if user_doc is None: 
		return None
	
	return FollowingDoc.objects(owner=user_doc.id)

def is_following(user_tokens_id: str, followed:str)->bool:
	connect()

	user = get_user_by_tokens_id(user_tokens_id)
	if user is None: 
		return False
	
	followed_user = get_user_by_username(followed)
	if followed_user is None: 
		return

	follow_doc = FollowingDoc.objects(owner=user.id, following=followed_user.id)

	return  follow_doc is not None and len(follow_doc)>0

def follow(user_tokens_id: str, channel: str)->FollowingDoc: 
	user = get_user_by_tokens_id(user_tokens_id)
	f_channel = get_user_by_username(channel)

	record = FollowingDoc(owner=user, following=f_channel, followed_at=dt.now())
	return record.save()

def unfollow(user_tokens_id: str, channel: str)->FollowingDoc: 
	user = get_user_by_tokens_id(user_tokens_id)
	f_channel = get_user_by_username(channel)

	return FollowingDoc.objects(owner=user.id, following=f_channel.id).delete()