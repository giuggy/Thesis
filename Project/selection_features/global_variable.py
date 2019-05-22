import os

class GlobalVariable:

    traffic = False
    usr = '/home/giuggy/'
    if traffic:
        PATH_DATABASE = usr + 'Project/database/features'
        traff = '/yes_traffic'
    else:
        PATH_DATABASE = usr + 'Project/database/features_no_traffic'
        traff = '/no_traffic'

    PATH = usr + 'Project/database/store_ml_features'
    try:
        os.mkdir(PATH)
    except FileExistsError:
        pass

    PATH2 = usr + 'Project/database/ml_evaluation'
    try:
        os.mkdir(PATH2)
    except FileExistsError:
        pass

    PATH_STORE = PATH + traff
    PATH_EVAL = usr + 'Project/database/ml_evaluation' + traff
    try:
        os.mkdir(PATH_EVAL)
    except FileExistsError:
        pass
    PATH_OBS = PATH_STORE + '/observations'
    LIMIT_SNAP = 24
    day_dict = {5: 'normal',
                1: 'attack_1',
                2: 'attack_2',
                3: 'attack_3',
                4: 'attack_4'
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

    max_val_dict = {'port_counts': 20,
                    'port_udp_counts': 10,
                    'tcp_failed': 30,
                    'unknown_protocol': 200}
