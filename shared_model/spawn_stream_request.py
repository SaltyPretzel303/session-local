from dataclasses import dataclass


@dataclass
class SpawnStreamRequest():
    creator: str
    title: str
    category: str
