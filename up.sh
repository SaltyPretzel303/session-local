#!/bin/bash 

docker-compose up --detach auth-service auth-database stream-registry registry-database

echo "Auth and registry deployed ... "

./utils/cdn/remove_cdn.py
./utils/cdn/deploy_cdn.py

echo "CDN deployed ... "

docker-compose up --detach cdn-proxy

echo "CDN-proxy deoployed ... "

./utils/ingest/stop_ingests.py y
./utils/ingest/deploy_ingest.py 2 0

echo "Ingest deployed ... "

docker-compose up --detach ingest-proxy 

echo "Ingest proxy deoployed ... "