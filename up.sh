#!/bin/bash 

docker-compose up --detach stream-registry \
	registry-database \
	users-db \
	tokens-core \
	tokens-db \
	tokens-api \
	cdn-manager \
	chat-relay \
	frontend 

echo "Auth, stream registry and frontend services deployed."

./utils/cdn/remove_cdn.py
./utils/cdn/deploy_cdn.py

echo "Cdn instances deployed." 

# Has to be deployed after cdn instances are up and running beacuse 
# it will try to resolve all hostanmes on startup. Resolver directive 
# is not allowed in rtmp.server section.
docker-compose up --detach cdn-proxy

echo "Cdn proxy deployed."

./utils/ingest/stop_ingests.py y
./utils/ingest/deploy_ingest.py 2 0

echo "Ingest deployed."

docker-compose up --detach ingest-proxy 
echo "Ingest proxy deoployed."
# Has to be deoployed after ingest instances deployed.
# (same reason as for cdn-proxy)

docker-compose up --detach gateway
echo "Gateway deployed."