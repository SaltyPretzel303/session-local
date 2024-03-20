#!/usr/bin/python

from mongoengine import connect
from models import FollowingDoc, UserDoc
from jsonpickle import encode, decode

connect(host="mongodb://session_user:session_pwd@session.com:37017/session_auth")

u = UserDoc.objects(username='streamer-0').first()

f_doc = FollowingDoc.objects(user=u.id).first()
print(f_doc.to_json())
print(f_doc.user.to_json())