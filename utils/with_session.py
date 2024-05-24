import json
import pickle
from requests import Session, post, Response
from jsonpickle import encode, decode, dumps

USERNAME = "streamer"
EMAIL = "some_streamer@mail.com"
PASSWORD = "strong_password"

AUTH_ROUTE = "http://localhost:8003/authenticate"
REGISTER_ROUTE = "http://localhost:8003/register"

COOKIE_PATH = "./cookie"

register_data = {
	"username": "some_user",
	"password": "some_password",
	"email": "some_email@email.com"
}

print("Doing register ... ")

reg_response : Response = post(url=REGISTER_ROUTE, json=register_data) 
	
if reg_response.status_code !=  200:
	print("Registartion failed ...")
	print(f"{reg_response.text}")
	exit(1)
	

s = Session()
try:
	cookie_file = open(COOKIE_PATH, "rb") 
	if not cookie_file.read():
		raise Exception("Cookie file empty ... ")
	
	cookie_file.seek(0)
	s.cookies.update(pickle.load(cookie_file))
	cookie_file.close()
except IOError as err:
	print("Failed to read cookie ... ")
	print(f"Err: {err}")
		
auth_data = {
	"email": register_data["email"],
	"password": register_data["password"]
}

print("Doing authenticate ... ")

auth_response : Response = s.post(url=AUTH_ROUTE, json=auth_data)

if auth_response.status_code != 200:
	print("Failed to authenticate ... ")
	print(f"{auth_response.text}")
	exit(2)

print(f'Session_id: {auth_response.cookies.get("session")}')

try:
	cookie_file = open(COOKIE_PATH, "wb") 
	pickle.dump(auth_response.cookies, cookie_file)
	cookie_file.close()

except IOError as err:
	print("Failed to write cookie ... ")
	print(err)
	exit(3)

# OK now you have a cookie ... 

from dataclasses import dataclass

@dataclass
class UpdateRequest:
	title: str
	category: str
	is_public: bool

d = UpdateRequest("some_stream", "Chatting", True)
txt_d = encode(d, unpicklable=False)

post_res = s.post("http://localhost:8002/update", json=decode(encode(d, unpicklable=False)))
print(post_res)
print(post_res.text)