from dataclasses import dataclass


class KeyStatus:
	SUCCESS = 0
	FAILED = 1


@dataclass
class KeyResponse:
	status: int
	message: str = ""
	value: str = ""
	exp_data: str = ""
	

