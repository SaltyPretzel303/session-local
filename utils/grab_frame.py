#!/usr/bin/python 

import ffmpeg 

STREAM_NAME="user0"
STREAM_QUALITY="subsd"
OUTPUT_FILE="./img.jpg"

# ffmpeg -i http://localhost:10000/live/streamer_subsd/index.m3u8 
# -vf "select=gt(n\,1)" 
# -vframes 1 
# img.jpg  -y

cmd = ffmpeg\
		.input(f"http://localhost:10000/live/{STREAM_NAME}_{STREAM_QUALITY}/index.m3u8")\
		.filter('scale', 300, -1) \
		.output(OUTPUT_FILE, vframes=1)\
		.global_args('-y')\
		.run()

# vframes from 1 to 32, 1 is the best