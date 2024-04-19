from dataclasses import dataclass


@dataclass
class ContinueViewRequest:
	username: str
	stream_name: str