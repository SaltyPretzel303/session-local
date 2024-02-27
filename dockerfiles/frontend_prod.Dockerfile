FROM session/frontend_base

WORKDIR /app/react_app
RUN npm run build 

# Express frontend host
WORKDIR /app/express_host
ADD frontend/express_host/package.json \
	frontend/express_host/package-lock.json \
	./

RUN npm install 

ADD frontend/express_host/server.js ./

RUN mv /app/react_app/build /app/express_host/client_build

ENV NODE_ENV="production"

ENTRYPOINT ["npm", "start"]
