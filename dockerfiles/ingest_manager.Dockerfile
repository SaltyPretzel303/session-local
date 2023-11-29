FROM python:3

WORKDIR /app
ADD ./ingest_manager/ ./ingest_manager
ADD ./shared_model ./shared_model

WORKDIR /app/ingest_manager
RUN pip install . 

ENV PYTHONPATH=.

EXPOSE 8001

WORKDIR /app

ENTRYPOINT ["python3", "-u", "ingest_manager/src/api.py"]