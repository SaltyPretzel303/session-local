#!/bin/bash 

REMOVE_FLAG=0

if [ "$#" -eq "1" ] && [ "$1" == "y" ]
then 
	echo "Remove flag set ... "
	REMOVE_FLAG=1
fi

INGEST_PREFIX='session-ingest-'

ingests=$(docker ps --filter name=$INGEST_PREFIX'(\d)+' -q)

if [ "$ingests" == "" ]
then 
	echo "Ingest not found ... "
	exit 0
fi 

for ingest_id in $ingests
do 
	echo $(docker inspect $ingest_id --format='{{.Name}} {{.State.Status}}')
	docker stop $ingest_id
done 

echo "============"

for ingest_id in $ingests
do 
	echo $(docker inspect $ingest_id --format='{{.Name}} {{.State.Status}}')
done 

if [ "$REMOVE_FLAG" -ne "1" ]
then 
	read -p "To remove ingests type y: " flag_txt
	if [ "$flag_txt" == "y" ]
	then 
		REMOVE_FLAG=1
	fi
fi 

if [ "$REMOVE_FLAG" -eq "1" ]
then 
	echo "Removing ingests ... "

	for ingest in $ingests
	do 
		docker remove $ingest
	done
fi 
