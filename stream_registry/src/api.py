import asyncio
import os
from typing import List

from fastapi import FastAPI, HTTPException, Response, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
# from starlette.responses import FileResponse
import uvicorn

from datetime import datetime, timedelta

from requests import get
from httpx import AsyncClient, Response as HttpxResp

from shared_model.continue_view_request import ContinueViewRequest
from shared_model.following_info import FollowingInfo
from shared_model.media_server_request import MediaServerRequest
from shared_model.media_server_info import MediaServerInfo
from shared_model.stream_info import StreamInfo
from shared_model.update_request import UpdateRequest
from shared_model.category import Category as PublicCategory

from shared_model.user import User
from stream_registry.src.db import Db

from stream_registry.src.app_config import AppConfig, DOMAIN_NAME
from stream_registry.src.app_config import Category as ConfCategory
from stream_registry.src.media_server_data import MediaServerData
from stream_registry.src.stream_data import StreamData

JSON_CONTENT_TYPE = 'application/json'

app = FastAPI()
app.add_middleware(CORSMiddleware, 
				   allow_origins=[f'http://{DOMAIN_NAME}'], 
				   allow_credentials=True, 
				   allow_headers=['rid', 'st-auth-mode'])


TNAIL_LONGEVITY = 120 # 120s 
tnails = {}

def jsonify(content) -> str:
	return jsonable_encoder(content)

def get_db() -> Db:
	return Db(AppConfig.get_instance().db_url)

def media_server_dict_to_info(data):
	return MediaServerInfo(quality=data['quality'], access_url=data['media_url'])

def stream_dict_to_info(data) -> StreamInfo:
	servers = list(map(media_server_dict_to_info, data['media_servers']))
	return StreamInfo(title=data['title'],
				   creator=data['creator'],
				   category=data['category'],
				   media_servers=servers)

def stream_data_to_info(data:StreamData)->StreamInfo:
	servers = list(map(media_server_data_to_info, data.media_servers))
	return StreamInfo(title=data.title,
				creator=data.creator,
				category=data.category,
				media_servers=servers)

def media_server_data_to_info(data: MediaServerData)->MediaServerInfo:
	return MediaServerInfo(quality=data.quality, access_url=data.media_url)

@app.get("/ping")
def ping():
	return "pong"

# This is used by the ingest instance so therefore
# request.ip should be the ingest instance's ip.
@app.post("/start_stream")
async def start_stream(request: Request):
	print("Processing start stream request.")
	
	args = url_decode((await request.body()).decode())
	key = args.get("name")
	proxy_ip = args.get("addr") # this is gonna be the ip of nginx reverse proxy 
	ingest_ip = request.client.host

	print(f"StreamKey: {key} from: {ingest_ip}")

	try:
		print(f"Requesting key match for: {key}.")
		match_res = get(AppConfig.get_instance().match_key_url(key))

		if match_res is None: 
			raise Exception("Match key response is None.")

		if match_res.status_code != 200:
			raise Exception(f"Match key status code: {match_res.status_code}")
		
		match_data = match_res.json()

		print(f"Key successfully matched to: {match_data['value']}")

		print("Saving stream info skeleton.")
		db_res = get_db().save_empty(match_data["value"], ingest_ip, key)
		if db_res is None:
			raise HTTPException(status_code=500)
			# return  Response(content="Failure.", 
			# 		   status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
		print("Stream saved.")

		# response.headers["Location"] = match_data["value"]

		return Response(status_code=status.HTTP_302_FOUND, 
				headers={'Location': match_data['value']})

	except Exception as e:
		print(f"Failed to match key: {key}, reason: {e}")
		raise HTTPException(status_code=500)
		return Response(content="Failure.", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/add_media_server")
async def add_media_server(server_data: MediaServerRequest):
	print("Processing add media server request.")

	print(f"Media server:{server_data.media_server_ip} to:{server_data.content_name}")

	add_res = get_db().add_media_server(server_data.content_name, 
								server_data.quality,
								server_data.media_server_ip,
								server_data.region,
								server_data.media_url)

	if add_res is None:
		raise HTTPException(status_code=500, detail='Failed to add media server.')
		return Response("Failed to add media server.", 
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
	else:
		return Response("Success.")

@app.post("/remove_media_server")
async def remove_media_server(remove_req: MediaServerRequest):
	print("Processing remove media server request.")

	print(f"mediaIp: {remove_req.media_server_ip} content: {remove_req.content_name}")

	get_db().remove_media_server(remove_req.content_name, remove_req.media_server_ip)

	return Response("Success.")

@app.post('/update')
async def update(update_data: UpdateRequest, request: Request):
	print("Processing update stream request.")

	if await getUser(request.cookies) is None: 
		raise HTTPException(status_code=401, detail='Authorization failed.')
	
	print("User authorized.")

	update_success = get_db().update(update_data.username, update_data)

	if update_success:
		return "Stream updated."
	else: 
		raise HTTPException(status_code=500, detail='Failed to update stream.')

async def getUser(cookies) -> User:
	async with AsyncClient() as client: 
		auth_url = AppConfig.get_instance().is_authenticated_url
		auth_res: HttpxResp = await client.get(url=auth_url, cookies=cookies)

		if auth_res is None or auth_res.status_code != 200: 
			return None

		return User(**auth_res.json())

@app.post("/continue_view")
async def add_viewer(view_request: ContinueViewRequest):

	print("Processing continue view request.")
	print(f"User: {view_request.username}, stream:{view_request.stream_name}")
	

	result = get_db().update_viewer(viewer_username=view_request.username, 
						stream_name=view_request.stream_name)
	if result is None: 
		print("Failed to update viewer.")
		raise HTTPException(status_code=500)
		return "Failed to update viewer.", status.HTTP_500_INTERNAL_SERVER_ERROR

	return "Viewer updated."

@app.get('/viewer_count/{streamer}')
async def get_viewer_count(streamer: str):
	count = get_db().get_view_count(streamer)
	print(f"Found count: {count}")

	return count

@app.get("/all")
def get_all(region:str="eu", start:int=0, count:int=4, ordering: str = 'None'):
	print("Processing get all streams request.")
	print(f"Ordering: {ordering}")
	streams_data = get_db().get_all(start, count, region, ordering)

	if streams_data is None: 
		print("Failed to obtain requested streams.")
		return "Failed.", status.HTTP_500_INTERNAL_SERVER_ERROR

	return list(map(stream_dict_to_info, streams_data))
	# return list(map(stream_data_to_info, streams_data))

@app.get("/stream_query/{name_query}")
def get_by_query(name_query: str, 
			region:str="eu", 
			start:int=0, count:int=4):
	
	print(f"Processing get by query request: {name_query}")
	streams = get_db().get_by_query(name_query, region , start, count)
	
	as_objs = list(map(stream_dict_to_info, streams))

	return as_objs

@app.get("/by_category/{category}")
def get_by_category(category: str, 
					region: str='eu', 
					start: int = 0, 
					count:int=3,
					ordering: str = 'None' ):
	print(f"Processing get by category request for: {category}")
	print(f"Ordering: {ordering}")

	streams_data = get_db().get_by_category(category, region, start, count)
	if streams_data is None:
		raise HTTPException(status_code=404)
	
	return list(map(stream_data_to_info, streams_data))

@app.get("/stream_info/{streamer}")
async def get_stream_info(request: Request, streamer: str, region:str = 'eu'):
	print(f"Processing get stream info request for: {streamer} in: {region}")

	stream_data:StreamData = get_db().get_stream(streamer)

	if stream_data is None:
		raise HTTPException(status_code=404, detail='No such stream..')

	user = await getUser(request.cookies)

	if not stream_data.is_public and (user is None or user.username != streamer):
		print("This is not public stream ... ")
		raise HTTPException(status_code=404, detail='No such stream.')
	
	return JSONResponse(jsonify(stream_data_to_info(stream_data)))

@app.get("/get_following")
async def get_following(request: Request,
						start:int=0, 
						count:int=4, 
						ordering: str = 'None') -> List[StreamInfo]:
	
	print("Processing get following streams request. ")

	config = AppConfig.get_instance()
	following_data: List[FollowingInfo] = []
	try: 
		followed_res = get(config.followingUrl, cookies=request.cookies)
		if followed_res is None:
			raise Exception("Request failed.")
		
		if followed_res.status_code != 200:
			raise Exception(followed_res.text)

		following_data = followed_res.json()

	except Exception as e:
		print(f"Failed to obtain followed channels: {e}")
		raise HTTPException(status_code=followed_res.status_code, 
					detail='Failed to obtain followed channels.')

	return following_data
	return map(lambda f: f.following, following_data)

@app.get("/get_recommended/{username}")
def get_recommended(username: str):
	print("GET RECOMMENDED NOT IMPLEMENTED")
	raise HTTPException(status_code=501)
	return jsonify([]), status.HTTP_501_NOT_IMPLEMENTED

@app.get("/get_explore")
def get_explore(region: str="eu", start:int=0, count:int=2):
	print("GET EXPLORE NOT IMPLEMENTED")
	# raise HTTPException(status_code=501)
	return jsonify([])

@app.get("/tnail/{streamer}")
async def get_tnail(request: Request, streamer: str='unavailable'):
	print(f"Requested tnail for: {streamer}.")

	config = AppConfig.get_instance()

	if streamer == 'unavailable':
		print("Requested static unavailable thumbnail.")
		raise HTTPException(status_code=400, detail='Stream name not provided.') # bad request

	if not is_live(streamer):
		raise HTTPException(status_code=404, detail='Stream is not live.') 
	
	if streamer not in tnails or is_expired(tnails[streamer]):
		print("Thumbnail expired, will generate new.")

		tnail_path = config.tnail_path(streamer)
		gen_result = await generate_thumbnail(streamer, tnail_path)

		if not gen_result:
			print(f"Failed to generate thumbnail for: {streamer}.")
			raise HTTPException(status_code=500) 

		exp_date = datetime.now() + timedelta(seconds=TNAIL_LONGEVITY)
		tnails[streamer] = exp_date
		print(f"Tnail generated, will expire at: {exp_date}.")

	if not os.path.exists(config.tnail_path(streamer)):
		print(f"Failed to generate tnail at: {config.tnail_path(streamer)}")
		raise HTTPException(status_code=500) 

	print(f"Returning tnail for {streamer}.")
	return FileResponse(path=config.tnail_path(streamer), media_type="image/jpg")

@app.get("/is_live/{streamer}")
async def is_live_request(streamer: str):
	print(f"Processing is live request for: {streamer}")
	return is_live(streamer)


# @app.middleware("http")
# async def header_print(request:Request, call_next):
# 	print("In middleware.")
# 	print(request.headers)

# 	return await call_next(request)

# Default end index is 200 so that all categories are fetched (with the
# assumption there is not more than 200) if indices are not specified
@app.get("/categories")
async def get_categories(start:int=0, end:int=200):
	cats: List[ConfCategory] =  AppConfig.get_instance().categories[start:end]
	return list(map(to_public_cat, cats))

def to_public_cat(cat: ConfCategory):
	return PublicCategory(name=cat.name, display_name=cat.displayName)

@app.get("/category_low_tnail/{category}")
async def get_category_low_tnail(category: str):
	cat:ConfCategory = next(filter(lambda c: c.name==category, 
							AppConfig.get_instance().categories), 
						None)
	
	if cat is None: 
		raise HTTPException(status_code=404)

	if not os.path.exists(cat.low_icon_path):
		print(f"Failed to server low icon from: {cat.low_icon_path}")
		raise HTTPException(status_code=500)

	ext = get_extension(cat.low_icon_path)

	return FileResponse(path=cat.low_icon_path, media_type=f"image/{ext}")

@app.get("/category_high_tnail/{category}")
async def get_category_high_tnail(category: str):
	cat:ConfCategory = next(filter(lambda c: c.name==category, 
							AppConfig.get_instance().categories), 
						None)
	
	if cat is None: 
		raise HTTPException(status_code=404)

	if not os.path.exists(cat.high_icon_path):
		print(f"Failed to server high icon from: {cat.high_icon_path}")
		raise HTTPException(status_code=500)

	ext = get_extension(cat.high_icon_path)

	return FileResponse(path=cat.high_icon_path, media_type=f"image/{ext}")

def get_extension(file: str):
	return file.split('.')[1]

def flatten_cookies(cookies):
	return f"Cookie: sAccessToken={cookies['sAccessToken']}"
	return ",".join([f"{key}:{cookies[key]}" for key in cookies])

def is_expired(expiration_date: datetime):
	return expiration_date is None or datetime.now() > expiration_date

async def generate_thumbnail(streamer, path):
	print(f"Generate tnail for: {streamer} at: {path}")
	stream_data:StreamData = get_db().get_stream(streamer)

	found_valid = False
	preview_servers= filter(preview_quality_filter, stream_data.media_servers)
	# servers = iter(stream_data.media_servers)

	while (server:=next(preview_servers, None)) and not found_valid: 
		try:
			print(f"Pulling from: {server.media_url}")
			proc = await asyncio.create_subprocess_exec(
				"ffmpeg",
				# Replace SessionOrigin field with some secret, or somehow
				# authenticate registry service.
				# "-headers", "sessionorigin: streamregistry", 
				"-i",
				server.media_url,
				"-vframes", "1",
				'-update', '1',
				path,
				"-y",
				stdout=asyncio.subprocess.PIPE,
				stderr=asyncio.subprocess.PIPE)
			
			ret_code = await proc.wait()
			print(f"Pull return code: {ret_code}")

			# log, err = await proc.communicate()

			# if log is not None:
			# 	print(f"Log: {log.decode()}")

			# if err is not None: 
			# 	print(f"Err: {err.decode()}")
			
			# For some reason I am getting 'muxing overhead: unknown' error 
			# but thumbnail is susscessfully generated.
			# Ignore it I guess ... 

		except Exception as err: 
			print(f"Error while generating tnail: {err}")
			return False

	return True

def preview_quality_filter(server:MediaServerData):
	return server.quality == 'preview'

def is_live(streamer: str):
	return get_db().get_stream(streamer) is not None

# mockup data
def gen_stream_info(ind: int):
	return StreamInfo(f"title_{ind}", 
			f"creator_{ind}", 
			f"chatting",
			MediaServerInfo("127.0.0.1", 10000, "live","http://localhost:10000/live/streamer_subsd/index.m3u8") )


# Data MUST be str, not byte or byte[] !!!
# To translate byte/byte[] to string use .decode() method. 
def url_decode(data:str):
	return { pair.split("=")[0]:pair.split("=")[1]  for pair in data.split("&")}

@app.post("/stop_stream")
async def stop_stream(request: Request):
	args = url_decode((await request.body()).decode())
	stream_key = args['name']

	print(f"Removing stream with the key: {stream_key}")
	stream_name = get_db().remove_stream_by_key(stream_key)

	if stream_name is not None: 
		print(f"Clearing viewers for: {stream_name}")
		get_db().clear_viewers(stream_name)	
	else: 
		print("Stream name was not resolved, db will eventually clear viewers.")
	
	return Response(f"Stream {stream_key} removed.")

# if __name__ == '__main__':
# 	app.run(host='0.0.0.0', port='80') 

if __name__ == "__main__":
	uvicorn.run("api:app", host='0.0.0.0', port=80)

