FROM python 

WORKDIR /app

ADD ./printer/api.py ./api.py

RUN pip install flask flask_api flask_restful Werkzeug==2.2

EXPOSE 8010

ENTRYPOINT ["python", "-u", "api.py"]
