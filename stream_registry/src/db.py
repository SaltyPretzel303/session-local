# from typing import dict
from typing import List
from stream_data import StreamData
from shared_model.update_request import UpdateRequest
from stream_data import StreamData
from stream_category import StreamCategory
from mongoengine import connect, disconnect
from ipaddress import ip_address

class Db:

	def __init__(self, conn_string: str):
		connect(host=conn_string)

	def close(self):
		disconnect()

	def get_by_creator(self, creator: str) -> StreamData:
		return StreamData.objects(creator=creator).first()

	def get_by_category(self, cat: StreamCategory, start: int, end: int) -> List[StreamData]:
		return StreamData.objects(category=cat)

	def save_empty(self, creator: str, ingest_ip: str, stream_key: str) -> StreamData:
		return StreamData.empty(creator, ingest_ip, stream_key).save()

	def update(self, streamer: str, update_req: UpdateRequest) -> StreamData:
		data = StreamData.objects(creator=streamer).first()
		if data is None:
			print(f"Such stream not found: {streamer}")
			return None

		data.update(update_req.title, update_req.category, update_req.is_public)
		return data.save() # is save required here ... ?
			
	def remove_stream(self, key:str):
		return StreamData.objects(stream_key=key).first().delete()

	def add_media_server(self, stream_creator: str, server_ip: str) -> StreamData:
		stream:StreamData = StreamData.objects(creator=stream_creator).first()

		if stream is None:
			print(f"Failed to find stream with creator: {stream_creator} ...")
			return None
		
		stream.media_servers.append(int(ip_address(server_ip)))
		save_res:StreamData = stream.save()

		return save_res
	
	def remove_media_server(self, stream_creator: str, server_ip: str) -> StreamData:

		stream:StreamData = StreamData.objects(creator=stream_creator).first()
		
		if stream is None:
			print("Failed to find requested stream data ... ")
			return None

		int_addr = int(ip_address(server_ip))

		if int_addr in stream.media_servers:
			stream.media_servers.remove(int_addr)

		return stream.save()

	def get_stream(self, streamer) -> StreamData:
		return StreamData.objects(creator=streamer).first()

	def get_all(self, from_page, page_cnt):
		return StreamData.objects().skip(from_page).limit(page_cnt)