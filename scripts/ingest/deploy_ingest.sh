#!/bin/bash

# default values
INSTANCE_CNT="2"
STREAM_LIMIT="3"
# memory_per_proc="90"

NETWORK="session-net"
IP_SUBNET="172.23.1"
BASE_PORT=9090
INNER_PORT=9090

INGEST_PREFIX="session-ingest-"

# validate cli arguments
if [ "$#" -eq "0" ]
then 
	echo "Taking default values for arguments ... "
else

	if [ "$#" -eq "2" ]
	then
		INSTANCE_CNT=$1
		STREAM_LIMIT=$2	

		if [ "$#" -gt "2" ]
		then
			data_path=$3
		fi
	else
		echo "Please provide adequate arguments:"
		echo "arg1: number of ingests"
		echo "arg2: streams per ingest"
		echo "e.g.: ./deploy_ingest.sh 10 6"
		echo
		exit	
	fi

fi

echo "Number of ingests:  $INSTANCE_CNT "
echo "Streams per ingest: $STREAM_LIMIT "
echo # new line

# list previously used containers (if they exist)

# match session-ingest-[any number]
regex_match=$INGEST_PREFIX"(\d)+"
old_containers=$(docker ps -a --filter name=$regex_match -q)

if [ "$old_containers" != "" ]
then

	echo "Found next conflicted containers: "
	echo

	for single_id in $old_containers
	do

		single_name=$(docker inspect $single_id --format '{{.Name}}')
		single_status=$(docker inspect $single_id --format '{{.State.Status}}')
		echo $single_id " ---> " $single_name " ---> " $single_status

	done

	echo
	echo "Remove them before starting new ones ... "
	exit

else
	echo "No conflicting containers ... "
	echo
fi

for (( container_ind=0; container_ind<$INSTANCE_CNT; container_ind++ ))
do 

	container_ip="$IP_SUBNET.$container_ind"
	echo "Starting ingest: $INGEST_PREFIX$container_ind with ip: $container_ip" 

	let target_port=BASE_PORT+container_ind
	
	docker run -d \
				--name "$INGEST_PREFIX$container_ind" \
				--network "$NETWORK" \
				--publish "0.0.0.0:$target_port:$INNER_PORT" \
				--publish "0.0.0.0:8080:8080" \
				--ip "$container_ip" \
				 session/ingest '{"ip": "'$container_ip'", "max_streams": '$STREAM_LIMIT'}'

	sleep 0.2 
	# just so that they are not started at the same time

done
