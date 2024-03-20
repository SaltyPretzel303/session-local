#!/usr/bin/python 

from models import UserDoc, FollowingDoc, StreamKeyDoc

from mongoengine import connect, disconnect

connect(host="mongodb://localhost:37017/session_auth")

print("Clearing follow records.")
for rec in FollowingDoc.objects():
	rec.delete()

print("Clearing stream keys.")
for key in StreamKeyDoc.objects():
	print(f"\tKey: {key.value}")
	key.delete()

print("Clearing users.")
for user in UserDoc.objects():
	print(f"\tUser: {user.username}")
	user.delete()

disconnect()
