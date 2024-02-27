#!/usr/bin/python 

import ffmpeg

ffmpeg.input("http://localhost:10000/live/streamer-0_subsd/index.m3u8")\
	.output('-', format='null')\
	.run()
