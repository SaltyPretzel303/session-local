from dataclasses import dataclass

@dataclass
class StreamKey:
	value: str
	exp_data: str
	owner_username: str # username
