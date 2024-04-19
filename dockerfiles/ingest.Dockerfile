FROM session/nginx-rtmp

# Set up config file
COPY ingest/nginx.conf /etc/nginx/nginx.conf

# default rtmp
EXPOSE 1935 

ENTRYPOINT ["nginx","-g","daemon off;"]
