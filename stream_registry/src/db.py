# from typing import dict
from shared_model.stream_info import StreamInfo
from stream_data import StreamData
from stream_category import StreamCategory
from mongoengine import connect, disconnect, Document

import jsonpickle


class Db:

    def __init__(self, conn_string: str):
        connect(host=conn_string)

    def close(self):
        disconnect()

    def to_obj(doc: Document) -> StreamInfo:
        # m_doc = doc.to_mongo()
        # del m_doc["_id"]
        return doc.to_stream_info()
        # return StreamInfo(**doc)

    def get_by_creator(self, creator: str) -> StreamInfo:
        data = StreamData.objects(creator=creator).first()

        if data is not None:
            data = Db.to_obj(data)

        return data

    def get_by_category(self, cat: StreamCategory, start: int, end: int) -> [StreamInfo]:
        data = StreamData.objects(category=cat)

        if data is not None:
            data = list(map(lambda d: Db.to_obj(d), data))

        return data

    def save(self, info: StreamInfo):
        res = StreamData.from_stream_info(info).save()
        if res is not None:
            return Db.to_obj(res)
            # return res

        return None
