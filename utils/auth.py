#!/usr/bin/python 

from dataclasses import dataclass
from requests import get, post

# register
# authenticate
# authorize
# refresh_token 

@dataclass 
class Result:
	success: bool
	error: str
	acc_token: str
	rfr_token: str


def get_register_data(username, password, email):
	return {
		'username': username,
		'password': password,
		'email': email
	}

def register(reg_data) -> Result:



	return 