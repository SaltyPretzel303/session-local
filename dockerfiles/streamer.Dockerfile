FROM python 

RUN apt update; apt install ffmpeg -y
RUN mkdir /cookies 
# ^ shouldn't be used with tokens auth

RUN pip install argparse ffmpeg-python jsonpickle requests

ADD utils/bots/tokens_auth.py /tokens_auth.py
ADD utils/bots/streamer.py /streamer.py

ENTRYPOINT ["python3", "-u", "/streamer.py"]
