from dataclasses import dataclass

@dataclass
class UpdateRequest:
	username: str
	title: str
	category: str
	is_public: bool
