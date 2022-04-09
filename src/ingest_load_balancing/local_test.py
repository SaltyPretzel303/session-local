from time import sleep
import docker
import jsonpickle


client = docker.from_env()

container = client.containers.run("tiangolo/nginx-rtmp",
                                  command=None,
                                  auto_remove=True,
                                  detach=True,
                                  name="rtmp_from_python",
                                  ports=None,
                                  volumes=None)


if container is not None:
    print("The container is running")
    # print(jsonpickle.encode(container, unpicklable=False).attrs.NetworkSettings)
    print(container.attrs.get("NetworkSettings"))

    # sleep(3.0)

    print("")
    new_container = client.containers.get("rtmp_from_python")
    # print(new_container.attrs.get("NetworkSettings"))

    cont_ip = new_container.attrs.get('NetworkSettings').get(
        'Networks').get('bridge').get('IPAddress')

    print(cont_ip)


else:
    print("Container is not running")
