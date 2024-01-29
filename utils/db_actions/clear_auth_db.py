#!/usr/bin/python 

from models import User, FollowRecord

from mongoengine import connect, disconnect

connect(host="mongodb://localhost:27018/session_auth")

print("Clearing follow records.")
for rec in FollowRecord.objects():
	print(f"\tRecord: {rec.user.username}")
	rec.delete()


print("Clearing users.")
for user in User.objects():
	print(f"\tUser: {user.username}")
	user.delete()


disconnect()
