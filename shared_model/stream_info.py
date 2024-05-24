from dataclasses import dataclass
from typing import List

from shared_model.media_server_info import MediaServerInfo

@dataclass
class StreamInfo:
    title: str
    creator: str
    category: str
    media_servers: List[MediaServerInfo]
    