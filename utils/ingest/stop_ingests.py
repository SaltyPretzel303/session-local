#!/usr/bin/python 

# Filter containers (all of them) by the label associated with the ingest server.
# If remove flag is set (y as an cli argument) stopped containers will be removed.

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
		remove_input = input("Do you want to remove this containers ? (y to proceed): ")
		REMOVE_FLAG = remove_input == "y"

	if REMOVE_FLAG:
		for ing in ingests:
			print(f"Removing: {ing['Names'][0]}")
			d_api.remove_container(ing)

print("Exiting ... ")
	