#!/usr/bin/python 

from sys import argv
from docker import APIClient


REMOVE_FLAG=False

if len(argv)>1 and argv[1]=="y":
	print("Remove flag set ... ")
	REMOVE_FLAG=True

INGEST_PREFIX='session-ingest-'
INGEST_LABEL="ingest_instance"

d_api = APIClient()

ingests = d_api.containers(all=True, filters={"label":f"{INGEST_LABEL}"})

if len(ingests) > 0:
	for ing in ingests:
		print(f"{ing['Names'][0]} -> {ing['State']}")
		if ing['State'] != "exited":
			print(f"Stopping: {ing['Names'][0]}")
			d_api.stop(ing)

	print("========")

	if not REMOVE_FLAG:
		remove_input = input("Do you want to remove this containers ? (y to proceed)")
		REMOVE_FLAG = remove_input == "y"

	if REMOVE_FLAG:
		for ing in ingests:
			print(f"Removing: {ing['Names'][0]}")
			d_api.remove_container(ing)

print("Exiting ... ")
	

# ingests=$(docker ps -a --filter name=$INGEST_PREFIX'(\d)+' -q)

# if [ "$ingests" == "" ]
# then 
# 	echo "Ingest not found ... "
# 	exit 0
# fi 

# for ingest_id in $ingests
# do 
# 	echo $(docker inspect $ingest_id --format='{{.Name}} {{.State.Status}}')
# 	docker stop $ingest_id
# done 

# echo "============"

# for ingest_id in $ingests
# do 
# 	echo $(docker inspect $ingest_id --format='{{.Name}} {{.State.Status}}')
# done 

# if [ "$REMOVE_FLAG" -ne "1" ]
# then 
# 	read -p "To remove ingests type y: " flag_txt
# 	if [ "$flag_txt" == "y" ]
# 	then 
# 		REMOVE_FLAG=1
# 	fi
# fi 

# if [ "$REMOVE_FLAG" -eq "1" ]
# then 
# 	echo "Removing ingests ... "

# 	for ingest in $ingests
# 	do 
# 		docker remove $ingest
# 	done
# fi 
