echo MININET TOPOLOGY
cd ~/Project/topology
sudo mn -c
sudo python single_switch.py -l 127.0.0.1:2342 -s 127.0.0.1:6653
