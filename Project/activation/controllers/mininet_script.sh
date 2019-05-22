#!/usr/bin/env bash
ip_local=$1
ports=$2
ip_super=$3
port=$4
attack=$5
password='g'

echo MININET TOPOLOGY
cd ~/Project/topology
sleep 5
echo $password | sudo -S mn -c
sudo python multiple_server.py -l $ip_local:$ports -s $ip_super:$port -a $attack
#sudo python multiple_topology.py -l $ip_local:$ports -s $ip_super:$port -a $attack
