FROM nginx 

ADD gateway/gateway_proxy.conf /etc/nginx/nginx.conf

# Entrypoint will be inherited.