FROM session/nginx-rtmp

# Set up config file
COPY cdn_proxy/nginx.conf /etc/nginx/nginx.conf

# Default rtmp port
EXPOSE 1935

ENTRYPOINT ["nginx","-g","daemon off;"]
