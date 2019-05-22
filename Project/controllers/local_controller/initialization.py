import argparse
import asyncore
from floodlight_client import FloodlightClient
from switch_server import Server
from distutils.util import strtobool


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--listen", help="address and port where the local server listens the switches")
    parser.add_argument("-s", "--super_agent", help="address and port to talk with the super agent")
    parser.add_argument("-f", "--flag", help= "True or False if the system needs the Learning phase")

    args = parser.parse_args()

    try:
        if args.listen:
            listen = args.listen.split(':')
            host_listen = listen[0]
            port_listen = int(listen[1])

        else:
            host_listen = 'localhost'
            port_listen = 22342

        if args.super_agent:
            super = args.super_agent.split(':')
            host_super = super[0]
            port_super = int(super[1])

        else:
            host_super = 'localhost'
            port_super = 8060

        if args.flag:
            flag = strtobool(args.flag)
        else:
            flag = False
    except ValueError:
        host_listen = 'localhost'
        port_listen = 2342
        host_super = 'localhost'
        port_super = 8060
        flag = True

    Server(host_listen, port_listen, host_super, flag)
    FloodlightClient(host=host_super, port=port_super)
    asyncore.loop()


if __name__ == '__main__':
    main()




