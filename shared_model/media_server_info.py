from dataclasses import dataclass

@dataclass
class MediaServerInfo:
	ip: str
	port: int
	media_path: str
	full_path: str
