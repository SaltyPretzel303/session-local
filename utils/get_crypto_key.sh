#!/bin/bash 

# docker exec cdn-eu.session ls -1 /var/www/keys/user_0_subsd | sed -nr 's/([0-9]+).key/\1/p'2
docker exec cdn-eu.session ls -1 /var/www/keys/user0_subsd | grep -o -m 1 '[0-9]*'