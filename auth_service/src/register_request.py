from dataclasses import dataclass

@dataclass
class RegisterRequest():
    username: str
    password: str
    email: str
