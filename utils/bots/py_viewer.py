#!/usr/bin/python 

import ffmpeg

ffmpeg.input("http://session.com:10000/live/streamer-0_subsd/index.m3u8")\
	.output('-', format='null')\
	.run()
