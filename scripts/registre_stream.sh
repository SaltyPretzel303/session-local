#!/bin/bash 

curl --request POST \
	 --data @register_stream_data \
	 --header 'Content-type: application/json' localhost:8002/register
