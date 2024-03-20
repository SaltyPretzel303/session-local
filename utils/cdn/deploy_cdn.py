#!/usr/bin/python 

import os
import docker 
import jsonpickle
from requests import Response, post
from retry_requests import retry

# For each region specified in regions json/dict create one cdn server instance.
# Update regions json with the created server's ip and create cdn manager 
# with the updated json config. 
# Could not find soultion to handle build errors or stop the deploy process
# if error occur. docker_api.build(...) returns very odd stream_helper ...

# Edit /etc/hosts to act as a dns server for all of these instances.
#########
# 172.19.0.20	eu-0-cdn.session.com
# 172.19.0.21	na-0-cdn.session.com
# 172.19.0.22	as-0-cdn.session.com
# 127.0.0.1	session.com
#########
# Add this ^ at the top of /etc/hosts.
# If new cdn instances are added, domain name mappings should be added to 
# the /etc/hosts as well.
regions =  {
		"eu": [
			{
				"ip":"172.19.0.20",
				"domainName": "eu-0-cdn.session.com",
				"hls_port": 80,
				"hc_port": 80,
				"hls_path":"live",
				"hc_path":"health_check"
			}
		],
		"na": [
			{
				"ip":"172.19.0.21",
				"domainName": "na-0-cdn.session.com",
				"hls_port": 80,
				"hc_port": 80,
				"hls_path":"live",
				"hc_path":"health_check"
			}
		],
		"as": [
			{
				"ip":"172.19.0.22",
				"domainName": "as-0-cdn.session.com",
				"hls_port": 80,
				"hc_port": 80,
				"hls_path":"live",
				"hc_path":"health_check"
			}
		]
	}

regions =  {
		"eu": [
			{
				"ip":"172.19.0.20",
				"domainName": "eu-0-cdn.session.com",
				"hls_port": 80,
				"hc_port": 80,
				"hls_path":"live",
				"hc_path":"health_check"
			}
		]
	}

NETWORK = "session-net"
IP_SUBNET_PREFIX = "172.19.0."
STARTING_IP = 20
BASE_RTMP_PORT = 11000
INNER_RTMP_PORT = 11000
BASE_HLS_PORT = 10000
INNER_HLS_PORT = 80

CDN_LABEL = "cdn_instance"
CDN_IMAGE_TAG = 'session/cdn'

MANAGER_IP = "session.com:8004"

dckr = docker.from_env()

old_instances = dckr.containers.list(filters={"label": [CDN_LABEL]}, all=True)

if len(old_instances)>0:
	print("Some CDN instances are still running (or are not removed).")
	print("Stop/remove them before proceeding.")

	for c in old_instances:
		print(f"{c.name} --> {c.status}")

	exit(1)

def gen_ip(index):
	return f"{IP_SUBNET_PREFIX}{STARTING_IP+index}"

def deploy_with_api(region_key, index):
	container_name = region[region_key][0]['domainName']
	out_hls_port = BASE_HLS_PORT + index
	out_rtmp_port = BASE_RTMP_PORT + index
	
	container = dckr.containers.run(image=CDN_IMAGE_TAG,
					   	detach=True,
						ports={
							INNER_HLS_PORT: ("0.0.0.0", out_hls_port),
							INNER_RTMP_PORT: ("0.0.0.0", out_rtmp_port)
						},
						network=NETWORK,
						name=container_name,
						labels=[CDN_LABEL],
						stop_signal="SIGINT")


	# Container obj returned from run() won't be populated with network attrs.
	container = dckr.containers.get(container.id)
	ip = container.attrs["NetworkSettings"]["Networks"][NETWORK]["IPAddress"]
	regions[region_key][0]["ip"] = ip
	
	return

def deploy_with_shell(region_conf):
	# Using shell is allowing me to assing ip to each container, which will 
	# allow me to have single /etc/hosts. Static DNS in some way.
	c_name = region_conf['domainName']
	out_hls_port = BASE_HLS_PORT + index
	out_rtmp_port = BASE_RTMP_PORT + index
	ip = region_conf['ip']

	cmd = f'docker run --name {c_name} \
			--network {NETWORK} \
			--ip {ip} \
			--publish 0.0.0.0:{out_hls_port}:{INNER_HLS_PORT} \
			--publish 0.0.0.0:{out_rtmp_port}:{INNER_RTMP_PORT} \
			--label {CDN_LABEL} \
			--stop-signal SIGINT \
			--detach  {CDN_IMAGE_TAG}'

	os.system(cmd)

	return

index=0
for region_key in regions:
	for region in regions[region_key]:
		print(f"Deploying region: {region}")
		deploy_with_shell(region)
		index = index+1

print("CDNS deployed, will initialize manager.")

config = jsonpickle.encode(regions, unpicklable=False)

retry_session = retry(retries=5, backoff_factor=0.2)
try:
	print(f"Waiting for cdn manager on: {MANAGER_IP}")
	retry_session.get(f'http://{MANAGER_IP}/ping')

	init_res: Response = post(f'http://{MANAGER_IP}/initialize', json=config)
	print(f"Initialize status code: {init_res.status_code}")
	
except:
	print("Failed to initialize cdn manager with deployed cdn instances.")
	print("Cdn manager may be down.")