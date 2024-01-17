FROM nginx:latest

RUN apt update; apt install npm -y
RUN apt update; apt install procps -y

WORKDIR /app

ADD frontend/react_app/package.json \
	frontend/react_app/package-lock.json \
	frontend/react_app/tsconfig.json \ 
	./

# RUN npm install 

ADD frontend/react_app/src ./src
ADD	frontend/react_app/public ./public
	
# RUN npm run build
# RUN mv ./build /var/www/

ADD ./frontend/frontend_proxy.conf /etc/nginx/nginx.conf

EXPOSE 80

# RUN echo "nginx; npm start" > launcher.sh

ENTRYPOINT ["nginx", "-g", "daemon off;"] 
# ENTRYPOINT ["/bin/bash", "./launcher.sh"]
