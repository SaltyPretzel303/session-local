from dataclasses import dataclass

def AuthRequest(username: str, password:str):
	return {
		username: username, 
		password: password
	}

@dataclass
class AuthRequest:
	username: str
	password: str
