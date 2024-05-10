import asyncio
from typing import List 
from fastapi.websockets import WebSocketState
from fastapi import FastAPI, WebSocket

app = FastAPI()

channels = {}

# @app.websocket('/ws')
# async def ws_connection(ws: WebSocket):
#         global count
#         await ws.accept()
#         while True:
#                 data = await ws.receive_text()
#                 count = count+1
#                 print(f"count: {count}")

#                 await ws.send_text(f"Ack: {data}.")
#                 print("msg acked.")



@app.websocket("/chat/{channel}")
async def chat(ws: WebSocket, channel: str):
	await ws.accept()

	

	while ws.client_state == WebSocketState.CONNECTED: 
		data = await ws.receive_json()
		
		if data is None: 
			print("Received data is None.")
			continue
		
		if not isAuthorized(ws.cookies, channel):
			print("Not authorized.")
			ws.close()

		print(f"Received: {data}")

	print(f"Client disconencted: {ws.}")
	return 

async def isLive(channel: str):
	print(f"Checking is live: {channel}")
	return True

async def isAuthorized(cookies:Dict[str,str], channel: str):
	print(f"Authorized: {cookies} for {channel}")
	return True