import os

class GlobalVariables:
    usr = '/home/giuggy/'
    no_traffic = False
    SYN_FLAG = '0x2'
    RST_FLAG = '0x14'
    ACK_FLAG = '0x10'  # final ack of handshake
    WINDOW = 50
    TIMER = 60
    MAX_LAST_THREAD = 90
    LIMIT_SNAP = 24
    if no_traffic:
        PATH_DATABASE = usr + 'Project/database/features_no_traffic/'
    else:
        PATH_DATABASE = usr + 'Project/database/features/'
    try:
        os.mkdir(PATH_DATABASE)
    except FileExistsError:
        pass
    PATH_ENTROPY = usr + 'Project/database/entropy/'
    PATH_LOCAL = usr + 'Project/database/local/'
    PATH_DEBUG = usr + 'Project/debug/'
    info_counter = 0
