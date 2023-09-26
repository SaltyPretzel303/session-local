FROM tiangolo/nginx-rtmp

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 9991
EXPOSE 9992

# RUN apt update
# RUN apt install ffmpeg -y

# entrypoint will be inherited 
