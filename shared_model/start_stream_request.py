from dataclasses import dataclass


@dataclass
class StartStreamRequest:
    title: str
    creator: str
    category: str
