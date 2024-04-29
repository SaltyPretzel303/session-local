
from dataclasses import dataclass
from requests import Session, get, post
from jsonpickle import encode

def jsonify(obj):
	return encode(obj, unpicklable=False, indent=4)

def form_remove_url(base: str, username: str):
	return f"{base}/{username}"

def tokens_remove_user(username: str, url: str)->bool:
	try:
		res = get(form_remove_url(url, username))
		
		if res is None:
			raise Exception(f"Remove response is None.")

		if res.status_code != 200 and res.status_code != 404:
			raise Exception(f"Non success code: {res.status_code}")
		
		return True

	except Exception as e:
		print(f"Failed to remove user: {e}.")
		return False

def get_signup_data(username, email, password):
	return {
		"formFields": 
			[
				{
					"id": "email",
					"value": email
				},
				{
					"id": "password",
					"value": password
				},
				{
					"id": "username",
					"value": username
				}
			]
	}

def get_signup_header():
	return {'rid': 'emailpassword'}

def tokens_signup(username, email, password, url)->bool:
	signup_res = None
	try:
		signup_res = post(url=url,
					headers=get_signup_header(),
					json=get_signup_data(username=username,
						  			email=email,
									password=password))
		
		if signup_res is None: 
			raise Exception("Signup result is None.")
		
		if signup_res.status_code != 200:
			raise Exception(f"Signup result code is: {signup_res.status_code}.")

	except Exception as e:
		print(f"Error in signup: {e}")
		return False
	
	return True

def get_signin_data(email, password):
	return {
		"formFields": 
			[
				{
					"id": "email",
					"value": email
				},
				{
					"id": "password",
					"value": password
				}
			]
	}

def get_signin_header():
	# https://app.swaggerhub.com/apis/supertokens/FDI/1.18.0#/EmailPassword%20Recipe/signIn
	# According to ^ rid should be session but it doesn't work.
	# Experimentally proven that emailpassword works.
	# return {'rid': 'session'}
	return {
		# 'origin': 'session.com',
		'rid': 'emailpassword',
		'st-auth-mode': 'cookie',
	} 

def tokens_signin(email, password, url)->Session:
	s = Session()
	signin_res = None
	try:
		signin_res = s.post(url=url,
					headers=get_signin_header(),
					json=get_signin_data(email, password))
		
		if signin_res is None: 
			raise Exception("Singin result in None.")
		
		if signin_res.status_code != 200:
			raise Exception(f"Signin result code is: {signin_res.status_code}")
		
		tokens_status = signin_res.json().get('status')
		if tokens_status != "OK":
			raise Exception(f"Tokens status not ok: {tokens_status}")

	except Exception as e:
		print(f"Exception in signin: {e}")
		return None

	return s

@dataclass
class StreamKey:
	value: str
	exp_date: str

	def from_resp(key_data)->"StreamKey":
		return StreamKey(value=key_data.get('value'), 
				exp_date=key_data.get("exp_date"))

def tokens_get_key(s: Session, url: str)->StreamKey:
	if s is None: 
		print("Requesting key without authentication.")
		s = Session()

	key_res = None
	try:
		key_res = s.get(url=url
				#   headers={'origin': 'session.com'}
				  )

		if key_res is None: 
			raise Exception("Key response is None.")
		
		if key_res.status_code != 200:
			raise Exception(f"Status code is not 200: {key_res.status_code}")

		key_data = key_res.json()
		if key_data is None: 
			raise Exception("Key data invalid or None.")
		
		data_status = key_data.get('status')
		if data_status != 0:
			raise Exception(f"Key error: {key_data.get('message')}")

		return StreamKey.from_resp(key_data)

	except Exception as e:
		print(f"Error in key request: {e}")
		return None
	

def tokens_full_auth(username, email, password, remove_at, signup_at, signin_at):
	
	tokens_remove_user(username, remove_at)

	signup_res = tokens_signup(username, email, password, signup_at)
	if not signup_res:
		return None
	
	return tokens_signin(email, password, signin_at)


