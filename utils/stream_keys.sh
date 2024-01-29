#!/bin/bash 

docker exec session-cdn-eu  ls -1 /var/www/keys/streamer_subsd | sed -nr 's/([0-9]+).key/\1/p'
