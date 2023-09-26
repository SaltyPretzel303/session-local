# from enum import Enum
from dataclasses import dataclass

class ResponseStatus:
    SUCCESS = 'Success'
    ERROR = 'Error'


@dataclass
class IngestResponse():
    # def __init__(self, status: ResponseStatus, ip: str, port: int, stream_key: str):
    # print(f"ingestresponsestatus: {status}")
    status: str
    ip: str
    port: int
    stream_key: str
