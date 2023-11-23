FROM tiangolo/nginx-rtmp:latest
# this base image will download and install nginx and its rtmp module
# it is updated regularly (nginx version) but may not be at some point

COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./alias_list /alias_list

RUN 	echo "" >> ~/.bashrc; \
	cat /alias_list >> ~/.bashrc; \
	mkdir /tmp/dashstream; \
	mkdir /tmp/hlsstream

EXPOSE 9991 
# rtmp server which receives rtmp stream
EXPOSE 9992 
# http server that serves dash/hls stream 

ENTRYPOINT ["nginx", "-g", "daemon off;"]

