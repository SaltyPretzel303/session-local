#!/bin/bash 

# Using haproxy runtime_cli adds ingest backend server instance to the
# loabalaners's server pool.

if [ "$#" -ne '2' ]
then 
	echo "Please provide server name and ip:port"
	echo "e.g.: ./add_ingest_server.sh rtmp_server9 172.23.1.9:9090"
	exit 1
fi

server_name=$1
address=$2

ip="$(docker inspect "$address" --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"
)"

echo "Server name: $1 with domain address: $2 and ip: $ip"

echo "add server \
	rtmp_backend/$server_name \
	$ip:1935 \
	enabled \
	maxconn 1 \
	check " | socat stdin tcp4:localhost:9001 


# server_up="$(echo 'show servers state' | socat stdio tcp4:localhost:9001 | grep $server_name)"
# echo "Is up: $server_up"

# These three won't be executed for some reason, will have to be executed
# manually or 
# echo 'enable health rtmp_backend/$server_name' | socat stdin tcp4:localhost:9001 

# For some reason when added server will be ignored by the loadbalancer. 
# On of the solutions is to set servers weight to 2 and then back to 1 (default value).
# After this for some reason newly added server will be considered.
# echo 'set server rtmp_backend/$server_name weight 2' | socat stdin tcp4:localhost:9001 
# echo 'set server rtmp_backend/$server_name weight 1' | socat stdin tcp4:localhost:9001 
