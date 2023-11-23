FROM python:3.10.12

WORKDIR /app/auth_service

ADD auth_service/setup.py ./setup.py
RUN pip install . 
ADD auth_service/src ./src

EXPOSE 8003

ENV AUTH_STAGE='prod'

WORKDIR /app

ENTRYPOINT ["python","-u","/app/auth_service/src/api.py"]
# -u for unbuffered output, without it docker wont show any prints/logs
