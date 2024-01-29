from dataclasses import dataclass

from shared_model.user import User

# @dataclass
# class User:
# 	pass

class AuthStatus: 
	SUCCESS = 0
	ALREADY_EXISTS = 1
	WRONG_CREDENTIALS = 2
	BAD_REQUEST = 3
	FAILED = 4
	FORBIDDEN = 5

@dataclass
class AuthResponse:
	status: int
	user: User = None
	message: str = ""

	def success(user: User):
		return AuthResponse(status=AuthStatus.SUCCESS, user=user)
	
	def already_exists(msg: str):
		return AuthResponse(status=AuthStatus.ALREADY_EXISTS, message=msg)
	
	def wrong_credentials(msg: str):
		return AuthResponse(status=AuthStatus.WRONG_CREDENTIALS, message=msg)
	
	def bad_request(msg: str):
		return AuthResponse(status=AuthStatus.BAD_REQUEST, message=msg)
	
	def failed(msg: str):
		return AuthResponse(status=AuthStatus.FAILED, message=msg)
	
	def forbidden():
		return AuthResponse(status=AuthStatus.FORBIDDEN)