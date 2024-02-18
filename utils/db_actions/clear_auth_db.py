#!/usr/bin/python 

from models import User, FollowRecord, StreamKeyDoc

from mongoengine import connect, disconnect

connect(host="mongodb://localhost:37017/session_auth")

print("Clearing follow records.")
for rec in FollowRecord.objects():
	print(f"\tRecord: {rec.user.username}")
	rec.delete()

print("Clearing stream keys.")
for key in StreamKeyDoc.objects():
	print(f"\tKey: {key.value}")
	key.delete()

print("Clearing users.")
for user in User.objects():
	print(f"\tUser: {user.username}")
	user.delete()



disconnect()
