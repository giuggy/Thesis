from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.term import makeTerm
import argparse
import time

PATH = '~/Project/activation/hosts/'
ATTACK_FILE = '~/Project/activation/attacks/attacks_script.sh'
traffic_file = 'traffic.sh '
traffic_server_file = "traffic_server.sh"
MODBUS_PORT = '5020'
IEC_PORT = '3000'
DNP3_PORT = '2000'
WEB_PORT = '8000'
CMD = ""


def activation_bash(host, web_server, file, port, target=None):
    job1 = PATH + file + " " + str(host.IP()) + " " + port
    job3 = PATH + traffic_file + str(web_server) + " " + WEB_PORT
    global CMD
    if target is not None:
        flag = target[0]
        if flag == 4:
            lst = str(host.IP()).split(".")
            lst.pop(len(lst) - 1)
            host_str = '.'.join(lst)
            host_target = host_str + ".0/24"
            job2 = ATTACK_FILE + " " + str(flag) + " " + host_target + " 0"
        else:
            host_target = target[1]
            port_target = target[2]
            job2 = ATTACK_FILE + " " + str(flag) + " " + str(host_target.IP()) + " " + port_target

        cmd = "bash " + job2 + " & " + job3 + " & " + job1 + " && fg"
        CMD = cmd
    else:
        cmd = "bash " + job3 + " & " + job1 + " && fg"
        CMD = cmd

    return makeTerm(host, cmd=cmd)


def myNet(super_ip, super_port, local_ip, local_port, attack):

    net = Mininet(topo=None, switch=OVSKernelSwitch, build=False)

    # Create nodes
    host1 = net.addHost('h1', mac='12:00:00:00:00:12')
    host2 = net.addHost('h2', mac='22:00:00:00:00:22')
    host3 = net.addHost('h3', mac='32:00:00:00:00:32')

    host4 = net.addHost('h4', mac='44:00:00:00:00:44')
    host5 = net.addHost('h5', mac='54:00:00:00:00:54')
    host6 = net.addHost('h6', mac='64:00:00:00:00:64')

    host7 = net.addHost('h7', mac='76:00:00:00:00:76')
    host8 = net.addHost('h8', mac='86:00:00:00:00:86')
    host9 = net.addHost('h9', mac='96:00:00:00:00:96')

    hmi = net.addHost('h10', mac='10:00:00:00:00:10')

    host_s1 = net.addHost('h11', mac='a0:00:00:00:00:a0')
    host_s2 = net.addHost('h12', mac='b2:00:00:00:00:b2')
    host_s3 = net.addHost('h13', mac='c4:00:00:00:00:c4')
    host_s4 = net.addHost('h14', mac='d6:00:00:00:00:d6')

    # Create switches
    info("*** Creating switch\n")
    switch1 = net.addSwitch('s1', listenPort=30634, mac='00:00:00:00:00:01')
    switch2 = net.addSwitch('s2', listenPort=30635, mac='00:00:00:00:00:02')
    switch3 = net.addSwitch('s3', listenPort=30636, mac='00:00:00:00:00:03')
    switch4 = net.addSwitch('s4', listenPort=30637, mac='00:00:00:00:00:04')

    info("*** Creating links\n")

    net.addLink(switch2, switch1)
    net.addLink(switch3, switch1)
    net.addLink(switch4, switch1)

    net.addLink(host1, switch2)
    net.addLink(host2, switch2)
    net.addLink(host3, switch2)
    net.addLink(host_s2, switch2)

    net.addLink(host4, switch3)
    net.addLink(host5, switch3)
    net.addLink(host6, switch3)
    net.addLink(host_s3, switch3)

    net.addLink(host7, switch4)
    net.addLink(host8, switch4)
    net.addLink(host9, switch4)
    net.addLink(host_s4, switch4)

    net.addLink(hmi, switch1)
    net.addLink(host_s1, switch1)

    # Add Controllers

    my_ctrl = []

    fl_ctrl = net.addController('c0', controller=RemoteController, ip=super_ip, port=super_port)
    c = 1
    for ip, port in zip(local_ip, local_port):
        my_ctrl.append(net.addController('c' + str(c), controller=RemoteController, ip=ip, port=port))
        c += 1

    info("*** Starting network\n")

    net.build()

    # Connect each switch to a different controller

    switch1.start([my_ctrl[0], fl_ctrl])
    switch2.start([my_ctrl[1], fl_ctrl])  # ([fl_ctrl])
    switch3.start([my_ctrl[2], fl_ctrl])
    switch4.start([my_ctrl[3], fl_ctrl])

    info("*** Waiting Floodlight \n")
    time.sleep(35)

    info("*** Starting hosts topic\n")
    # Modbus server hosts

    h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')
    h4 = net.get('h4')
    h5 = net.get('h5')
    h6 = net.get('h6')
    h7 = net.get('h7')
    h8 = net.get('h8')
    h9 = net.get('h9')
    hmi = net.get('h10')

    h_s1 = net.get('h11')
    h_s2 = net.get('h12')
    h_s3 = net.get('h13')
    h_s4 = net.get('h14')

    cmd = "bash " + PATH + traffic_server_file + " " + str(h_s1.IP()) + " " + WEB_PORT
    net.terms = makeTerm(h_s1, cmd=cmd)
    cmd = "bash " + PATH + traffic_server_file + " " + str(h_s2.IP()) + " " + WEB_PORT
    net.terms = makeTerm(h_s2, cmd=cmd)
    cmd = "bash " + PATH + traffic_server_file + " " + str(h_s3.IP()) + " " + WEB_PORT
    net.terms = makeTerm(h_s3, cmd=cmd)
    cmd = "bash " + PATH + traffic_server_file + " " + str(h_s4.IP()) + " " + WEB_PORT
    net.terms = makeTerm(h_s4, cmd=cmd)

    if attack == 2:
        target = [attack, h7, MODBUS_PORT]
    else:
        target = None
    web_list = str(h_s1.IP()) + "," + str(h_s2.IP()) + "," + str(h_s3.IP()) + "," + (h_s4.IP())
    net.terms += activation_bash(host=h1, web_server=web_list, file='host_modbus.sh', port=MODBUS_PORT)
    net.terms += activation_bash(host=h4, web_server=web_list, file='host_modbus.sh', port=MODBUS_PORT, target=target)

    net.terms += activation_bash(host=h7, web_server=web_list, file='host_modbus.sh', port=MODBUS_PORT)

    if attack == 3:
        target = [attack, h2, DNP3_PORT]
    else:
        target = None

    net.terms += activation_bash(host=h2, web_server=web_list, file='host_dnp3.sh', port=DNP3_PORT)
    net.terms += activation_bash(host=h5, web_server=web_list, file='host_dnp3.sh', port=DNP3_PORT)
    net.terms += activation_bash(host=h8, web_server=web_list, file='host_dnp3.sh', port=DNP3_PORT, target=target)

    if attack == 1:
        target = [attack, h6, IEC_PORT]
    elif attack == 4:
        target = [attack]
    else:
        target = None
    net.terms += activation_bash(host=h3, web_server=web_list, file='host_iec.sh', port=IEC_PORT, target=target)
    net.terms += activation_bash(host=h6, web_server=web_list, file='host_iec.sh', port=IEC_PORT)
    net.terms += activation_bash(host=h9, web_server=web_list, file='host_iec.sh', port=IEC_PORT)
    job3 = PATH + traffic_file + str(web_list) + " " + WEB_PORT
    print("COMMAND:" + CMD)
    cmd = "bash " + job3 + " & " + PATH + 'hmi.sh' + " " + \
          str(MODBUS_PORT) + " " + str(h1.IP()) + " " + str(h4.IP()) + " " + str(h7.IP()) + " " + \
          str(DNP3_PORT) + " " + str(h2.IP()) + " " + str(h5.IP()) + " " + str(h8.IP()) + " " + \
          str(IEC_PORT) + " " + str(h3.IP()) + " " + str(h6.IP()) + " " + str(h9.IP()) + " " + str(hmi.IP()) + " && fg"
    print("CMD HMI " + cmd)
    net.terms += makeTerm(hmi, cmd=cmd)

    CLI(net)

    # net.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--local_controller", help="list of addresses and ports of local "
                                                         "controllers (# SWITCH: 4)")
    parser.add_argument("-s", "--super_controller", help="address and port of the super controller (Floodlight)")
    parser.add_argument("-a", "--attack", help="flag for activating attack")

    args = parser.parse_args()

    if args.local_controller:
        print(args)
        listen = args.local_controller[1:len(args.local_controller)-1].split(']:[')
        local_address = listen[0].split(',')
        local_port = list(map(int, listen[1].split(',')))
        if len(local_address) != len(local_port):
            print("Error: Length of lists are different")
            exit()
    else:
        local_address = 4*['127.0.0.1']
        local_port = list(range(21342, 21346))

    if args.super_controller:
        super = args.super_controller.split(':')
        super_address = super[0]
        super_port = int(super[1])

    else:
        super_address = '127.0.0.1'
        super_port = 6653

    if args.attack:
        attack = int(args.attack)
    else:
        attack = 0

    myNet(super_ip=super_address, super_port=super_port, local_ip=local_address, local_port=local_port, attack=attack)


if __name__ == '__main__':
    setLogLevel('info')
    main()
