from dataclasses import dataclass

@dataclass
class AuthRequest():
    password: str
    email: str
