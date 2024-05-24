from typing import List
from stream_data import StreamData
from shared_model.update_request import UpdateRequest
from stream_data import StreamData
from stream_category import StreamCategory
from mongoengine import connect, disconnect
from ipaddress import ip_address

from stream_registry.src.media_server_data import MediaServerData
from stream_registry.src.viewer_data import ViewerData

from datetime import datetime, UTC
from app_config import AppConfig

def filter_region_streams(streams, region):
	stream: StreamData

	def region_filter(stream:StreamData):
		return stream.region == region

	for stream in streams:
		stream.media_servers = list(filter(region_filter, stream.media_servers ))
		
	return streams

# TODO refactor this to be just a collection of methods, where each calls
# connect at the beginning.
class Db:

	def __init__(self, conn_string: str):
		connect(host=conn_string)

	def close(self):
		disconnect()
	
	def fetch_analytics(viewer: str):
		return []

	def recommended_sort_pipeline():
		return [{'$match': {}}]

	def views_sort_pipeline():
		return [{'$match': {}}]

	def no_sort_pipeline():
		return [{'$match': {}}]

	def from_stage(ind: int):
		return {'$skip': ind}

	def count_stage(count: int):
		return {'$limit': count}

	def dict_to_data(dict):
		return StreamData(**dict)

	def get_all(self, from_ind, cnt, region, ordering):

		pipeline = []

		if ordering == "Recommended":
			pipeline = Db.recommended_sort_pipeline()
		elif ordering == "Views": 
			pipeline = Db.views_sort_pipeline()
		else: 
			pipeline = Db.no_sort_pipeline()
		
		pipeline.append(Db.from_stage(from_ind))
		pipeline.append(Db.count_stage(cnt))
		

		# datas = StreamData.objects(media_servers__region=region)\
		# 	.skip(from_ind)\
		# 	.limit(cnt)

		return StreamData.objects().aggregate(pipeline)

		# return filter_region_streams(datas, region)

	def get_by_category(self, 
					category: StreamCategory, 
					region: str,
					start: int, 
					count: int) -> List[StreamData]:

		datas = StreamData.objects(category=category, 
							media_servers__region=region)\
					.skip(start)\
					.limit(count)
		return filter_region_streams(datas, region)

	def save_empty(self, creator: str, 
				ingest_ip: str, 
				stream_key: str) -> StreamData:
		
		return StreamData.empty(creator, ingest_ip, stream_key).save()

	def update(self, streamer: str, update_req: UpdateRequest) -> bool:
		
		if not Db.validate_category(update_req.category):
			print(f"Failed to update, stream category invalid: {update_req.category}")
			return False
		
		update_result = StreamData\
			.objects(creator=streamer)\
			.update_one(set__title=update_req.title, 
			   		set__category=update_req.category,
					set__is_public=update_req.is_public)
		

		return update_result > 0

	def validate_category(cat: str):
		cats = AppConfig.get_instance().categories
		return next(filter(lambda c: c.name == cat, cats), None) is not None

	def remove_stream_by_key(self, key:str) -> str: # return the name
		data = StreamData.objects(stream_key=key).first()
		data.delete()

		if data is not None: 
			return data.creator

		return None

	def add_media_server(self, stream_creator: str, 
					quality: str,
					server_ip: str,
					region:str, 
					media_url:str) -> StreamData:
		
		stream = StreamData.objects(creator=stream_creator).first()

		if stream is None:
			print(f"Failed to find stream with creator: {stream_creator} ...")
			return None

		# existing = filter(lambda s: s.ip == int(ip_address(server_ip)), stream.media_servers)

		# if all(s.ip == int(ip_address(server_ip)) for s in stream.media_servers):
		# 	print("Media server already registered.")
		# 	return None
		
		new_server_data = MediaServerData(quality=quality, 
									ip=int(ip_address(server_ip)), 
									region=region, 
									media_url=media_url)

		if new_server_data in stream.media_servers:
			print("Media server already registered.")
			# If None is returned the return code is server error, cdn_instance
			# will keep trying to execute on_publish call. 
			return new_server_data
		

		stream.media_servers.append(new_server_data)
		save_res:StreamData = stream.save()

		return save_res
	
	def remove_media_server(self, stream_creator: str, server_ip: str) -> StreamData:

		stream:StreamData = StreamData.objects(creator=stream_creator).first()
		
		if stream is None:
			# This is normal. When stream is stopped, ingest server will 
			# send stop_stream request which will remove stream completely.
			# Remove media server is issued by the cdn a bit latter, when the 
			# last packet arrives from the ingest.
			print("Failed to find requested stream data.")
			return None

		int_addr = int(ip_address(server_ip))

		# Filter out the instance with ip == int_addr
		stream.media_servers = [ 
						data 
						for data in stream.media_servers 
						if data.ip != int_addr 
					]

		return stream.save()

	def get_stream(self, streamer) -> StreamData:
		return StreamData.objects(creator=streamer).first()
	
	def update_viewer(self, viewer_username: str, stream_name: str) -> ViewerData: 
		view_data = ViewerData.objects(stream=stream_name, viewer=viewer_username).first()

		# view_data can be None if stream doesn't exists (not only if user was
		# not watching it already). This means after the clear_viewers is called
		# it is possible that someone will request update_viewer again and thus
		# create an document, but this should not drastically impact anything
		# since the db is remove those documents anyway after the expire_at.
		if view_data is None: 
			print("No such viewer, will create one.")
			view_data = ViewerData(stream=stream_name, viewer=viewer_username)
		
		
		longevity = AppConfig.get_instance().viewer_longevity
		view_data.expire_at = datetime.now(UTC) + longevity

		return view_data.save()
	
	def clear_viewers(self, stream_name):
		viewers = ViewerData.objects(stream=stream_name)

		print("Viewers: ")
		for v in viewers:
			print(v.to_json())
			v.delete()

	def get_view_count(self, stream_name):
		return ViewerData.objects(stream=stream_name).count()
