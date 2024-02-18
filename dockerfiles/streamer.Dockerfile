FROM python 

RUN apt update; apt install ffmpeg -y
RUN mkdir /cookies

RUN pip install argparse ffmpeg-python jsonpickle requests

ADD utils/bots/streamer/streamer.py /streamer.py

ENTRYPOINT ['python3', '-u', '/streamer.py']
