#!/usr/bin/env bash
password="g"
echo FLOODLIGHT CONTROLLER
cd ~/floodlight
echo $password | sudo -S mn -c
java -jar target/floodlight.jar
 