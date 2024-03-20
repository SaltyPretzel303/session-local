from dataclasses import dataclass

@dataclass
class MediaServerRequest:
	content_name: str
	quality: str
	# Quality will be kinda ignored since VBR is resolved between
	# player and cdn instance itself.
	media_server_ip: str
	region: str
	media_url: str

