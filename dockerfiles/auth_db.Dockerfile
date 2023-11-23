FROM mongo:latest

ADD ./dockerfiles/auth_mongo_init.sh /docker-entrypoint-initdb.d/