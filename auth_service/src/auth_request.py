from dataclasses import dataclass

@dataclass
class AuthRequest:
	email: str
	password: str