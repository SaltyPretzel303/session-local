#!/usr/bin/python 

from tokens_auth import tokens_full_auth, tokens_get_key

username = "obs_streamer"
email = 'obs@streamer.com'
password = 'obsstreamer1'

key_url = 'http://session.com/auth/get_key'
remove_at = "http://session.com/user/remove"
signup_at = "http://session.com/auth/signup"
signin_at = "http://session.com/auth/signin"

s = tokens_full_auth(username, email, password, remove_at, signup_at, signin_at)

if s is not None: 
	key = tokens_get_key(s, key_url)
	print(key.value)
else: 
	print("unknown")


