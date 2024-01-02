# from typing import dict
from shared_model.stream_info import StreamInfo
from shared_model.update_request import UpdateRequest
from stream_data import StreamData
from stream_category import StreamCategory
from mongoengine import connect, disconnect
from jsonpickle import encode

class Db:

	def __init__(self, conn_string: str):
		connect(host=conn_string)

	def close(self):
		disconnect()

	def to_obj(doc: StreamData) -> StreamInfo:
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

	def save_empty(self, creator: str, ingest_ip: str, stream_key: str):
		res = StreamData.empty(creator, ingest_ip, stream_key).save()
		if res is not None:
			return Db.to_obj(res)
		
		return None

	def update(self, streamer: str, update_req: UpdateRequest):
		data = StreamData.objects(creator=streamer).first()
		if data is None:
			print(f"Such stream not found: {streamer}")
			return None

		data.update(update_req.title, 
					update_req.category, 
					update_req.is_public)
		save_res = data.save()

		if save_res is None:
			print("Failed to save updated data ... ")
			return None
		
		return Db.to_obj(save_res)
			
	def remove_stream(self, key:str):
		print(f"Removing stream with the key: {key}")

		query_res = StreamData.objects(stream_key=key)


		return query_res.first().delete()



