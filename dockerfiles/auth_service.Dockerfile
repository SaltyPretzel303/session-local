FROM python

WORKDIR /app/auth_service
ADD auth_service/setup.py ./setup.py
RUN pip install . 

ADD auth_service/src ./src

WORKDIR /app 
ADD shared_model ./shared_model

WORKDIR /app/auth_service

EXPOSE 8003

ENV PYTHONPATH=.
ENV AUTH_STAGE='prod'

WORKDIR /app

ENTRYPOINT ["python", "-u", "auth_service/src/api.py"]
# -u for unbuffered output, without it docker wont show any prints/logs
