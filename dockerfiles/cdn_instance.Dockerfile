FROM session/nginx-rtmp

# Set up config file
COPY cdn_instance/nginx.conf /etc/nginx/nginx.conf

# WORKDIR /launcher
# ADD ./ingest/launcher/* ./
# RUN pip3 install setuptools
# RUN pip3 install . 

# ingest
EXPOSE 11000
# hls content
EXPOSE 80

# ENTRYPOINT ["python3", "-u", "launcher.py"]

ENTRYPOINT ["nginx","-g","daemon off;"]