import asyncio
import os
from typing import List
from fastapi import FastAPI, Response, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import FileResponse
import uvicorn

from datetime import datetime, timedelta

from requests import get

import jsonpickle

from shared_model.media_server_request import MediaServerRequest
from shared_model.media_server_info import MediaServerInfo
from shared_model.stream_info import StreamInfo
from shared_model.update_request import UpdateRequest

from stream_registry.src.db import Db

from stream_registry.src.app_config import AppConfig
from stream_registry.src.media_server_data import MediaServerData
from stream_registry.src.stream_data import StreamData

JSON_CONTENT_TYPE = 'application/json'

app = FastAPI()
app.add_middleware(CORSMiddleware, 
				   allow_origins=['http://session.com'], 
				   allow_credentials=True, 
				   allow_headers=['rid', 'st-auth-mode'])


TNAIL_LONGEVITY = 120 # 120s 
tnails = {}

def jsonify(content) -> str:
	return jsonable_encoder(content)

def get_db() -> Db:
	return Db(AppConfig.get_instance().db_url)

def stream_data_to_info(data:StreamData)->StreamInfo:
	servers = list(map(media_server_data_to_info, data.media_servers))
	return StreamInfo(title=data.title,
				creator=data.creator,
				category=data.category,
				media_servers=servers)

def media_server_data_to_info(data: MediaServerData)->MediaServerInfo:
	return MediaServerInfo(quality=data.quality, access_url=data.media_url)

@app.post('/update')
async def update(update_data: UpdateRequest, request: Request):
	print("Processing update stream request.")

	try:
		auth_url = AppConfig.get_instance().authorize_url
		auth_res: Response = get(url=auth_url, cookies=request.cookies)

		if auth_res is None: 
			raise Exception("Auth response is None.")

		if auth_res.status_code != 200:
			raise Exception(f"Auth status code: {auth_res.status_code}")
		
	except Exception as e :
		print(f"Failed to authorize user: {e}")
		return "Authorization failed.", status.HTTP_401_UNAUTHORIZED

	print("User authorized.")

	stream_data = get_db().update(update_data.username, update_data)

	if stream_data is None:
		print("Failed to update stream info.")
		return "Failed to perform update.", status.HTTP_500_INTERNAL_SERVER_ERROR

	return stream_data_to_info(stream_data)
			
@app.get("/by_category/{category}")
def get_by_category(category: str, region: str='eu', start: int = 0, count:int=3):
	print(f"Processing get by category request for: {category}")

	streams_data = get_db().get_by_category(category, region, start, count)
	if streams_data is None:
		return "No such category.", status.HTTP_404_NOT_FOUND
	
	return list(map(stream_data_to_info, streams_data))

@app.get("/all")
def get_all(region:str="eu", start:int=0, count:int=4):
	print("Processing get all streams request.")

	streams_data = get_db().get_all(start, count, region)
	if streams_data is None: 
		print("Failed to obtain requested streams.")
		return "Failed.", status.HTTP_500_INTERNAL_SERVER_ERROR

	return list(map(stream_data_to_info, streams_data))

# This is used by the ingest instance so therefore
# request.ip should be the ingest instance's ip.
@app.post("/start_stream")
async def start_stream(request: Request):
	print("Processing start stream request.")
	
	args = url_decode((await request.body()).decode())
	key = args.get("name")
	ingest_ip = args.get("addr") # this is gonna be the ip of nginx reverse proxy 

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
			return Response(content="Failure.", 
					   status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
		print("Stream saved.")

		# response.headers["Location"] = match_data["value"]

		return Response(status_code=status.HTTP_302_FOUND, 
				headers={'Location': match_data['value']})

	except Exception as e:
		print(f"Failed to match key: {key}, reason: {e}")
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

@app.get("/stream_info/{streamer}")
def get_stream_info(streamer: str, region:str = 'eu'):
	print(f"Processing get stream info request for: {streamer} in: {region}")

	stream_data:StreamData = get_db().get_stream(streamer)

	if stream_data is None:
		return "No such stream.", status.HTTP_404_NOT_FOUND

	if not stream_data.is_public:
		print("This is not public stream ... ")
		return "No such stream.", status.HTTP_404_NOT_FOUND
	
	return JSONResponse(jsonify(stream_data_to_info(stream_data)))

@app.get("/get_recommended/{username}")
def get_recommended(username: str):
	print("GET RECOMMENDED NOT IMPLEMENTED")
	return jsonify([]), status.HTTP_501_NOT_IMPLEMENTED

@app.get("/get_explore")
def get_explore(region: str="eu", start:int=0, count:int=2):
	print("GET EXPLORE NOT IMPLEMENTED")
	return jsonify([]), status.HTTP_200_OK

@app.get("/tnail/{streamer}")
async def get_tnail(request: Request, streamer: str='unavailable'):
	print(f"Requested tnail for: {streamer}.")

	config = AppConfig.get_instance()

	if streamer == 'unavailable':
		print("Requested static unavailable thumbnail.")
		return "Stream name not provided", status.HTTP_404_NOT_FOUND

	if not is_live(streamer):
		return "Streamer is not live.", status.HTTP_404_NOT_FOUND
	
	if streamer not in tnails or is_expired(tnails[streamer]):
		print("Thumbnail expired, will generate new.")

		gen_result = await generate_thumbnail(streamer, 
									config.tnail_path(streamer))

		if not gen_result:
			print(f"Failed to generate thumbnail for: {streamer}.")
			return "Server error.", status.HTTP_500_INTERNAL_SERVER_ERROR

		exp_date = datetime.now() + timedelta(seconds=TNAIL_LONGEVITY)
		tnails[streamer] = exp_date
		print(f"Tnail generated, will expire at: {exp_date}.")

	if not os.path.exists(config.tnail_path(streamer)):
		print(f"Failed to generate tnail at: {config.tnail_path(streamer)}")
		return "Server error.", status.HTTP_500_INTERNAL_SERVER_ERROR

	print(f"Returning tnail for {streamer}.")
	return FileResponse(path=config.tnail_path(streamer), media_type="image/jpg")

def flatten_cookies(cookies):
	return f"Cookie: sAccessToken={cookies['sAccessToken']}"
	return ",".join([f"{key}:{cookies[key]}" for key in cookies])

def is_expired(expiration_date: datetime):
	return expiration_date is None or datetime.now() > expiration_date

async def generate_thumbnail(streamer, path):
	print(f"Generate tnail for: {streamer} at: {path}")
	stream_data:StreamData = get_db().get_stream(streamer)

	found_valid = False
	servers = iter(stream_data.media_servers)

	while (server:=next(servers, None)) and not found_valid: 
		try:
			print(f"Pulling from: {server.media_url}")
			proc = await asyncio.create_subprocess_exec(
				"ffmpeg",
				# Replace SessionOrigin field with some secret, or somehow
				# authenticate registry service.
				"-headers", "sessionorigin: streamregistry",
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

def is_live(streamer: str):
	return get_db().get_stream(streamer) is not None

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
	stream_name = args['name']

	print(f"Removing stream with the key: {stream_name}")

	get_db().remove_stream(stream_name)

	return Response(f"Stream {stream_name} removed.")

# if __name__ == '__main__':
# 	app.run(host='0.0.0.0', port='80') 

if __name__ == "__main__":
	uvicorn.run("api:app", host='0.0.0.0', port=80)

