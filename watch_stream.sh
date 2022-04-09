#!/bin/bash

# look at the publish_stream.sh, this field should be the same
STREAM_NAME="stream"

vlc "http://localhost:9992/hlsstream/$STREAM_NAME.m3u8"