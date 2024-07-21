#!/usr/bin/python 

from tokens_auth import tokens_full_auth, tokens_get_key
from config import get_key_url, remove_user_url, signin_url, signup_url

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--name", action='store', default='obsstreamer')
parser.add_argument("--email", action='store', default='obs@gmail.com')
parser.add_argument("--password", action='store', default='defaultpwd1')
args = parser.parse_args()

s = tokens_full_auth(args.name, args.email, args.password, 
					remove_user_url, signup_url, signin_url)

if s is not None: 
	key = tokens_get_key(s, get_key_url)
	print(key.value)
else: 
	print("unknown")


