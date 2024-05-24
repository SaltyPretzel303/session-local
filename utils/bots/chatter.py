#!/usr/bin/python 

from tokens_auth import tokens_full_auth
from messages import get_message
import argparse
from random import randrange
import asyncio 
from websockets.client import connect
from websockets.client import WebSocketClientProtocol
from jsonpickle import encode
from config import signin_url, signup_url, remove_user_url
from config import ws_chat_url

DESCRIPTION = "Will connect to websocket chat server and randomly send\
			messages and print received messages."


CHANNEL = "bot_channel"
USERNAME = 'bot_chatter'
EMAIL = "chatbot@mail.com"
PASSWORD = 'verygoodbot1'
MAX_RAND_INTERVAL = 10

def json_encode(obj):
	return encode(obj, unpicklable=False)

def setup_arg_parser():

	parser = argparse.ArgumentParser(description=DESCRIPTION)

	parser.add_argument('--server', action='store', default=ws_chat_url)
	parser.add_argument('--channel', action='store', default=CHANNEL)
	parser.add_argument('--username', action='store', default=USERNAME)
	parser.add_argument('--email', action='store', default=EMAIL)
	parser.add_argument('--password', action='store', default=PASSWORD)
	parser.add_argument('--interval', action='store', default=-1)

	return parser.parse_args()

def interval_provider(interval):
	if interval == -1: # default interval value / inveraval value not provided
		return randrange(1, MAX_RAND_INTERVAL)
	else:
		return interval 

async def receiver(socket:WebSocketClientProtocol):
	if socket is None or not socket.open:  
		print("Failed to start receiver, socket is not open.")
		return 

	print("Receiving ... ")
	while socket.open: 
		try: 
			data = await socket.recv()
			print(f"received: {data}")
		except Exception as e: 
			print(f"ws exception: {e}")
			return


async def chatter(sender, server_uri, interval, cookies):
	global sender_sleep_cor
	async with connect(server_uri, extra_headers={'Cookie': cookies}) as socket: 
		print("Client connected.")

		asyncio.create_task(receiver(socket))
		print("Receiver started.")

		while socket.open: 
			msg = get_message()
			print(f"Will send: {msg}", end=" ... ")
			
			if socket.open:
				await socket.send(message(sender, msg))
				print("Sent.")

				int = interval_provider(interval)
				print(f"Delay for: {int}s")
				await asyncio.sleep(int)
				
		
		print("Socket closed.")

def flatten_cookie(cookie_jar):
	return ';'.join([f"{c.name}={c.value}" for c in cookie_jar])

def message(sender, content):
	return json_encode({"sender": sender, 
					"txtContent": content, 
					"type": "text"})

if __name__ == '__main__':
	args = setup_arg_parser()

	session = tokens_full_auth(args.username, 
							args.email,
							args.password, 
							remove_user_url,
							signup_url,
							signin_url)

	if session is None: 
		print("Failed to authenticate.")
		exit(1)

	asyncio.run(chatter(args.username,
					f"{args.server}/{args.channel}", 
					args.interval, 
					flatten_cookie(session.cookies)))
