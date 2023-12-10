FROM haproxy:latest

USER root

RUN apt update; apt install socat vim -y 

# RUN mkdir /var/log/haproxy; touch /var/log/haproxy/h_log.log
# RUN mkdir --parents /var/log/haproxy && chown -R haproxy:haproxy /var/log/haproxy
# RUN mkdir --parents /var/lib/haproxy && chown -R haproxy:haproxy /var/lib/haproxy 
RUN mkdir /run/haproxy
# RUN touch /run/haproxy/admin.sock


# USER haproxy

COPY ingest_proxy/haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg

EXPOSE 9000

# RUN useradd haproxy

ENTRYPOINT ["haproxy","-f","/usr/local/etc/haproxy/haproxy.cfg"]
