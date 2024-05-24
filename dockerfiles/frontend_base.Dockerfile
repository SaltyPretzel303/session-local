FROM node

WORKDIR /app/react_app 
COPY frontend/react_app/package.json \
	frontend/react_app/package-lock.json \
	frontend/react_app/tsconfig.json \
	frontend/react_app/tailwind.config.js \
	./

RUN npm install 

COPY frontend/react_app/src ./src
COPY frontend/react_app/public ./public

# Required for npm start
ENV PORT=80
EXPOSE 80