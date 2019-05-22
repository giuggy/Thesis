#!/usr/bin/env python
import argparse
import socket
from datetime import datetime


def connect_tcp(ip, port_number, delay):
    TCPsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCPsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPsock.settimeout(delay)
    try:
        TCPsock.connect((ip, port_number))
        output = True
        TCPsock.close()
    except:
        output = False
    return output


def scan_ports(host_ip, delay):
    start = datetime.now()
    for port in range(1, 10000):
        out = connect_tcp(host_ip, port, delay)
        if out:
            print("Port ", port, " :Open")
        else:
            print("Port ", port, " : Close")
    end = datetime.now()
    print("TIME: ", end - start)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", help="address of the target host")
    parser.add_argument("-d", "--delay", help="maximum delay time of the connection")

    args = parser.parse_args()

    if args.target:
        host = args.target
    else:
        host = '127.0.0.1'

    if args.delay:
        delay = int(args.delay)
    else:
        delay = 3
    scan_ports(host, delay)


if __name__ == '__main__':
    main()

