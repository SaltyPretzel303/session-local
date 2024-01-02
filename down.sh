#!/bin/bash 

output=$(docker ps  --filter name='session/*' -q)

if [ "$output" == "" ]
then 
	echo "No runnnin session containers ... "
	exit 0
else
	echo $output | xargs docker stop 
fi
