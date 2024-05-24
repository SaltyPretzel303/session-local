FROM python 

RUN apt update; apt install ffmpeg -y
RUN apt update; apt install uvicorn -y

WORKDIR /app/stream_registry
COPY stream_registry/setup.py ./setup.py
RUN pip install . 

WORKDIR /app
RUN mkdir tnails
COPY unavailable.png ./tnails/unavailable.png
# ^ provide some icon representing unavailable stream thumbnail 
# This may not be used. Default stream icon could be implemnted on frontend. 

RUN mkdir categories
COPY stream_registry/icons/* ./categories/

WORKDIR /app/stream_registry
COPY stream_registry/src ./src

WORKDIR /app
COPY shared_model ./shared_model

ENV PYTHONPATH=.
ENV REGISTRY_STAGE='prod'

ENTRYPOINT ["python", "-u", "stream_registry/src/api.py"]
# ENTRYPOINT ["uvicorn", "stream_registry.src.api:app"]