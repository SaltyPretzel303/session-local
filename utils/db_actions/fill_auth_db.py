#!/usr/bin/python 

from models import User, FollowRecord, hash_pwd
from mongoengine import connect, disconnect

USERS_CNT = int(12)

connect(host="mongodb://localhost:37017/session_auth")

def gen_user(ind: int):
	return User(username=f"user_{ind}", email=f"email_{ind}@ses.com")

print("Inserting users: ")

users = [gen_user(i) for i in range(0, USERS_CNT)]

for u in users:
	print(f"\tIn: {u.username}")
	u.save()

print("")

print("Inserting follow records: ")
cnt = int(USERS_CNT/3)
for ind in range(0,cnt):
	user = users[ind]
	from_foll = cnt + 1
	to_foll = from_foll + ind + 1
	following = users[from_foll:to_foll]
	rec = FollowRecord(user=user, following=following)
	rec.save()

	print(f"\tUser: {user.username}")
	for f in following: 
		print(f"\t\t following: {f.username}")
	

disconnect()