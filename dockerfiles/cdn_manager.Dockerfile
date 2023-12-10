FROM python 

WORKDIR /app 
ADD cdn_manager/setup.py ./setup.py
RUN pip install . 

ADD cdn_manager/src/ ./src/

ENV CDN_STAGE='prod'

EXPOSE 8004

ENTRYPOINT ["python", "-u", "/app/src/api.py"]