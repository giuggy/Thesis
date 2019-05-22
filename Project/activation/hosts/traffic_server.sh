#!/usr/bin/env bash

ip=$1
port=$2
#nginx -c /etc/nginx/nginx.conf
python3 /home/giuggy/Traffic\ Src/BackGroundTraffic/server_async.py $ip $port