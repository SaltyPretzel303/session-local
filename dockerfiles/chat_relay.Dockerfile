FROM python

RUN apt update; apt install uvicorn -y 

WORKDIR /app/

COPY ./shared_model ./shared_model

WORKDIR /app/relay 
COPY ./chat_relay/setup.py ./setup.py
RUN pip install . 

COPY ./chat_relay/src ./src 

WORKDIR /app
ENV PYTHONPATH=.
EXPOSE 80

ENTRYPOINT ["python", "-u", "./relay/src/server.py"]

