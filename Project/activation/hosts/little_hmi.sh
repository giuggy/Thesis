#!/usr/bin/env bash
# HMI activation all clients
port1=$1
server11=$2
server12=$3
hmi=${4}
cd ~/Project/activation/hosts/
./client_modbus.sh $server11 $port1 & ./client_modbus.sh $server12 $port1 && fg
