# HMI modbus client
server=$1
port=$2
cd ~/Traffic\ Src/modbus_script/
python sync_tcp_client.py -s $server:$port
