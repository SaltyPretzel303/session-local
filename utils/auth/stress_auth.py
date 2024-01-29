#!/usr/bin/python 

from requests import Response, get, post

def gen_user(ind: int):
	return {
		'username': f"user_{ind}",
		'password': f"pwd_{ind}"
	}

AUTH_URL = 'http://localhost:8003/authenticate'
GET_KEY_URL = 'http://localhost:8003/get_key'
MATCH_KEY_URL = 'http://localhost:8003/match_key'
GET_FOLLOWING = 'http://localhost:8003/get_following'

def do_auth(req_data):
	print(f"Trying with: {req_data.get('username')}")
	res:Response = post(url=AUTH_URL,json=req_data)
	if not res.ok:
		print(f"Failed with: {req_data['username']}")
		return

	session_id = res.cookies.get('session')
	print(f"AuthSuccess s: {session_id}")

	print("Getting key.")
	key_res: Response = get(url=GET_KEY_URL, cookies={'session':session_id})
	if not key_res.ok:
		print("Failed.")
	
	key = key_res.json().get('value')
	print(f"Get Success k: {key_res}")

	print(f"Matching key.")
	match_res:Response = get(url=f"{MATCH_KEY_URL}/{key}", cookies = {'session': session_id})
	if not match_res.ok:
		print("Failed to match key.")

	streamer = match_res.json().get('value')
	print(f"Matched key: {streamer}")

	print("Getting followers.")
	foll_res:Response = get(url=f"{GET_FOLLOWING}/{streamer}", cookies = {'session': session_id})
	if not foll_res: 
		print("Failed to get following.")

	print("Got following. ")
	for u in foll_res.json().get("result"):
		print(u)
	# print(foll_res.json())
	
	print("===")

for ind in range(0, 10):
	user = gen_user(ind)
	do_auth(user)
