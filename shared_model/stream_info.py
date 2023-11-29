from dataclasses import dataclass


@dataclass
class StreamInfo:
    title: str
    creator: str
    category: str
    ingest_ip: str
    media_servers: [str]
    is_public: bool
