from mongoengine import Document, StringField, ListField, LongField
from shared_model.stream_info import StreamInfo
from ipaddress import ip_address


class StreamData(Document):
    title = StringField(required=True, max_length=120)
    creator = StringField(required=True, max_length=20)
    category = StringField(required=True, max_length=40)

    stream_id = StringField(required=True, max_length=15)
    ingest_ip = LongField(required=True)
    media_servers = ListField(LongField())
    # ip is stored as an number in order to allow queries on it

    def to_stream_info(self) -> StreamInfo:
        return StreamInfo(self.title,
                          self.creator,
                          self.category,
                          self.stream_id,
                          str(ip_address(self.ingest_ip)),
                          list(map(lambda num: str(ip_address(num)), self.media_servers)))

    @staticmethod
    def from_stream_info(info: StreamInfo):
        return StreamData(
            title=info.title,
            creator=info.creator,
            category=info.category,
            stream_id=info.stream_id,
            # ^ where do i get this one from ... currently just the container ip
            # which is wrong since since container should represent ingest for
            # multiple streams ...
            ingest_ip=int(ip_address(info.ingest_ip)),
            media_servers=(
                list(map(lambda ip: int(ip_address(ip)), info.media_servers)))
        )
