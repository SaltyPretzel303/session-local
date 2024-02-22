from dataclasses import dataclass


class KeyStatus:
	SUCCESS = 0
	FAILED = 1


@dataclass
class KeyResponse:
	status: int
	message: str = ""
	value: str = ""
	exp_date: str = ""

	def success(value: str, expiration_date: str = None):
		return KeyResponse(status=KeyStatus.SUCCESS, 
					value=value, 
					exp_date=expiration_date)
	
	def failure(message: str):
		return KeyResponse(status=KeyStatus.FAILED, message=message)

