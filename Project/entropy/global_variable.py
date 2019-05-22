import os

class GlobalVariable:
    usr = '/home/giuggy/'
    no_traffic = True
    no_bins = False
    if no_bins:
        exp = 'no_bin'
    else:
        exp = 'yes_bin'
    if no_traffic:
        PATH_FEATURES = usr + 'Project/database/features_no_traffic'
        experiment = "experiment_without_traffic/"
    else:
        PATH_FEATURES = usr + 'Project/database/features'
        experiment = "experiment_with_traffic/"
    PATH = usr + 'Project/database/' + experiment
    try:
        os.mkdir(PATH)
    except FileExistsError:
        pass
    PATH_EXP = PATH + exp
    try:
        os.mkdir(PATH_EXP)
    except FileExistsError:
        pass
    PATH_PROB = PATH_EXP + '/probabilities'
    PATH_OBS = PATH_PROB + '/observations'
    PATH_ENTROPY = PATH_EXP + '/manual_entropy/'
    PATH_LOCAL = usr + 'Project/database/local/'
    save_pic = PATH_EXP + '/pictures/'
    save_txt = PATH_EXP + '_results/'
    try:
        os.mkdir(save_txt)
    except FileExistsError:
        pass
    try:
        os.mkdir(save_pic)
    except FileExistsError:
        pass
    name_dir_obs = "observations"
    LIMIT = 24
    TOTAL_PORTS = 65535
    round_val_bytes = 100
    round_val_pkt = 10
    DIR_V = 'computed_entropy_v'
    DIR_H = 'computed_entropy_h'
    day_dict = {1: 'attack_1',
                2: 'attack_2',
                3: 'attack_3',
                4: 'attack_4',
                5: 'normal'
                #2: 'attack_1',
                #3: 'attack_2',
                #4: 'attack_3',
                #5: 'attack_4'
                }
    host_dict = {'10:00:00:00:00:10': 'hmi',
                 '12:00:00:00:00:12': 'h1',
                 '22:00:00:00:00:22': 'h2',
                 '32:00:00:00:00:32': 'h3',
                 '44:00:00:00:00:44': 'h4',
                 '54:00:00:00:00:54': 'h5',
                 '64:00:00:00:00:64': 'h6',
                 '76:00:00:00:00:76': 'h7',
                 '86:00:00:00:00:86': 'h8',
                 '96:00:00:00:00:96': 'h9',
                 'a0:00:00:00:00:a0': 'h_s_1',
                 'b2:00:00:00:00:b2': 'h_s_2',
                 'c4:00:00:00:00:c4': 'h_s_3',
                 'd6:00:00:00:00:d6': 'h_s_4'
                 }
    switch_name = {'00:00:00:00:00:00:00:01': 'switch_1',
         '00:00:00:00:00:00:00:02': 'switch_2',
         '00:00:00:00:00:00:00:03': 'switch_3',
         '00:00:00:00:00:00:00:04': 'switch_4'}
    LIMIT_SNAP = 24

    features = {'attack_1': {'00:00:00:00:00:00:00:01': ['port_1_s_rx_pkt',
                                                         'port_1_s_tx_pkt',
                                                         'port_2_s_rx_pkt',
                                                         'port_2_s_tx_pkt',
                                                         'rst',
                                                         # 'tcp_connection',
                                                         'tcp_failed',
                                                         'tcp_port_counts'],
                             '00:00:00:00:00:00:00:02': ['h3_src_flow',
                                                         # 'h3_src_pkt',
                                                         'port_h3_rx_pkt',
                                                         'port_h3_tx_pkt',
                                                         'port_1_s_rx_pkt',
                                                         'port_1_s_tx_pkt',
                                                         'rst',
                                                         # 'tcp_connection',
                                                         'tcp_failed',
                                                         'tcp_port_counts'],
                             '00:00:00:00:00:00:00:03': ['h6_dst_flow',
                                                         # 'h6_dst_pkt',
                                                         'port_h6_rx_pkt',
                                                         'port_h6_tx_pkt',
                                                         'port_1_s_rx_pkt',
                                                         'port_1_s_tx_pkt',
                                                         'rst',
                                                         # 'tcp_connection',
                                                         'tcp_failed',
                                                         'tcp_port_counts'],
                             '00:00:00:00:00:00:00:04': ['port_1_s_rx_pkt',
                                                         'port_1_s_tx_pkt',
                                                         'rst',
                                                         # 'tcp_connection',
                                                         'tcp_failed',
                                                         'tcp_port_counts']},
                'attack_2': {'00:00:00:00:00:00:00:01': ['port_2_s_rx_pkt',
                                                         'port_2_s_tx_pkt',
                                                         'port_3_s_rx_pkt',
                                                         'port_3_s_tx_pkt',
                                                         'rst',
                                                         # 'tcp_connection',
                                                         'tcp_failed',
                                                         'tcp_port_counts'],
                             '00:00:00:00:00:00:00:02': ['port_1_s_rx_pkt',
                                                         'port_1_s_tx_pkt',
                                                         'rst',
                                                         # 'tcp_connection',
                                                         'tcp_failed',
                                                         'tcp_port_counts'],
                             '00:00:00:00:00:00:00:03': ['h4_src_flow',
                                                         # 'h4_src_pkt',
                                                         'port_h4_rx_pkt',
                                                         'port_h4_tx_pkt',
                                                         'port_1_s_rx_pkt',
                                                         'port_1_s_tx_pkt',
                                                         'rst',
                                                         # 'tcp_connection',
                                                         'tcp_failed',
                                                         'tcp_port_counts'],
                             '00:00:00:00:00:00:00:04': ['h7_dst_flow',
                                                         # 'h7_dst_pkt',
                                                         'port_h7_rx_pkt',
                                                         'port_h7_tx_pkt',
                                                         'port_1_s_rx_pkt',
                                                         'port_1_s_tx_pkt',
                                                         'rst',
                                                         # 'tcp_connection',
                                                         'tcp_failed',
                                                         'tcp_port_counts']},
                'attack_3': {'00:00:00:00:00:00:00:01': ['port_1_s_rx_pkt',
                                                         'port_1_s_tx_pkt',
                                                         'port_2_s_rx_pkt',
                                                         'port_2_s_tx_pkt',
                                                         'port_3_s_rx_pkt',
                                                         'port_3_s_tx_pkt',
                                                         'port_udp_counts',
                                                         'udp_connection'],
                             '00:00:00:00:00:00:00:02': [  # 'h2_dst_flow',
                                 'h2_dst_pkt',
                                 'port_h3_rx_pkt',
                                 'port_h3_tx_pkt',
                                 'port_1_s_rx_pkt',
                                 'port_1_s_tx_pkt',
                                 'port_udp_counts',
                                 'udp_connection'],
                             '00:00:00:00:00:00:00:03': ['port_1_s_rx_pkt',
                                                         'port_1_s_tx_pkt',
                                                         'port_udp_counts',
                                                         'udp_connection'],
                             '00:00:00:00:00:00:00:04': ['h8_src_flow',
                                                         # 'h8_src_pkt',
                                                         'port_h8_rx_pkt',
                                                         'port_h8_tx_pkt',
                                                         'port_1_s_rx_pkt',
                                                         'port_1_s_tx_pkt',
                                                         'port_udp_counts',
                                                         'udp_connection']},
                'attack_4': {'00:00:00:00:00:00:00:01': ['hmi_dst_flow',
                                                         # 'hmi_dst_pkt',
                                                         'tcp_port_counts',
                                                         'port_hmi_rx_pkt',
                                                         'port_hmi_tx_pkt',
                                                         'port_1_s_tx_pkt',
                                                         'port_2_s_rx_pkt',
                                                         'port_2_s_tx_pkt',
                                                         'port_3_s_rx_pkt',
                                                         'port_3_s_tx_pkt',
                                                         'rst',
                                                         # 'tcp_connection',
                                                         'tcp_failed',
                                                         'tcp_port_counts'],
                             '00:00:00:00:00:00:00:02': ['h1_dst_flow',
                                                         # 'h1_dst_pkt',
                                                         'h2_dst_flow',
                                                         # 'h2_dst_pkt',
                                                         'h3_src_flow',
                                                         # 'h3_src_pkt',
                                                         'port_1_s_rx_pkt',
                                                         'port_1_s_tx_pkt',
                                                         'rst',
                                                         # 'tcp_connection',
                                                         'tcp_failed',
                                                         'tcp_port_counts'],
                             '00:00:00:00:00:00:00:03': ['h4_dst_flow',
                                                         # 'h4_dst_pkt',
                                                         'h5_dst_flow',
                                                         # 'h5_dst_pkt',
                                                         'h6_dst_flow',
                                                         # 'h6_dst_pkt',
                                                         'rst',
                                                         # 'tcp_connection',
                                                         'tcp_failed',
                                                         'tcp_port_counts'],
                             '00:00:00:00:00:00:00:04': ['h7_dst_flow',
                                                         # 'h7_dst_pkt',
                                                         'h8_dst_flow',
                                                         # 'h8_dst_pkt',
                                                         'h9_dst_flow',
                                                         # 'h9_dst_pkt',
                                                         'rst',
                                                         # 'tcp_connection',
                                                         'tcp_failed',
                                                         'tcp_port_counts']}}


