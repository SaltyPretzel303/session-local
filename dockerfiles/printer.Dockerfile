FROM python 

WORKDIR /app
RUN pip install flask flask_api flask_restful requests Werkzeug==2.2

ADD ./printer/api.py ./api.py

EXPOSE 8010

ENTRYPOINT ["python", "-u", "api.py"]
