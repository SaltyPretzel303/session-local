FROM python 

RUN apt update; apt install ffmpeg -y

RUN pip install argparse ffmpeg-python jsonpickle requests

COPY utils/config.py /config.py
COPY utils/bots/tokens_auth.py /tokens_auth.py
COPY utils/bots/viewer.py /viewer.py

ENTRYPOINT ["python3", "-u", "/viewer.py"]
