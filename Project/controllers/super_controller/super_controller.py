import asyncore
import argparse



class ServerHandler(asyncore.dispatcher_with_send):

    def handle_read(self):
        '''

        Function that handle the connection and the data from the switch
        '''
        print("Local controller says")
        data = self.recv(8192)
        print("--> Data: ", data)


class Server(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accepted(self, sock, addr):
        print('------------------------------------------------------------------')
        print('Incoming connection from %s' % repr(addr))
        ServerHandler(sock)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--listen", help="address and port where the super agent server listens the floodlight "
                                               "controller")

    args = parser.parse_args()

    if args.listen:
        listen = args.listen.split(':')
        host_listen = listen[0]
        port_listen = int(listen[1])

    else:
        host_listen = 'localhost'
        port_listen = 21717


    Server(host_listen, port_listen)
    asyncore.loop()


if __name__ == '__main__':
    main()
