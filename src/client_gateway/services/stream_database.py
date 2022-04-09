from data.stream_info import StreamInfo


class StreamDatabase():

    def __init__(self):
        self.current_streams = [
            StreamInfo("stream_1", "author_1", "author_id_1", "stream_1_id"),
            StreamInfo("stream_2", "author_2", "author_id_2", "stream_2_id"),
            StreamInfo("stream_3", "author_3", "author_id_3", "stream_3_id"),
            StreamInfo("stream_4", "author_4", "author_id_4", "stream_4_id")
        ]

    def list_streams(self):
        return self.current_streams

    def add_stream(self, stream_name, author_name, author_id, stream_id):
        new_stream = StreamInfo(stream_name, author_name, author_id, stream_id)
        self.current_streams.__add__(new_stream)

    def remove_stream(self, stream_id):
        self.current_streams.remove(
            lambda stream: stream.stream_id == stream_id)

    def clear_streams(self):
        self.current_streams.clear()
