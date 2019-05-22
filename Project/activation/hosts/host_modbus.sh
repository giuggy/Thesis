# Host modbus server
ip=$1
port=$2
cd ~/Traffic\ Src/modbus_script/
python sync_tcp_server.py -l $ip:$port