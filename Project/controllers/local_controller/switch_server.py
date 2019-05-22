import asyncore
import os
import sys
import time
import ast
import binascii
import threading
from datetime import datetime
from operator import add
from preprocessing import Preprocessing
from position import PositionApi
from thread_with_result import ThreadWithReturnValue, RepeatedTimer
from global_variable import GlobalVariables
from pyof.v0x04.common.utils import unpack_message
from pyof.v0x04.common.header import Type, Header
from pyof.v0x04.symmetric.echo_reply import EchoReply
from pyof.v0x04.symmetric.echo_request import EchoRequest
from pyof.v0x04.symmetric.hello import Hello
from pyof.v0x04.common.flow_match import Match, OxmOfbMatchField, OxmTLV, OxmClass, MatchType
from pyof.v0x04.controller2switch.multipart_request import AggregateStatsRequest, MultipartRequest, PortStatsRequest
from pyof.v0x04.controller2switch.common import MultipartType
from pyof.v0x04.controller2switch.features_request import FeaturesRequest
from pyof.foundation.exceptions import UnpackException
from pypacker.layer12 import ethernet, arp, lldp
from pypacker.layer3 import icmp, icmp6
from pypacker.layer4 import tcp, udp, sctp
from pprint import pprint
from socket import inet_aton, inet_pton, AF_INET6
import logging
import warnings

warnings.filterwarnings("error")


class ServerHandler(asyncore.dispatcher_with_send):
    name = None
    msg = None
    bytes_msg = None
    time_stamp = None
    time_0 = None
    data_tmp = b''
    first_tmp = b''

    flag_learning = None
    features = False
    variables = GlobalVariables
    path_db = ""
    path_entropy = ""
    db_connection = None
    super_address = '127.0.0.1'
    super_thread = None

    hosts = None
    position = None
    day = 0

    tcp_entries = {}
    counter_rst = 0
    counter_tcp_connection = 0
    dst_port = set()
    dst_udp_port = set()
    no_tcp_connection = 0
    unknown_protocol = 0

    msg_port = None

    msg_tmp = None
    msg_aggr = []

    def __create_directories(self):
        try:
            os.mkdir(self.path_db)
        except FileExistsError:
            if self.flag_learning:
                os.rmdir(self.path_db)
                os.mkdir(self.path_db)
        try:
            os.mkdir(self.variables.PATH_LOCAL + self.name)
        except FileExistsError:
            pass

        # try:
            # os.mkdir(self.path_entropy)
        # except FileExistsError:
        #    if self.flag_learning:
        #        os.remove(self.path_entropy)
        #        os.mkdir(self.path_entropy)

        data = {"position": self.position, "host": self.hosts}
        with open(self.variables.PATH_LOCAL + self.name + "/info_" + self.name + "_" + str(self.variables.info_counter)
                  + ".txt", 'w') as f:
            pprint(data, f)

        logging.basicConfig(filename=GlobalVariables.PATH_DEBUG + self.name + ".txt", level=logging.DEBUG,
                            format=' [%(levelname)s] (%(threadName)-9s) %(message)s', )

    def hello_reply(self):
        '''

        Handshake: function to reply to Hello from the switch
        '''

        reply = Hello()
        binary_reply = reply.pack()
        self.send(binary_reply)
        print("** Server ** responds with ", reply.header.message_type)
        reply = FeaturesRequest()
        binary_reply = reply.pack()
        self.send(binary_reply)
        print("****** ", reply.header.message_type)
        print("<< " + str(datetime.now()) + " Features Request")

    def features_reply(self):
        '''

        Function that handle features of the switch
        '''
        print(self.msg.header.message_type)
        print(">> " + str(datetime.now()) + " Features Reply")
        if not self.features:
            self.features = True
            response = self.msg
            mac = response.datapath_id.value
            self.name = mac
            getter = PositionApi(self.super_address, mac)
            self.hosts = getter.get()
            if len(self.hosts) != 0:
                self.position = 'L'
            else:
                self.position = 'B'
            print("TIMER BEFORE REPEATED TIMER ", self.variables.TIMER)
            self.super_thread = RepeatedTimer(self.variables.TIMER, self.statistics_to_super)
            print("TIMER AFTER TIMER ", self.variables.TIMER)
            self.path_db = self.variables.PATH_DATABASE + mac + "/"
            self.path_entropy = self.variables.PATH_ENTROPY + mac + "/"
            self.__create_directories()

    def echo_reply(self):
        '''

        Handshake: function to reply to EchoRequest from the switch and call also the function to ask statistics
        '''

        reply = EchoReply()
        binary_reply = reply.pack()
        self.send(binary_reply)
        print("** Server ** responds with ", reply.header.message_type)

    def statistics_reply(self):
        '''

        Function that handle statistics
        '''
        stats = str(self.msg.body[0])
        if 'PortStats' in stats:
            self.msg_port = self.msg.body
        else:
            self.msg_tmp = self.msg

    def __port_request__(self):
        stats = MultipartRequest(xid=len(self.hosts) + 1, multipart_type=MultipartType.OFPMP_PORT_STATS, flags=0,
                                 body=PortStatsRequest())
        binary_stats = stats.pack()
        self.send(binary_stats)
        print("<< " + str(datetime.now()) + " ** Server from PORT thread** asks ", stats.header.message_type)

    def __send_aggregation_ip__(self, val, oxm_field, ip_address, n_id):
        tlv1 = OxmTLV(oxm_class=OxmClass.OFPXMC_OPENFLOW_BASIC,
                      oxm_field=OxmOfbMatchField.OFPXMT_OFB_ETH_TYPE,
                      oxm_hasmask=False, oxm_value=val)
        tlv2 = OxmTLV(oxm_class=OxmClass.OFPXMC_OPENFLOW_BASIC,
                      oxm_field=oxm_field,
                      oxm_hasmask=False, oxm_value=ip_address)
        match = Match(match_type=MatchType.OFPMT_OXM, oxm_match_fields=[tlv1, tlv2])

        stats = MultipartRequest(xid=n_id, multipart_type=MultipartType.OFPMP_AGGREGATE, flags=0,
                                 body=AggregateStatsRequest(match=match))
        binary_stats = stats.pack()
        self.send(binary_stats)
        print(" ** Server from DOS thread ** asks ", stats.header.message_type)

    def __aggregate_request_ip__(self, host, n_id_src, n_id_dst):
        try:
            ip_address = inet_aton(host)
            val = b'\x08\x00'
            oxm_field_src = OxmOfbMatchField.OFPXMT_OFB_IPV4_SRC
            oxm_field_dst = OxmOfbMatchField.OFPXMT_OFB_IPV4_DST
        except:
            ip_address = inet_pton(AF_INET6, host)
            val = b'\x86\xdd'
            oxm_field_src = OxmOfbMatchField.OFPXMT_OFB_IPV6_SRC
            oxm_field_dst = OxmOfbMatchField.OFPXMT_OFB_IPV6_DST
        self.__send_aggregation__(val=val, oxm_field=oxm_field_src, ip_address=ip_address, n_id=n_id_src)
        self.__send_aggregation__(val=val, oxm_field=oxm_field_dst, ip_address=ip_address, n_id=n_id_dst)

    def __send_aggregation__(self, oxm_field, mac_address, n_id):

        tlv = OxmTLV(oxm_class=OxmClass.OFPXMC_OPENFLOW_BASIC,
                     oxm_field=oxm_field, oxm_hasmask=False, oxm_value=mac_address)
        match = Match(match_type=MatchType.OFPMT_OXM, oxm_match_fields=[tlv])

        stats = MultipartRequest(xid=n_id, multipart_type=MultipartType.OFPMP_AGGREGATE, flags=0,
                                 body=AggregateStatsRequest(match=match))
        binary_stats = stats.pack()
        self.send(binary_stats)
        print("<< " + str(datetime.now()) + " ** Server from DOS thread ** asks ", stats.header.message_type)

    def __aggregate_request__(self, mac, n_id, pos):

        mac_address = binascii.unhexlify(mac.replace(':', ''))

        if pos == "src":
            oxm_field = OxmOfbMatchField.OFPXMT_OFB_ETH_SRC
        else:
            oxm_field = OxmOfbMatchField.OFPXMT_OFB_ETH_DST

        self.__send_aggregation__(oxm_field=oxm_field, mac_address=mac_address, n_id=n_id)

    def error_probabilities(self):
        logging.debug('Starting Error, TIME ' + str(datetime.now()))
        while self.msg_port is None:
            time.sleep(0.1)
        print(">> " + str(datetime.now()) + " RECEIVED PORT MSG")
        msg_body = self.msg_port
        self.msg_port = None

        res = []
        for msg in msg_body:
            port_no = str(msg.port_no.value)
            if port_no in list(self.hosts.keys()):
                host_ip = self.hosts[str(msg.port_no.value)][0]
                host_mac = self.hosts[str(msg.port_no.value)][1]
                values = list(self.hosts.values())
                ip_list, mac_list = zip(*values)
                host_idx = 'h' + str(mac_list.index(host_mac) + 1)
            elif len(port_no) < 2:
                host_ip = 'switch_port'
                host_mac = 'switch_port'
                host_idx = 's'
            else:
                host_mac = None
                host_ip = None
            if host_mac is not None:
                err_dic = {
                    'port_no': port_no,
                    'host_ip': host_ip,
                    'host_mac': host_mac,
                    'host_idx': host_idx,
                    'rx': {
                        'pkt': msg.rx_packets.value,
                        'drop': msg.rx_dropped.value,
                        'bytes': msg.rx_bytes.value,
                        'error': msg.rx_errors.value,
                        'frame_err': msg.rx_frame_err.value,
                        'over_err': msg.rx_over_err.value,
                        'crc_err': msg.rx_crc_err.value
                    },
                    'tx': {
                        'pkt': msg.tx_packets.value,
                        'drop': msg.tx_dropped.value,
                        'bytes': msg.tx_bytes.value,
                        'error': msg.tx_errors.value
                    },
                    "collision": msg.collisions.value,
                    "duration_sec": msg.duration_sec.value
                }
                res.append(err_dic)
        logging.debug('Exiting Error, TIME ' + str(datetime.now()))
        return res

    def dos_probabilities(self):
        logging.debug('Starting DOS, TIME ' + str(datetime.now()))
        print(">> " + str(datetime.now()) + " DOS STATS")
        results = self.msg_aggr
        self.msg_aggr = []

        val = len(self.hosts)
        tmp = []
        tmp_host = []
        result = []
        for msg in results:
            idx = msg.header.xid.value
            body_msg = msg.body
            src = []
            dst = []
            for body in body_msg:
                values = list(self.hosts.values())
                ip_list, mac_list = zip(*values)
                lst = [body.packet_count.value, body.byte_count.value, body.flow_count.value]
                if idx < val:
                    ip = ip_list[idx]
                    mac = mac_list[idx]
                    host_idx = mac_list.index(mac) + 1
                    if len(src) == 0:
                        src = lst
                    else:
                        src = list(map(add, src, lst))
                else:
                    ip = ip_list[idx - len(self.hosts)]
                    mac = mac_list[idx - len(self.hosts)]
                    host_idx = mac_list.index(mac) + 1
                    if len(dst) == 0:
                        dst = lst
                    else:
                        dst = list(map(add, dst, lst))
                if idx < val:
                    src_dic = {'host': str(ip),
                               'mac': str(mac),
                               'host_idx': 'h' + str(host_idx),
                               'src': {"pkt": src[0], "bytes": src[1], "flow": src[2]}}
                    if mac in tmp_host:
                        dic = list(filter(lambda x: x['mac'] == str(mac), tmp))[0]
                        dic.update(src_dic)
                        result.append(dic)
                    else:
                        tmp_host.append(mac)
                        tmp.append(src_dic)
                else:
                    dst_dic = {'host': str(ip),
                               'mac': str(mac),
                               'host_idx': 'h' + str(host_idx),
                               'dst': {"pkt": dst[0], "bytes": dst[1], "flow": dst[2]}}
                    if mac in tmp_host:
                        dic = list(filter(lambda x: x['mac'] == str(mac), tmp))[0]
                        dic.update(dst_dic)
                        result.append(dic)
                    else:
                        tmp_host.append(mac)
                        tmp.append(dst_dic)

        logging.debug('Exiting DOS, TIME ' + str(datetime.now()))
        return result

    def __tcp_handler(self, pack):

        ip_src, ip_dst, port_src, port_dst = pack.src, pack.dst, pack.tcp.sport, pack.tcp.dport
        if hex(pack.tcp.flags) == self.variables.SYN_FLAG:
            entry = (ip_src, ip_dst, port_src, port_dst)
            self.dst_port.add(port_dst)
            if entry in self.tcp_entries:
                self.tcp_entries[entry] = self.tcp_entries[entry] + [self.time_stamp]
            else:
                self.tcp_entries[entry] = [self.time_stamp]

        elif hex(pack.tcp.flags) == self.variables.RST_FLAG:
            entry = (ip_dst, ip_src, port_dst, port_src)
            if entry in self.tcp_entries:
                self.counter_rst += 1
                stamps = self.tcp_entries.pop(entry)
                stamps.remove(min(stamps))
                if len(stamps) != 0:
                    self.tcp_entries[entry] = stamps

        elif hex(pack.tcp.flags) != self.variables.ACK_FLAG:
            entry = (ip_src, ip_dst, port_src, port_dst)
            if entry in self.tcp_entries:
                self.counter_tcp_connection += 1
                stamps = self.tcp_entries.pop(entry)
                stamps.remove(min(stamps))
                if len(stamps) != 0:
                    self.tcp_entries[entry] = stamps

    def syn_analyzer(self):
        data = self.msg.data.value
        bytes_data = self.bytes_msg
        flag = 0
        try:
            pack = ethernet.Ethernet(data)
        except Exception:
            self.data_tmp = bytes_data
            flag = 2
        if flag != 2:
            print(data)
            print("LEN ", len(data))
            print("LEN pack ", len(pack))
            print("DATA ", pack.__len__())
            pack = ethernet.Ethernet(data)
            if len(data) != len(pack):
                self.data_tmp = bytes_data
                flag = 1
            else:
                try:
                    if pack.arp is not None:
                        self.data_tmp = b''
                        flag = 21
                except AttributeError:
                    try:
                        if pack.lldp is not None:
                            self.data_tmp = b''
                            flag = 22
                    except AttributeError:
                        pass
        if flag == 0:
            values = list(self.hosts.values())
            address, mac_list = zip(*values)
            dic_dst = list(filter(lambda x: x == pack.dst_s, mac_list))
            dic_src = list(filter(lambda x: x == pack.src_s, mac_list))
            if len(dic_dst) > 0 or len(dic_src) > 0:
                with open(GlobalVariables.PATH_LOCAL + self.name + "/packet.txt", "a") as f:
                    f.write(str(data) + '\n' + str(pack) + '\n')
                try:
                    print("IP ", pack.ip.len)
                    print("IP2 ", pack.ip.__len__())
                    if pack.ip.len > pack.ip.__len__():
                        self.data_tmp = bytes_data
                        flag = 25
                    elif pack.ip.len + 14 > len(data):
                        print("IP TOT ", pack.ip.len)
                        self.data_tmp = bytes_data
                        flag = 22
                    elif pack.ip[tcp.TCP] is not None:
                        self.__tcp_handler(pack.ip)
                    elif pack.ip[icmp.ICMP] is not None:
                        pass
                    elif pack.ip[udp.UDP] is not None:
                        self.dst_udp_port.add(pack.ip.udp.dport)
                        self.no_tcp_connection += 1
                    elif pack.ip[sctp.SCTP] is not None:
                        pass
                    else:
                        self.unknown_protocol += 1
                except AttributeError:
                    try:
                        print("IP ", pack.ip6.dlen + pack.ip6.header_len)
                        print("IP2 ", pack.ip6.__len__())
                        if (pack.ip6.dlen + pack.ip6.header_len) > pack.ip6.__len__():
                            self.data_tmp = bytes_data
                            flag = 29
                        elif (pack.ip6.dlen + pack.ip6.header_len) + 14 > len(data):
                            self.data_tmp = bytes_data
                            flag = 290
                        elif pack.ip6[tcp.TCP] is not None:

                            self.__tcp_handler(pack.ip6)
                        elif pack.ip6[icmp6.ICMP6] is not None:
                            pass
                        elif pack.ip6[udp.UDP] is not None:
                            self.dst_udp_port.add(pack.ip6.udp.dport)
                            self.no_tcp_connection += 1
                        elif pack.ip6[sctp.SCTP] is not None:
                            pass
                        else:
                            self.unknown_protocol += 1
                    except AttributeError:
                        self.data_tmp = bytes_data
                        flag = 10
            else:
                print("NO IN MY NETWORK")
                try:
                    print("IP ", pack.ip.len)
                    print("IP2 ", pack.ip.__len__())
                    if pack.ip.len > pack.ip.__len__():
                        self.data_tmp = bytes_data
                        flag = 25
                    elif pack.ip.len + 14 > len(data):
                        print("IP TOT ", pack.ip.len)
                        self.data_tmp = bytes_data
                        flag = 22
                except AttributeError:
                    try:
                        print("IP ", pack.ip6.dlen + pack.ip6.header_len)
                        print("IP2 ", pack.ip6.__len__())
                        if (pack.ip6.dlen + pack.ip6.header_len) > pack.ip6.__len__():
                            self.data_tmp = bytes_data
                            flag = 29
                        elif (pack.ip6.dlen + pack.ip6.header_len) + 14 > len(data):
                            self.data_tmp = bytes_data
                            flag = 290
                    except AttributeError:
                        self.data_tmp = bytes_data
                        flag = 10
        print("FLAG ", flag)

    def syn_probabilities(self):

        tmp = self.time_0
        logging.debug('Starting SYN, TIME ' + str(datetime.now()))
        counter_tcp_failed = 0
        for e in self.tcp_entries.copy().items():
            values = list(map(lambda x: x - tmp, e[1]))
            filter_val = list(filter(lambda x: x < self.variables.WINDOW, values))
            if len(filter_val) == len(values):
                counter_tcp_failed += len(filter_val)
                self.tcp_entries.pop(e[0])
            elif len(filter_val) < len(values):
                counter_tcp_failed += len(values) - len(filter_val)
                self.tcp_entries[e[0]] = list(map(lambda x: x + tmp, filter_val))
        dic = {"tcp_failed": counter_tcp_failed, "tcp_connection": self.counter_tcp_connection, "rst": self.counter_rst,
               "udp_connection": self.no_tcp_connection, "port_counts": len(self.dst_port),
               "unknown_protocol": self.unknown_protocol, "port_udp_counts": len(self.dst_udp_port)}
        logging.debug('Exiting SYN, TIME ' + str(datetime.now()))
        return dic

    def __handle_request(self, mac_list):
        print("HANDLE REQUEST*****************************************")
        t = time.time()
        max_val = len(mac_list)*2
        idx = 0
        idx_lst = []

        while idx < max_val:
            print("<< Send idx: ", idx, "Time: ", datetime.now())
            if idx < max_val/2:
                tmp = idx
                pos = "src"
            else:
                tmp = idx - int(max_val/2)
                pos = "dst"
            self.__aggregate_request__(mac=mac_list[tmp], n_id=idx, pos=pos)
            while self.msg_tmp is None:
                time.sleep(0.1)
                pass

            if self.msg_tmp.header.xid.value != idx:
                self.msg_tmp = None
            else:
                print(">> Receive idx: ", idx, "Time: ", datetime.now())
                self.msg_aggr.append(self.msg_tmp)
                idx_lst.append(idx)
                self.msg_tmp = None
                idx += 1
        end = time.time()
        print("DELTA REQUEST ", end - t)

    def statistics_to_super(self):

        start = time.time()
        logging.debug('Starting Super, TIME ' + str(datetime.now()))
        print("TIMER SUPER TIMER ", self.variables.TIMER)
        print("NUMBER OF THREAD ", threading.active_count())

        self.time_0 = time.time()
        self.__port_request__()
        t1 = None
        values = list(self.hosts.values())
        address, mac_list = zip(*values)
        print(values)
        if self.position == 'L':
            self.__handle_request(mac_list)
            t1 = ThreadWithReturnValue(target=self.dos_probabilities)

        t2 = ThreadWithReturnValue(target=self.error_probabilities)
        t3 = ThreadWithReturnValue(target=self.syn_probabilities)

        t2.start()
        t3.start()

        if t1 is not None:
            t1.start()
            dos_stats = t1.join()
        err_stats = t2.join()
        syn_stats = t3.join()
        self.dst_port = set()
        self.dst_udp_port = set()
        self.counter_tcp_connection = 0
        self.counter_rst = 0
        self.no_tcp_connection = 0
        self.unknown_protocol = 0

        if not err_stats:
            print("EXIT")
            return

        time_stamp = str(datetime.now())
        if t1 is not None:
            result = {"time_stamp": time_stamp, "switch_mac": self.name, "host_stats":  dos_stats,
                      "port_stats": err_stats, "connection_stats": syn_stats}
        else:
            result = {"time_stamp": time_stamp, "switch_mac": self.name, "port_stats": err_stats,
                      "connection_stats": syn_stats}

        with open(self.path_db + time_stamp + '.txt', 'w') as f:
            pprint(result, f)

        # self.flag_learning, count, self.day = Preprocessing(path=self.path_entropy, day=self.day)\
        #     .probability_calculation(result, self.flag_learning)

        print("END NUMBER OF THREAD ", threading.active_count())

        end = time.time()
        delta = end - start
        logging.debug('Exiting super, TIME ' + str(datetime.now()))

        print("TIME: ", delta)

    def handle_empty(self):
        reply = EchoRequest()
        binary_reply = reply.pack()
        self.send(binary_reply)
        print("** Server ** responds with ", reply.header.message_type)

    @staticmethod
    def handle_echo():
        print("** Switch ** responds with an ECHO REPLY")

    @staticmethod
    def __get_len_pkt__(data):

        header = Header()
        head_size = header.get_size()
        head_buf = data[:head_size]
        header.unpack(head_buf)
        return header.length.value

    def handle_read(self):
        '''

        Function that handle the connection and the data from the switch
        '''
        print("Switch says")
        data = self.recv(8192)
        print("DATE ", datetime.now())
        print("--> Data: ", data)
        if self.data_tmp != b'':
            data = self.data_tmp + data
        else:
            data = self.first_tmp + data
        time_stamp = time.time()
        print("--> NEW Data: ", data)
        self.data_tmp = b''
        self.first_tmp = b''
        msg_queue = []
        data_queue = []
        if data:

            while data:
                try:
                    data_len = self.__get_len_pkt__(data)
                except UnpackException as e:
                    print(e)
                    self.first_tmp = data
                    data = []
                try:
                    first, data = data[:data_len], data[data_len:]
                except UnboundLocalError as e:
                    print(e)
                try:
                    msg_queue.append(unpack_message(first))
                    data_queue.append(first)
                except ValueError as e:
                    print(e)
                    if len(first) == 0:
                        data = []
                except UnboundLocalError as e:
                    print(e)
                except Exception as e:
                    self.first_tmp = first
                    print(e)

            self.time_stamp = time_stamp
            while msg_queue:
                self.msg = msg_queue.pop(0)
                self.bytes_msg = data_queue.pop(0)
                print("--> Message: ", self.msg.header.message_type)
                print()
                try:
                    self.header_type[self.msg.header.message_type](self)
                except AttributeError as e:
                    print(e)
                except Exception as e:
                    print(e)
        else:
            print("HERE")
            self.handle_empty()

    header_type = {
        Type.OFPT_HELLO: hello_reply,
        Type.OFPT_ECHO_REQUEST: echo_reply,
        Type.OFPT_ECHO_REPLY: handle_echo,
        Type.OFPT_MULTIPART_REPLY: statistics_reply,
        Type.OFPT_FEATURES_REPLY: features_reply,
        Type.OFPT_PACKET_IN: syn_analyzer
    }


class Server(asyncore.dispatcher):

    def __init__(self, host, port, super_address, flag):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.super_address = super_address
        self.flag_learning = flag

    def handle_accepted(self, sock, addr):
        print('------------------------------------------------------------------')
        print('Incoming connection from %s' % repr(addr))
        ServerHandler(sock).flag_learning = self.flag_learning