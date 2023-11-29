FROM python

WORKDIR /app
ADD ./client_gateway ./client_gateway
ADD ./shared_model ./shared_model

WORKDIR /app/client_gateway

RUN pip install .

EXPOSE 8000

ENV PYTHONPATH=.
ENV GATEWAY_STAGE='prod'

WORKDIR /app
ENTRYPOINT ["python3", "client_gateway/src/api.py"]
