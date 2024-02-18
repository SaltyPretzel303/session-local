FROM python

WORKDIR /app
ADD ./tokens_auth/setup.py ./setup.py
RUN pip install . 

ADD ./tokens_auth/init.py ./init.py

EXPOSE 8100

ENTRYPOINT ["python", "-u", "/app/init.py"]
