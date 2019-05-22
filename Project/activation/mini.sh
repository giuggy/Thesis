ip_local="localhost"
ip_server="127.0.0.1"
port_server="6653"
port_l1=21342
port_l2=21343
port_l3=21344
port_l4=21345

./controllers/mininet_script.sh [$ip_local,$ip_local,$ip_local,$ip_local] [$port_l1,$port_l2,$port_l3,$port_l4] $ip_server 6653