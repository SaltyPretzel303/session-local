#!/bin/bash

# Using haproxy runtime_cli polls the backend's state. 

echo 'show servers state' | socat stdio tcp4:localhost:9001