#!/bin/bash

X_SIZE=500
Y_SIZE=500

if [ "$#" -ne 2 ]
then 
	printf "Two arguments are required: \n"
	printf "\t - stream name\n" 
	printf "\t - cookie path\n"

	printf "Leaving ... \n"
	exit 1
fi 

stream_name="$1"
cookie_path="$2"

cookie=$(cat $cookie_path)
echo "Watching: " $stream_name", with cookie: " $cookie

ffplay -x $X_SIZE -y $Y_SIZE \
	-fflags nobuffer \
	-headers 'Cookie: session='$cookie \
	http://localhost:10000/live/$stream_name/index.m3u8

# -headers 'Cookie: session='$(cat $cookie_path | ./just_cookie.sh) \
