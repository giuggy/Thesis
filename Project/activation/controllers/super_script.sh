ip=$1
port=$2
echo SUPER CONTROLLER
cd ~/Project/controllers/super_controller
python3 super_controller.py -l $ip:$port