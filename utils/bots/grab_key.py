#!/usr/bin/python 

from tokens_auth import tokens_full_auth, tokens_get_key
from config import get_key_url, remove_user_url, signin_url, signup_url

username = "obsstreamer"
email = 'some@mail.com'
password = 'obsstreamer1'

# key_url = 'http://session.com/auth/get_key'
# remove_at = "http://session.com/user/remove"
# signup_at = "http://session.com/auth/signup"
# signin_at = "http://session.com/auth/signin"

s = tokens_full_auth(username, email, password, remove_user_url, signup_url, signin_url)

if s is not None: 
	key = tokens_get_key(s, get_key_url)
	print(key.value)
else: 
	print("unknown")


