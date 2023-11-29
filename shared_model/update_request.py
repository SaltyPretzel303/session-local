from dataclasses import dataclass

@dataclass
class UpdateRequest:
	title: str
	category: str
	is_public: bool
