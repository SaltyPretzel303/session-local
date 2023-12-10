#!/bin/bash 

# ffmpeg -re -i - \
# 	-vf "drawtext=text='%{gmtime\:%H-%M-%S.%6N-%Z}':fontcolor=red:fontsize=36" \
# 	-f flv -

# ffmpeg -re -i - -f flv rtmp://localhost:9090/local_hls/stream 
# 2>> /var/log/nginx/proc_log.log

for arg in "$@"
do
	echo "-> $arg" > /var/log/nginx/ff_log.log

done

name=$[1]

# ffmpeg -re -i pipe: -c copy -f flv rtmp://localhost:9090/local_hls/$name 2>>/var/log/nginx/ff_log.log
ffmpeg -re -i rtmp://localhost:9090/ingest/$name -c copy -f flv -flvflags no_duration_filesize rtmp://localhost:9090/local_hls/$name


# 2>> /var/log/nginx/proc_log.log

# 2>/var/log/nginx/proc_log.log
# -vf "drawtext=text='%{gmtime\:%H-%M-%S}':fontcolor=red:fontsize=30:y=32" \