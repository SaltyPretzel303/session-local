#!/usr/bin/python 

import os
import docker 
from requests.adapters import HTTPAdapter
from requests import post, Session
from config import DOMAIN_NAME
import json

# For each region specified in regions json/dict create one cdn server instance.
# Update regions json with the created server's ip and initialize cdn manager 
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
				"ip":"172.23.1.20",
				"domainName": f"eu-0-cdn.{DOMAIN_NAME}",
				"hls_port": 80,
				"hc_port": 80,
				"hls_path":"live",
				"hc_path":"health_check",
				"preview_path": "preview"
			}
		],
		"na": [
			{
				"ip":"172.23.1.21",
				"domainName": f"na-0-cdn.{DOMAIN_NAME}",
				"hls_port": 80,
				"hc_port": 80,
				"hls_path":"live",
				"hc_path":"health_check",
				"preview_path": "preview"
			}
		],
		"as": [
			{
				"ip":"172.23.1.22",
				"domainName": f"as-0-cdn.{DOMAIN_NAME}",
				"hls_port": 80,
				"hc_port": 80,
				"hls_path":"live",
				"hc_path":"health_check",
				"preview_path": "preview"
			}
		]
	}

regions =  {
		"eu": [
			{
				"ip":"172.23.1.20",
				"domainName": f"eu-0-cdn.{DOMAIN_NAME}",
				"hls_port": 80,
				"hc_port": 80,
				"hls_path":"live",
				"hc_path":"health_check",
				"preview_path": "preview"
			}
		]
	}

NETWORK = "session-net"
BASE_RTMP_PORT = 11000
INNER_RTMP_PORT = 1935
BASE_HLS_PORT = 10000
INNER_HLS_PORT = 80

CDN_LABEL = "cdn_instance"
CDN_IMAGE_TAG = 'session/cdn'

MANAGER_IP = f"{DOMAIN_NAME}:8004"

dckr = docker.from_env()

old_instances = dckr.containers.list(filters={"label": [CDN_LABEL]}, all=True)

if len(old_instances)>0:
	print("Some CDN instances are still running (or are not removed).")
	print("Stop/remove them before proceeding.")

	for c in old_instances:
		print(f"{c.name} --> {c.status}")

	exit(1)

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

def deploy_with_shell(region_conf, index):
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

for ind, instance in enumerate([instance for region in regions.values() for instance in region]):
	print(f"Deploying region: {instance}")
	deploy_with_shell(instance, ind)
	
print("CDNS deployed, will initialize manager.")

config = json.dumps(regions)

ping_url = f'http://{MANAGER_IP}/ping'

s = Session()
s.mount(ping_url, adapter=HTTPAdapter(max_retries=5))
try:

	print(f"Waiting for cdn manager on: {ping_url}")
	s.send()

	init_res = post(f'http://{MANAGER_IP}/initialize', json=config)
	print(f"Initialize status code: {init_res.status_code}")
	
except:
	print("Failed to initialize cdn manager with deployed cdn instances.")
	print("Cdn manager may be down.")