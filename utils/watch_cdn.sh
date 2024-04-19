#!/usr/bin/bash

watch -n 1 docker exec eu-0-cdn.session.com ls -l /var/www/live /var/www/preview
