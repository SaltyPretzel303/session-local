from dataclasses import dataclass

class AuthStatus: 
	SUCCESS = 0
	ALREADY_EXISTS = 1
	WRONG_CREDENTIALS = 2
	BAD_REQUEST = 3
	FAILED = 4

@dataclass
class AuthResponse:
	status: int
	message: str = ""
	username: str = ""
	email: str = ""