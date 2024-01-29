FROM python:latest

ADD ./icons_service/nginx.conf /etc/nginx/nginx.conf

# -p: no error if existing, make parents if needed 
RUN mkdir -p /var/icons/profiles; /var/icons/tnails

WORKDIR /icons_generator

ADD ./icons_service/icons_generator.py ./icons_generator.py

