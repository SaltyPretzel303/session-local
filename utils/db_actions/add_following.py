#!/usr/bin/python 

from argparse import ArgumentParser
from mongoengine import connect
from models import UserDoc, FollowingDoc
from datetime import datetime as dt
import bots.tokens_auth as auth

parser = ArgumentParser()
parser.add_argument("--user", action='store', required=True)
parser.add_argument("--count", action='store', default=3)

args = parser.parse_args()

for i in range(1,10):
	auth.tokens_remove_user(f"user-{i}","http://session.com/user/remove")
	auth.tokens_signup(f"user-{i}",f"mail-{i}@s.com", f"very_longpwd{i}", "http://session.com/auth/signup")

# connect(host="mongodb://session_user:session_pwd@users-db.session.com:37017/session_auth")
connect(host="mongodb://session_user:session_pwd@session.com:37017/session_auth")

user_data = UserDoc.objects(username=args.user).first()
if user_data is None: 
	print(f"No such user: {args.user}")
	exit(1)

others = UserDoc.objects(username__ne=args.user).limit(args.count)
print(f"Adding {others.count()} to following record.")

for other in others: 
	f_doc = FollowingDoc(owner=user_data, 
					following=other, 
					followed_at=dt.now())
	f_doc.save()