#!/usr/bin/env bash
password='g'
flag=$1
target=$2
port=$3

if [ ${flag} = '1' ]
then
    cd ~/Project/attacks/
    echo $password | sudo -S python tcp-syn-flood-attack.py -t $target:$port
elif [ ${flag} = '2' ]
then
    sleep 120
    echo $password | sudo -S nmap -sV $target
elif [ ${flag} = '3' ]
then
sleep 60
    echo $password | sudo -S nmap -sU $target
elif [ ${flag} = '4' ]
then
sleep 60
    echo $password | sudo -S nmap -v -sV $target
fi
