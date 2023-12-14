import json
from docker import APIClient
api = APIClient()

context_path = '../../'
image_tag = 'session/cdn-manager'
d_file = 'dockerfiles/cdn_manager.Dockerfile'

# img, generator, third = 
generator = api.build(path = context_path, 
		  tag = image_tag,
		  rm = True,
		  pull = False,
		  dockerfile = d_file)

for block in generator:
	line = json.loads(block.decode().replace("\\n",""))
	if "stream" in line:
		line = line["stream"]
	print(line)