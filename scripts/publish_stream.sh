#!/bin/bash

STREAM_NAME="some_username"

VIDEO_PATH="/home/nemanja/Videos/rabbit.mp4"
# VIDEO_PATH="/home/nemanja/Videos/horse.webm"
INGEST_PATH="rtmp://localhost:9991/live/"$STREAM_NAME

if [ "$#" -eq "2" ]
then
	VIDEO_PATH=$1
	INGEST_PATH=$2
fi

echo "Streaming: $VIDEO_PATH"
echo "To: $INGEST_PATH"

# ffmpeg -re -i "$VIDEO_PATH" -bsf:v h264_mp4toannexb -c copy -f flv -flvflags no_duration_filesize -movflags frag_keyframe+empty_moov "$INGEST_PATH"
# ffmpeg -re -i "$VIDEO_PATH" -bsf:v h264_mp4toannexb -c:v libvpx -f alsa "$INGEST_PATH"
# ffmpeg -re -i ~/Movies/sintel.mp4 -bsf:v h264_mp4toannexb -c copy -f mpegts http://127.0.0.1:8000/publish/sintel

ffmpeg -re -i "$VIDEO_PATH" \
	-c copy \
	-flvflags no_duration_filesize  `# to avoid ` \
	-movflags frag_keyframe+empty_moov `# unknown` \
	-f flv "$INGEST_PATH"
	
# for webm format, publishing but watching is laggy ... 
# ffmpeg -re -i "$VIDEO_PATH" \
# 	-c:v h264 \
# 	-c:a aac \
# 	-flvflags no_duration_filesize \
# 	-f flv "$INGEST_PATH"

# -re 
# It is an input parameter that instructs FFmpeg to read the same number of 
# frames per second as the framerate of the input video.
# It is most used for live streaming or with a camera input.

# -i 
# input file 

# -f flv
# defines output container format 
# "For the RTMP protocol, we need to use the flv (Flash Video) format." ? 
