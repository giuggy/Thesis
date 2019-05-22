import psycopg2


class ConnectionDB:

    def __init__(self, name, user, host, passw):
        self.name = name
        self.user = user
        self.host = host
        self.passw = passw

        self.conn = psycopg2.connect(dbname=self.name, user=self.user, host=self.host, password=self.passw)
        self.cur = self.conn.cursor()

    def execute_op(self, operation, params):
        if params:
            self.cur.execute(operation, params)
            self.conn.commit()
        else:
            self.cur.execute(operation)

    def close(self):
        self.cur.close()
        self.conn.close()


''' in SERVER: HANDLE_ACCEPTED
obj = ServerHandler(sock)
obj.db_connection = ConnectionDB("super", "super", "localhost", "super")
'''
''' USAGE IN switch server.py statistics_to_super
operation = 'INSERT INTO features (time_stamp , mac , src_pkt , src_byte , src_flow , dst_pkt , dst_byte , \
                     dst_flow , rx_packets , tx_packets , rx_dropped , tx_dropped , rx_bytes , tx_bytes , rx_errors , \
                     tx_errors , rx_frame_err , rx_over_err , rx_crc_err , collisions , duration_sec , tcp_fail_p , \
                     tcp_rst_p ) \
                     VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

        self.db_connection.execute_op(operation, result)
'''