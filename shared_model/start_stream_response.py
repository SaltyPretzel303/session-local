from dataclasses import dataclass
from shared_model.stream_info import StreamInfo


class ResponseStatus:
    STARTED = 'Started'
    ALREADY_STREAMING = 'AlreadyStreaming'
    ERROR = 'Error'


@dataclass
class StartStreamResponse:
    status: str
    data: StreamInfo
