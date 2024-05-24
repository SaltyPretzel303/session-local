from dataclasses import dataclass
from enum import Enum
from httpx import AsyncClient 
from typing import Dict
from fastapi.websockets import WebSocketState
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi import status as code
import uvicorn
from jsonpickle import decode
from shared_model.user import User
from shared_model.chat_message import ChatMessage, MsgType

@dataclass 
class WsConnection: 
	socket: WebSocket
	name: str

DOMAIN_NAME = "session.com"
AUTHORIZE_URL = lambda channel: f"http://{DOMAIN_NAME}/auth/authorize_chatter/{channel}"

app = FastAPI()

channels: Dict[str, WsConnection] = {}


@app.websocket("/chat/{channel}")
async def chat(ws: WebSocket, channel: str):

	if channel is None or channel == "":
		raise HTTPException(status_code=code.HTTP_400_BAD_REQUEST, 
					detail='Provide channel name.')

	await ws.accept()
	print("Connection accepted, will try to authorize.")

	user: User = await isAuthorized(ws.cookies, channel)

	if user is None: 
		raise HTTPException(status_code=code.HTTP_401_UNAUTHORIZED)

	print(f"{user.username} is successfully authorization.")

	if channel not in channels: 
		print(f"Will create chat channel for: {channel}")
		channels[channel] = [WsConnection(socket=ws, name=user.username)]
	else: 
		print(f"Adding: {user.username} to the: {channel}")
		channels[channel].append(WsConnection(socket=ws, name=user.username))

	print(f"state: {list(map(lambda c: c.name, channels[channel]))}")

	while ws.client_state == WebSocketState.CONNECTED: 
		try: 
			data = await ws.receive_json()
			# data = await ws.receive_text()
		except Exception as e: 
			print(f"ws exception with: {user.username} -> {e}")
			
			if ws.client_state != WebSocketState.DISCONNECTED: 
				await ws.close()

			if channel in channels: 
				print("Removing chatter.")
				channels[channel] = filter_out(user.username, channels[channel])

			return

		print(f"Received: {data}")

		if not await isAuthorized(ws.cookies, channel):
			print("Not authorized.")
			ws.close()

		msg = ChatMessage(**data)

		for chat_user in channels[channel]: 
			print(f"Sending to: {chat_user.name}", end=' ... ')
			await chat_user.socket.send_json(msg.__dict__)
			print("Sent.")

	print(f"{user.username} disconnected from: {channel}.")
	if channel in channels:
		# channels[channel] = filter(lambda c: c.name != user.username, channels[channel])
		channels[channel] = filter_out(user.username, channels[channel])
		print(f"state: {list(map(lambda c: c.name, channels[channel]))}")
	
	return "Goodbye."


async def isLive(channel: str):
	print(f"Checking is live: {channel}")
	return True

async def isAuthorized(cookies:Dict[str,str], channel: str) -> User: 
	print(f"Checking chatters authorization for {channel}")

	async with AsyncClient() as client: 
		res = await client.get(url=AUTHORIZE_URL(channel), cookies=cookies)

		if res.status_code != code.HTTP_200_OK: 
			print("Not authorized")
			return None

		print(f"Is authorized: {res.json()}")
		return User(**res.json())

def filter_out(username, collection): 
	return list(filter(lambda el: el.name != username, collection))

if __name__ == "__main__":
	uvicorn.run("server:app", host='0.0.0.0', port=80)