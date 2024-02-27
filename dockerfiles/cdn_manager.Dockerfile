FROM python 

WORKDIR /app/manager 
ADD cdn_manager/setup.py ./setup.py
RUN pip install . 

ADD cdn_manager/src/ ./src/

WORKDIR /app/
ADD shared_model/ ./shared_model

EXPOSE 80

ENV PYTHONPATH=.

WORKDIR /app

ENTRYPOINT ["python", "-u", "manager/src/api.py"]