FROM python 

WORKDIR /app
ADD stream_registry ./stream_registry
ADD shared_model ./shared_model

WORKDIR /app/stream_registry

RUN pip install . 

EXPOSE 8002

ENV PYTHONPATH=.
ENV REGISTRY_STAGE='prod'

WORKDIR /app

ENTRYPOINT ["python","stream_registry/src/api.py"]