from dataclasses import dataclass


@dataclass
class StreamInfo:
    title: str
    creator: str
    category: str
    stream_id: str
    ingest_ip: str
    media_servers: [str]
