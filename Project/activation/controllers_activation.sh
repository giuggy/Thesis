#!/bin/bash

# Script to run topology and controllers: Floodlight, Local and Super controller

SESSION_NAME="Project"

ip_local="127.0.0.1"
ip_server="127.0.0.1"
port_server="8060"
port_l1=21342
port_l2=21343
port_l3=21344
port_l4=21345
flag=False
attack=$1 # 0 normal, 1 SYN Attack, 2 TCP Portscan single target, 3 Udp Portscan single target, 4 TCP Portscan single target

tmux new -d -s ${SESSION_NAME}
 

tmux new-window -t "$SESSION_NAME:1" -n "SUPER"
tmux send-keys -t ${SESSION_NAME}:1 './controllers/super_script.sh ' $ip_server " " 2117 C-m
tmux split-window -h -t ${SESSION_NAME}:1
tmux send-keys -t ${SESSION_NAME}:1 './controllers/floodlight_script.sh' C-m

tmux new-window -t "$SESSION_NAME:2" -n "LOCAL"
tmux send-keys -t ${SESSION_NAME}:2 './controllers/local_script.sh ' $ip_local " " $port_l1 " " $ip_server " " $port_server " " $flag " | tee ~/Project/debug/local1.txt" C-m


tmux split-window -h -p 50 -t ${SESSION_NAME}:2
tmux send-keys -t ${SESSION_NAME}:2 './controllers/local_script.sh ' $ip_local " " $port_l2 " " $ip_server " " $port_server " " $flag " | tee ~/Project/debug/local2.txt" C-m

tmux selectp -t 0 
tmux split-window -v -p 50 -t ${SESSION_NAME}:2
tmux send-keys -t ${SESSION_NAME}:2 './controllers/local_script.sh ' $ip_local " " $port_l3 " " $ip_server " " $port_server " " $flag " | tee ~/Project/debug/local3.txt" C-m

tmux selectp -t 2
tmux split-window -v -p 50 -t ${SESSION_NAME}:2
tmux send-keys -t ${SESSION_NAME}:2 './controllers/local_script.sh ' $ip_local " " $port_l4 " " $ip_server " " $port_server " " $flag " | tee ~/Project/debug/local4.txt" C-m

tmux new-window -t "$SESSION_NAME:3" -n "TOPOLOGY"
tmux send-keys -t ${SESSION_NAME}:3 './controllers/mininet_script.sh ' [$ip_local,$ip_local,$ip_local,$ip_local] " " [$port_l1,$port_l2,$port_l3,$port_l4] " 127.0.0.1 " 6653 " " $attack C-m




tmux select-window -t "$SESSION_NAME:3"

tmux -2 attach-session -t ${SESSION_NAME}