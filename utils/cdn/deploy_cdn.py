import docker 
import json

regions =  {
		"eu": [
			"cdn:8000/live"
		],
		"na": [
			"cdn:8000/live"
		],
		"as": [
			"cdn:8000/live"
		]
	}

NETWORK = "session-net"
IP_SUBNET_PREFIX = "172.23.2."
BASE_PORT = 8000
INNER_PORT = 8000
MEDIA_PATH = "live"

CDN_PREFIX = "session-cdn-"
CDN_LABEL = "cdn_instance"

BUILD_CONTEXT = '../../'
CDN_IMAGE_TAG = 'session/cdn'
CDN_DOCKERFILE = 'dockerfiles/cdn.Dockerfile'

MANAGER_IMAGE_TAG = 'session/cdn-manager'
MANGER_DOCKERFILE = 'dockerfiles/cdn_manager.Dockerfile'
MANAGER_CONFIG_PATH = '../../cdn_manager/src/app_config.json'
MANAGER_CONT_NAME = 'session-cdn-manager'
MANAGER_LABEL = 'cdn_manager'

PRODUCTION_STAGE = 'prod'

dckr = docker.APIClient()

# regex_pat = f"{CDN_PREFIX}(\\d)+"
old_cdns = dckr.containers(filters={"label": CDN_LABEL}, all=True)

if len(old_cdns)>0:
	print("Some CDN instances are still running (or still not removed) ... ")
	print("Stop or remove them before proceeding  ... ")
	for c in old_cdns:
		print(f"{c['Names'][0]} --> {c['State']}")

	exit(1)

generator = dckr.build(path=BUILD_CONTEXT,
		   tag=CDN_IMAGE_TAG,
		   rm=True,
		   pull=False,
		   dockerfile=CDN_DOCKERFILE)

for block in generator:
	line = block.decode().replace("\\n","")
	print(line)

index=0
for region_key in regions:
	c_name = f"{CDN_PREFIX}{region_key}"
	out_port = BASE_PORT + index
	
	ports = [INNER_PORT]
	addr = f"{IP_SUBNET_PREFIX}{index}"

	h_config = dckr.create_host_config(
		port_bindings={
			INNER_PORT: ("0.0.0.0", out_port)
		}
	)
	n_config = dckr.create_networking_config({
		NETWORK: dckr.create_endpoint_config(ipv4_address=addr)
	})
	cnt_id = dckr.create_container(image=CDN_IMAGE_TAG,
					   	detach=True,
						ports=[INNER_PORT],
						host_config=h_config,
						networking_config=n_config,
						name=c_name,
						labels=[CDN_LABEL],
						stop_signal="SIGINT")
	
	dckr.start(cnt_id)
	regions[region_key] = [f"{addr}:{out_port}/{MEDIA_PATH}"]
	
	index = index+1

print("Deployed CDNs")
print(regions)

file = open(MANAGER_CONFIG_PATH, 'r')
json_content = json.loads(file.read())
file.close()

json_content[PRODUCTION_STAGE] = regions

file = open(MANAGER_CONFIG_PATH, "w")
file.write(json.dumps(json_content, indent=4))
print(json.dumps(json_content,indent=4))
file.close()

generator = dckr.build(path = BUILD_CONTEXT, 
		  tag = MANAGER_IMAGE_TAG,
		  rm = True,
		  pull = False,
		  dockerfile = MANGER_DOCKERFILE)

for block in generator:
	line = json.loads(block.decode().replace("\\n",""))
	if "stream" in line:
		line = line["stream"]
	print(line)

manager_ind = dckr.create_container(image=MANAGER_IMAGE_TAG,
					  detach=True,
					  ports=[8004],
					  host_config=dckr.create_host_config(
						port_bindings={
							8004:("0.0.0.0",8004)
						}
					  ),
					  networking_config=dckr.create_networking_config(
						{
							NETWORK: dckr.create_endpoint_config()
						}
					  ),
					  name=MANAGER_CONT_NAME,
					  labels=[MANAGER_LABEL],
					  stop_signal='SIGINT')
dckr.start(manager_ind)