FROM session/nginx-rtmp

# Set up config file
COPY cdn_proxy/nginx.conf /etc/nginx/nginx.conf

# ingest
EXPOSE 9090

ENTRYPOINT ["nginx","-g","daemon off;"]
