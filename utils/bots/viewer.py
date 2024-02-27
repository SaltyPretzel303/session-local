#!/usr/bin/python 

from argparse import ArgumentParser
import os
from subprocess import Popen
import ffmpeg
import signal

from requests import Session, get
from tokens_auth import tokens_full_auth

def setup_arg_parser():

	parser = ArgumentParser()
	parser.add_argument("--username", action='store', default='viewer_0')
	parser.add_argument("--email", action='store', default='viewer_0@session.com')
	parser.add_argument("--password", action='store', default='strongpassword_1')

	parser.add_argument("--remove_at", 
					action='store', 
					default='http://session.com/remove')


	parser.add_argument("--signup_at", 
					action='store', 
					default='http://session.com/auth/signup')

	parser.add_argument("--signin_at", 
					action='store', 
					default='http://session.com/auth/signin')

	# stream_registry_at
	parser.add_argument('--reg_at', 
					action='store',
					default='http://session.com/stream/stream_info')

	parser.add_argument('--quality', action='store', default='subsd')
	parser.add_argument('--stream', action='store', default='streamer-0')

	parser.add_argument('--count', action='store', default='1')
	parser.add_argument('--show', action='store_true', default=False)
	parser.add_argument('--w', action='store', default='400')
	parser.add_argument('--h', action='store', default='300')

	return parser.parse_args()

def form_headers(s: Session):
	return f"'Cookie: sAccessToken={s.cookies['sAccessToken']}'"

def form_play_stream_cmd(headers, width, height, stream_url)->str:
	return [ 'ffplay',
		'-fflags', 'nobuffer',
		'-headers', headers,
		'-x', width,
		'-y', height,
		'-loglevel', 'error',
		stream_url
	]

def form_waste_stream_cmd(headers, stream_url):
	return [
		'ffmpeg', '-i', stream_url,
		'-headers', headers,
		'-loglevel', 'error',
		'-f', 'null',
		'-'
	]

def get_stream_url(registry_at, stream_name, quality):
	reg_url = f"{registry_at}/{stream_name}"
	info_res = get(reg_url)

	if info_res is None or info_res.status_code != 200:
		print("Failed to obtain stream info.")
		return None
	
	print("Media/cdn server info obtained.")
	
	cdn_url = info_res.json()['media_server']['full_path']
	return f"{cdn_url}/{stream_name}_{quality}/index.m3u8"

def gen_username(base, index):
	return f"{base}_proc_{index}"

def gen_email(base:str, index):
	parts = base.split("@")
	return f"{parts[0]}_proc_{index}@{parts[1]}"

def watch(username,
		email, 
		password, 
		remove_at,
		signup_at, 
		signin_at,
		registry_at,
		stream_name,
		quality,
		width, 
		height,
		count, 
		should_show):

	procs = {}

	for i in range(0, int(count)):

		ind_username = gen_username(username, i)
		ind_email = gen_email(email, i)

		s = tokens_full_auth(ind_username, 
					ind_email, 
					password, 
					remove_at, 
					signup_at, 
					signin_at)
		if s is None: 
			print(f"Failed to authenticate: {ind_username} - {ind_email}")
			return procs
		print(f"Successfully authenticated: {ind_username}")

		headers = form_headers(s)
		stream_url = get_stream_url(registry_at, stream_name, quality)

		if stream_url is None: 
			print("Failed to obtain stream url.")
			return procs

		# Nice approach but python-ffmpeg doesn't support -headers.
		# Which is necessary for encryption btw.
		# proc = ffmpeg.input(stream_url)\
		# 		.output('-',format='null')\
		# 		.run_async()

		if should_show:
			print(f"Will show stream: {stream_url} for: {ind_username}")
			cmd = form_play_stream_cmd(headers, width, height, stream_url)
		else:
			print(f"Will waste stream from: {stream_url} with: {ind_username}.")
			cmd = form_waste_stream_cmd(headers, stream_url)
		
		proc = Popen(cmd)	
		procs[proc.pid] = proc

	return procs

if __name__ == '__main__':

	args = setup_arg_parser()

	procs = watch(args.username, 
	   args.email,
	   args.password,
	   args.remove_at,
	   args.signup_at,
	   args.signin_at,
	   args.reg_at,
	   args.stream,
	   args.quality,
	   args.w,
	   args.h,
	   args.count,
	   args.show)
	
	print(f"Started: {[pid for pid in procs]}")

	def signal_handler(sig, frame):
		print(f"Handling {sig} signal.")
		if procs is None:
			print("No processed to stop.")
			exit(0)

		print(f"{len(procs)} procs to stop.")
		for proc in procs: 
			procs[proc].terminate()

		print("Procs stopped.")
		# exit(0)


	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)

	while procs: 
		pid, status = os.wait()
		procs.pop(pid)
		print(f"Process: {pid} just died.")

	print("Exiting ... ")
	exit(0)
