FROM python 

RUN apt update; apt install ffmpeg -y

RUN pip install argparse ffmpeg-python jsonpickle requests

ADD utils/bots/tokens_auth.py /tokens_auth.py
ADD utils/bots/viewer.py /viewer.py

ENTRYPOINT ["python3", "-u", "/viewer.py"]
