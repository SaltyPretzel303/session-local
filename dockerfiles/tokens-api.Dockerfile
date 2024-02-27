FROM python

WORKDIR /app/tokens_api
ADD ./tokens_api/setup.py ./setup.py
RUN pip install . 

ADD ./tokens_api/* ./

WORKDIR /app/shared_model
ADD ./shared_model ./

WORKDIR /app/
ENV PYTHONPATH=.

EXPOSE 80
ENTRYPOINT ["python", "-u", "/app/tokens_api/api.py"]
