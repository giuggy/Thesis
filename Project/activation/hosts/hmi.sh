# HMI activation all clients
port1=$1
server11=$2
server12=$3
server13=$4
port2=$5
server21=$6
server22=$7
server23=$8
port3=$9
server31=${10}
server32=${11}
server33=${12}
hmi=${13}
cd ~/Project/activation/hosts/
./client_modbus.sh $server11 $port1 & ./client_modbus.sh $server12 $port1 & ./client_modbus.sh $server13 $port1 & ./client_dnp3.sh $server21 $port2 & ./client_dnp3.sh $server22 $port2 & ./client_dnp3.sh $server23 $port2 & ./client_iec.sh $server31 $port3 & ./client_iec.sh $server32 $port3 & ./client_iec.sh $server33 $port3 && fg