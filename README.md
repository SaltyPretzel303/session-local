# Session

Real-time video streaming paltform developet mainly using Nginx server components with added nginx-rtmp module.  

Platform consists of __Ingest service__, __CDN (Content Delivery Network) service__, __Ingest__ and __CDN Proxy__.  

Content in received through the __Ingest proxy__ service, implemented using __Haproxy__ tcp proxy and load balancer. This component will keep track of active __Ingest service__ instances and balance the incoming traffic accordingly using __leastconn__ alghoritm.  

__Ingest service__ receives the content forwarded by the __Ingest proxy__, does secret streaming key validation (considering passed credentials in the form of the cookies) by contacting the auth service. If valid, received content is trancoded in three different qualities (size and maximum allowed bitrate) using __ffmpeg__ and h.264 compression format (libx264 implementation) and forwarded towards the __CDN proxy__.  

__CDN proxy__ is a simple implementation of Nginx server component which receives content using rtmp protocol and forwards it towards all active instances of __CDN service__ again using __ffmpeg__.

__CDN service__ receives content sent from the __CDN proxy__, does content fragmentation so it can be shared using __HLS__ protocol, generates cryptographic keys and master .m3u8 playlist containing all possible bitrate/quality information necessary for successfull use of __Variable bitrate__ techique.  

The rest of the services, not directly involved in video streaming (Stream registry, Authentication service and CDN Manager service) are developet in the form of simple HTTP Rest api's using Python.  

The frontend is developed using React web development library. Using Frontend app, clients can create account using email and password, generate unique secret streaming key required for video streaming, update info (title and category) for existing stream, browse other live streams using search bar or provided category switcher, watch some of the live streams, chat with other viewers and follow choosen stream so it will stay on the front page is the followed streamer is live. 

For the purpose of platform architecture abstarction, all of the http requests towards the backend services should be sent towards the single __Gateway__ proxy service which will then rout them accordingly. This service is also implemented using Nginx http server.

As an authentication and authorization service, __Supertokens__ auth platform is used.  

## Manual 

All of the services are expected to be run inside the docker containers. For this purpose docker-compose.yaml and appropriate dockerfiles are created (under the dockerfiles directory).  
For convinient starting of the necessary services __up.sh__ bash script, located at the project root can be used (after the __docker compose build__ commant has been run in order to pull or build necessary docker images). This script will start all the necessary backend services including: 
- two instances of ingest service  
- ingest proxy instance  
- cdn proxy instance
- two cdn instance
- gateway instance
- container hosting react web app.
  
Together will all of the services, bridge type docker network will be created. Since credentials are shared in the form of cookies, inside the http requests, platfrom's services (including frontend web app) have to be accessed using session.com domain name. This can be achieved by editing /etc/hosts configuration file (on linux systems) by adding mapping 'localhost  session.com'. Other mappings necessary for paltform's functioning are ip addresses for each cdn service instance.
Finally /etc/hosts file should look like this:  
```
172.23.1.20	eu-0-cdn.session.com  
172.23.1.21	na-0-cdn.session.com  
172.23.1.22	as-0-cdn.session.com  
127.0.0.1	session.com  
127.0.0.1	localhost
```

Other scripts for easier services management are located under project_root/utils.
