#!/usr/bin/python 

from mongoengine import connect
from mongoengine.queryset.visitor import Q
from models import FollowingDoc, UserDoc
from jsonpickle import encode, decode

connect(host="mongodb://localhost:37017/session_auth")

user = 'someusername'
whom = "njuz"

user_d = UserDoc.objects(username=user).first()
whom_d = UserDoc.objects(username=whom).first()

foll_res = FollowingDoc.objects(owner=user_d.id, following=whom_d.id)
print(foll_res)
print(foll_res is not None and len(foll_res) > 0)
