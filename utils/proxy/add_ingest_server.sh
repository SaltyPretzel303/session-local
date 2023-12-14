#!/bin/bash 

# Using haproxy runtime_cli adds ingest backend server instance to the loabalaners's 
# server pool.

if [ "$#" -ne '2' ]
then 
	echo "Please provide server name and ip:port"
	echo "e.g.: ./add_ingest_server.sh rtmp_server9 172.23.1.9:9090"
	exit 1
else
	echo "Server name: $1 with addr: $2"
fi

server_name=$1
addr=$2

echo "add server \
	 rtmp_backend/$server_name \
	 $addr \
	 enabled" | socat stdin tcp4:localhost:9001 

# For some reason when added server will be ignored by the loadbalancer. 
# On of the solutions is to set servers weight to 2 and then back to 1 (default value).
# After this for some reason newly added server will be considered.

# echo 'set weight rtmp_backend/rtmp_server3 2' | socat stdio tcp4:localhost:9001
# echo 'set weight rtmp_backend/rtmp_server3 1' | socat stdio tcp4:localhost:9001