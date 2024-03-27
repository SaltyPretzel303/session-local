#!/usr/bin/python

import requests
import re


resp = requests.get("http://localhost:10000/live/streamer-0_subsd/index.m3u8")

pattern = 'URI="(.+)"'
output = re.search(pattern, resp.content.decode())
if output is not None: 
	print(output[1])