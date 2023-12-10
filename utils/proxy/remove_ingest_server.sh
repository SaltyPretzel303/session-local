#!/bin/bash

if [ "$#" -ne '1' ]
then 
	echo "Please provide server name."
	exit 1
else
	echo "Server name: $1"
fi

echo "disable server\
	 rtmp_backend/$1" | socat stdin tcp4:localhost:9001 

echo "del server\
	rtmp_backend/$1" | socat stdio tcp4:localhost:9001