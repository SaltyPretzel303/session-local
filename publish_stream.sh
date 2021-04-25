ffmpeg -re -i ~/Videos/video.mp4 -bsf:v h264_mp4toannexb -c copy -f mpegts http://172.17.0.2:9991/live/ffmpegstream
