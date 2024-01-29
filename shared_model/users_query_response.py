from dataclasses import dataclass

from shared_model.user import User

@dataclass 
class UsersQueryResponse:
	for_user: str
	result: [User]
