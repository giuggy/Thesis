ip_local=$1
port_local=$2
ip_server=$3
port_server=$4
flag=$5
sleep 30
echo LOCAL CONTROLLER
cd ~/Project/controllers/local_controller
python3 initialization.py -l $ip_local:$port_local -s $ip_server:$port_server -f $flag
