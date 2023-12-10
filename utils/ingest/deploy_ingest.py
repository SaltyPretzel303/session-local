#!/usr/bin/python 

from sys import argv
from docker import APIClient
import re


INSTANCE_CNT=2
START_IND=0

NETWORK="session-net"
IP_SUBNET="172.23.1"
BASE_RTMP_PORT=9090
BASE_HLS_PORT=8080
INNER_RTMP_PORT=9090
INNER_HLS_PORT=8080
IMAGE_NAME="session/ingest"

INGEST_LABEL="ingest_instance"

INGEST_PREFIX="session-ingest-"

def is_conflicting(container):
	name = container['Names'][0]
	print(f"Matching: {name}", end="\t->\t")

	reg_res = re.findall(f"{INGEST_PREFIX}(\d+)$", name)
	
	if len(reg_res) > 0:
		ind = int(reg_res[0])
		if ind >= START_IND and ind < START_IND + INSTANCE_CNT:
			print("CONFLICT")
			return True
	
	print("OK")
	return False

if len(argv) > 1:
	INSTANCE_CNT = int(argv[1])

	if len(argv) > 2:
		START_IND = int(argv[2])

print("Using arguments: ")
print(f"Instance count:\t{INSTANCE_CNT}")
print(f"Start index:\t{START_IND}")

d_api = APIClient()

containers = d_api.containers(all=True, filters={"name": f"{INGEST_PREFIX}(\d)+"})

conflict_conts = [c for c in containers if is_conflicting(c)]

if len(conflict_conts) > 0:
	print("Found conflicting containers ... ")
	for c in conflict_conts:
		print(c["Names"][0])

	exit(1)
else:
	print("No conflicting containers ... ")
	for ind in range(START_IND, START_IND+INSTANCE_CNT):
		c_name = f"{INGEST_PREFIX}{ind}"
		out_rtmp_port = BASE_RTMP_PORT+ind
		out_hls_port = BASE_HLS_PORT+ind

		c_ports = [INNER_RTMP_PORT, INNER_HLS_PORT]
		addr = f"{IP_SUBNET}.{ind}"

		h_config = d_api.create_host_config(
			port_bindings={
				INNER_RTMP_PORT: ("0.0.0.0", out_rtmp_port),
				INNER_HLS_PORT: ("0.0.0.0", out_hls_port)
			}
		)

		n_config = d_api.create_networking_config({
			NETWORK: d_api.create_endpoint_config(ipv4_address=addr)
		})

		ing_id = d_api.create_container(image=IMAGE_NAME,
								  	detach=True, 
									ports=c_ports,
									host_config=h_config,
									networking_config=n_config, 
									name=c_name, 
									labels=[INGEST_LABEL])
		d_api.start(ing_id)




# for (( container_ind=START_INDEX; container_ind<$INSTANCE_CNT; container_ind++ ))
# do 

# 	let rtmp_port=BASE_RTMP_PORT+container_ind
# 	let hls_port=BASE_HLS_PORT+container_ind

# 	# +2 because vaild ip range starts at 172.23.1.2 (not 172.23.1.0)
# 	container_ip="$IP_SUBNET.$((container_ind + 2))"
# 	echo "Starting ingest: $INGEST_PREFIX$container_ind with ip: $container_ip:$rtmp_port" 
	
# 	docker run -d \
# 				--name "$INGEST_PREFIX$container_ind" \
# 				--network "$NETWORK" \
# 				--publish "0.0.0.0:$rtmp_port:$INNER_RTMP_PORT" \
# 				--publish "0.0.0.0:$hls_port:$INNER_HLS_PORT" \
# 				--ip "$container_ip" \
# 				session/ingest 
# 				#  '{"ip": "'$container_ip'", "max_streams": '$STREAM_LIMIT'}'

# 	sleep 0.2 
# 	# just so that they are not started at the same time

# done
