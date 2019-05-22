from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info, error
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.term import makeTerm
import os
import argparse
import re

PATH = '~/Project/activation/hosts/'
ATTACK_FILE = '~/Project/activation/attacks/attacks_script.sh'
MODBUS_PORT = '5020'
IEC_PORT = '3000'
DNP3_PORT = '2000'

def activation_bash(host, file, port, target=None):
    cmd = "bash " + PATH + file + " " + str(host.IP()) + " " + port
    if target is not None:
        flag = target[0]
        host_target = target[1]
        port_target = target[2]
        jobs = PATH + file + " " + str(host.IP()) + " " + port + " " + ATTACK_FILE + " " + str(flag) + " " + str(host_target.IP()) + " " + port_target
        cmd = "bash " + '~/Project/activation/attacks/host_attacker.sh ' + jobs
        print(cmd)
    else:
        print(cmd)
    return makeTerm(host, cmd=cmd)


def myNet(super_ip, super_port, local_ip, local_port):

    net = Mininet(topo=None, switch=OVSKernelSwitch, build=False)

    # Create nodes
    host1 = net.addHost('h1')
    host2 = net.addHost('h2')
    host3 = net.addHost('h3')

    # Create switches
    print("*** Creating switch")
    switch1 = net.addSwitch('s1', listenPort=6634, mac='00:00:00:00:00:01')
    # switch2 = net.addSwitch('s2', listenPort=6635, mac='00:00:00:00:00:02')

    print("*** Creating links")
    # net.addLink(switch2, switch1)
    net.addLink(host1, switch1)
    net.addLink(host2, switch1)
    net.addLink(host3, switch1)

    # Add Controllers

    fl_ctrl = net.addController('c1', controller=RemoteController, ip=super_ip, port=super_port)
    info("*** Starting network\n")

    net.build()
    switch1.start([fl_ctrl])

    h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')
    cmd = "bash " + PATH + "traffic_server.sh " + str(h3.IP()) + " " + "8000"
    net.terms = makeTerm(h3, cmd=cmd)
    cmd = "bash " + PATH + "traffic.sh " + str(h3.IP()) + " " + "8000"
    net.terms += makeTerm(h1, cmd=cmd)
    cmd = "bash " + PATH + "traffic.sh " + str(h3.IP()) + " " + "8000"
    net.terms += makeTerm(h2, cmd=cmd)

    CLI(net)
    net.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--local_controller", help="address and port of local controller")
    parser.add_argument("-s", "--super_controller", help="address and port of the super controller (Floodlight)")

    args = parser.parse_args()

    if args.local_controller:
        listen = args.local_controller.split(':')
        local_address = listen[0]
        local_port = int(listen[1])

    else:
        local_address = '127.0.0.1'
        local_port = 2342

    if args.super_controller:
        super_args = args.super_controller.split(':')
        super_address = super_args[0]
        super_port = int(super_args[1])

    else:
        super_address = '127.0.0.1'
        super_port = 6653

    myNet(super_ip=super_address, super_port=super_port, local_ip=local_address, local_port=local_port)


if __name__ == '__main__':
    setLogLevel('info')
    main()
