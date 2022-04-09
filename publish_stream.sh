#!/bin/bash

STREAM_NAME="stream"

VIDEO_PATH="/home/nemanja/Videos/sample_video.mp4"
INGEST_PATH="rtmp://172.17.0.2:9991/live/"$STREAM_NAME

if [ "$#" -eq "2" ]
then
	VIDEO_PATH=$1
	INGEST_PATH=$2
fi

echo "Streaming: $VIDEO_PATH"
echo "To: $INGEST_PATH"

ffmpeg -re -i "$VIDEO_PATH" -bsf:v h264_mp4toannexb -c copy -f flv "$INGEST_PATH"

# -re 
# It is an input parameter that instructs FFmpeg to read the same number of 
# frames per second as the framerate of the input video.
# It is most used for live streaming or with a camera input.

# -i 
# input file 

# -f flv
# defines output container format 
# "For the RTMP protocol, we need to use the flv (Flash Video) format." ? 