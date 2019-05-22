import os
import ast
from global_variable import GlobalVariable
from pprint import pprint


variables = GlobalVariable
attacks = {1: 'switch 2', 2: 'switch 3', 3: 'switch 4', 4: 'switch 2'}
targets = {1: 'switch 3', 2: 'switch 4', 3: 'switch 2', 4: 'all hosts'}

hosts = {'00:00:00:00:00:00:00:01': ['hmi', 'switch2', 'switch3', 'switch4'],
         '00:00:00:00:00:00:00:02': ['h1', 'h2', 'h3'],
         '00:00:00:00:00:00:00:03': ['h4', 'h5', 'h6'],
         '00:00:00:00:00:00:00:04': ['h7', 'h8', 'h9']}
s1 = '00:00:00:00:00:00:00:01'
s2 = '00:00:00:00:00:00:00:02'
s3 = '00:00:00:00:00:00:00:03'
s4 = '00:00:00:00:00:00:00:04'
switch_hmi = s1
weight_attack = 2
weight_normal = 0.2
weight_sw = 0.2
p_weight_attack = 2
p_weight_normal = 0.1
p_weight_sw = 0.2
YELLOW = 1
ORANGE = 3
RED = 5
error = 0.3
p_ORANGE = 1
p_RED = 2


def help_localization(score, thresh):
    low = thresh + error
    up = low + p_ORANGE
    upp = up + p_RED
    if score <= low:
        res = 'GREEN'
    elif low < score <= up:
        res = 'YELLOW'
    elif up < score <= upp:
        res = 'ORANGE'
    elif score > upp:
        res = 'RED'
    return res


def localization(dictionary, thresh):
    result = {}
    for sw in dictionary:
        if '1' in sw:
            weight = 1
        else:
            weight = 1
        result[sw] = {}
        for lst in dictionary[sw]['host']:
            print('ciao ', sw)
            pprint(lst)
            hosts, scores = zip(*lst)
            h = hosts[0].split('_')[0]
            s = hosts[0].split('_')[1]
            d = hosts[1].split('_')[1]
            score = round(sum(scores) * weight, 2)
            score1 = round(scores[0] * weight, 2)
            score2 = round(scores[1] * weight, 2)
            st = help_localization(score, thresh[sw][h])
            s1 = help_localization(score1, thresh[sw][h])
            s2 = help_localization(score2, thresh[sw][h])
            if (s1 == 'RED' and s2 == 'RED') or (s1 == 'RED' and s2 == 'ORANGE') or (s1 == 'RED' and s2 == 'YELLOW') \
                or (s1 == 'ORANGE' and s2 == 'RED') or (s1 == 'ORANGE' and s2 == 'ORANGE') or  (s1 == 'ORANGE' and \
                                                                                                s2 == 'YELLOW'):
                alarm = 'DANGEROUS'
            else:
                alarm = 'CORRECT'

            result[sw][h] = [('tot', st, score), (s, s1, score1), (d, s2, score2), alarm]
        for lst in dictionary[sw]['port']:
            ports, scores = zip(*lst)
            p = ports[0].split('_')[0]
            score = round(sum(scores), 2)
            score1 = round(scores[0], 2)
            score2 = round(scores[1], 2)
            st = help_localization(score, thresh[sw][p])
            s1 = help_localization(score1, thresh[sw][p])
            s2 = help_localization(score2, thresh[sw][p])
            if (s1 == 'RED' and s2 == 'RED') or (s1 == 'RED' and s2 == 'ORANGE') or (s1 == 'RED' and s2 == 'YELLOW') \
                or (s1 == 'ORANGE' and s2 == 'RED') or (s1 == 'ORANGE' and s2 == 'ORANGE') or  (s1 == 'ORANGE' and \
                                                                                                s2 == 'YELLOW') \
                or (s1 == 'YELLOW' and s2 == 'RED') or (s1 == 'YELLOW' and s2 == 'ORANGE') or  (s1 == 'YELLOW' and \
                                                                                                s2 == 'YELLOW'):
                alarm = 'DANGEROUS'
            else:
                alarm = 'CORRECT'
            result[sw][p] = [('tot', st, score), (s, s1, score1), (d, s2, score2), alarm]
        tcp_conn = sum(dictionary[sw]['tcp _connection']) + sum(list(map(lambda x: x * weight_attack,
                                                                     dictionary[sw]['tcp _failed'])))
        score1 = round(tcp_conn, 2)
        st = help_localization(score1, thresh[sw]['tcp'])
        result[sw]['tcp'] = (st, score1)
        score2 = round(sum(dictionary[sw]['udp _connection']), 2)
        st = help_localization(score2, thresh[sw]['udp'])
        result[sw]['udp'] = (st, score2)
    return result


def help_dic(num, key):
    '''
        elif 'src_flow' in key:
            k = num + '_src_flow'
        elif 'dst_flow' in key:
            k = num + '_dst_flow'
    '''

    if 'src_pkt' in key or 'src_flow' in key: # or 'src_bytes' in key:
        k = num + '_src'
    elif 'tx_pkt' in key:
        # k = num + '_tx_pkt'
        k = num + '_tx_pkt'
    elif 'dst_pkt' in key or 'dst_flow' in key: # or 'dst_bytes' in key:
        k = num + '_dst'
    elif 'rx_pkt' in key:
        #k = 'rx_pkt'
        k = num + '_rx_pkt'

    else:
        return None

    return k


def particular_score(switch, dictionary):

    res = {}
    for key in dictionary:
        if key == "tcp_connection":
            val = sum(dictionary[key])
            try:
                res['tcp _connection'].append(val)
            except KeyError:
                res['tcp _connection'] = [val]
        elif "tcp_failed" in key:
            val = sum(dictionary[key])
            try:
                res['tcp _failed'].append(val)
            except KeyError:
                res['tcp _failed'] = [val]
        elif key == "udp_connection":
            val = sum(dictionary[key])
            try:
                res['udp _connection'].append(val)
            except KeyError:
                res['udp _connection'] = [val]
        else:
            name_lst = key.split("_")
            if 'src' in key:
                val1 = sum(dictionary[key])
                # _" + name_lst[len(name_lst) - 1]
                val2 = sum(dictionary[name_lst[0] + "_dst"])
                # _" + name_lst[len(name_lst) - 1
                key2 = name_lst[0] + "_dst"
                try:
                    #res['host'].append([(key, val1)])
                    res['host'].append([(key, val1), (key2, val2)])
                except KeyError:
                    res['host'] = [[(key, val1), (key2, val2)]]
                    #res['host'] = [[(key, val1)]]
            elif 'rx' in key:
                val1 = dictionary[key][0]
                val2 = dictionary[name_lst[0] + "_tx_" + name_lst[len(name_lst) - 1]][0]
                key2 = name_lst[0] + "_tx_" + name_lst[len(name_lst) - 1]
                try:
                    res['port'].append([(key, val1), (key2, val2)])
                    #res['port'].append([(key, val1)])
                except KeyError:
                    res['port'] = [[(key, val1), (key2, val2)]]
                    #res['port'] = [[(key, val1)]]
    pprint(res)

    return res


def verification_network(dictionary, level):
    print('LEVEL ', level)
    low = level[0]
    up = level[1]
    upp = level[2]
    c_l = level[3]
    c_u = level[4]
    c_uu = level[5]
    sw_status = {}
    for status in dictionary:
        print("STATUS", status)
        sw_status[status] = {}
        #if status is not 'normal':
        for sw in dictionary[status]:
            score = dictionary[status][sw][0]
            if score <= low:
                sw_status[status][sw] = 'GREEN'
            elif low < score <= up:
                sw_status[status][sw] = 'YELLOW'
            elif up < score <= upp:
                sw_status[status][sw] = 'ORANGE'
            elif score > upp:
                sw_status[status][sw] = 'RED'
            score_conn = dictionary[status][sw][1]
            if score_conn <= c_l:
                st = 'GREEN'
            elif c_l < score_conn <= c_u - YELLOW:
                st = 'YELLOW'
            elif c_u - YELLOW < score_conn <= c_u:
                st = "ORANGE"
            elif score_conn > c_u:
                st = 'RED'
            print('SWITCH ', sw, "STATUS ", sw_status[status][sw], score, "ONLY CONN ", st, score_conn)
    return sw_status


def set_network_threshold(normal):
    low = 0.0
    low_conn = 0.0
    #lst= []
    print('NORMAL ', normal)
    for sw in normal:
        if '1' in sw:
            low += weight_sw * normal[sw][0]
            low_conn += weight_sw * normal[sw][1]
            #lst.append(weight_sw * normal[sw])
        else:
            low += normal[sw][0]
            low_conn += normal[sw][1]
            #lst.append(normal[sw])
        print('LOW CONN ', low_conn)
    low = round(low/len(normal))
    up = low + ORANGE + error
    upp = low + RED + error
    return [low + error, up, upp, low_conn, low_conn + ORANGE + error, upp + RED]


def set_particular_threshold(normal):

    thresh = {}
    weight = 1
    for sw in normal:
        thresh[sw] = {}

        for h in normal[sw]['host']:
            hosts, score = zip(*h)
            host_name = hosts[0].split('_')[0]
            thresh[sw][host_name] = round(sum(score)*weight, 2) + error
        for p in normal[sw]['port']:
            ports, score = zip(*p)
            port_name = ports[0].split('_')[0]
            thresh[sw][port_name] = round(sum(score)*weight, 2) + error
        tcp_conn = sum(normal[sw]['tcp _connection']) + sum(list(map(lambda x: x*weight_attack,
                                                                     normal[sw]['tcp _failed'])))
        thresh[sw]['tcp'] = round(tcp_conn, 2) + error
        thresh[sw]['udp'] = round(sum(normal[sw]['udp _connection']), 2) + error
    return thresh


def score_switch(switch, dictionary):
    numerator = 0.0
    denominator = len(hosts[switch])
    conn_score = 0.0
    for key in dictionary:
        if 'tcp' in key or 'udp' in key:
            if 'fail' in key or 'udp' in key:
                val = sum(list(map(lambda x: x*weight_attack, dictionary[key])))
            else:
                val = sum(list(map(lambda x: x*weight_normal, dictionary[key])))
            conn_score += val
        else:
            numerator += sum(dictionary[key])
    score = round((numerator / denominator) + conn_score, 2)
    return [score, round(conn_score, 2)]


def division_fun(switch, dictionary, time='reference'):
    host = hosts[switch]
    division = {}
    for key, value in dictionary.items():
        val = dictionary[key][time]
        #if val is not None:
          #  val = round(val)
        if 'rst' == key or 'tcp_failed' in key:
            try:
                division['tcp_failed'].append(val)
            except KeyError:
                division['tcp_failed'] = [val]
        elif 'tcp_port' in key or 'tcp_connection' in key:
            try:
                division['tcp_connection'].append(val)
            except KeyError:
                division['tcp_connection'] = [val]
        elif 'udp' in key:
            try:
                division['udp_connection'].append(val)
            except KeyError:
                division['udp_connection'] = [val]

        else:
            if len(host) < 4:
                if host[0] in key:
                    k = help_dic(host[0], key)
                    if k is not None:
                        try:
                            division[k].append(val)
                        except KeyError:
                            division[k] = [val]
                elif host[1] in key:
                    k = help_dic(host[1], key)
                    if k is not None:
                        try:
                            division[k].append(val)
                        except KeyError:
                            division[k] = [val]
                elif host[2] in key:
                    k = help_dic(host[2], key)
                    if k is not None:
                        try:
                            division[k].append(val)
                        except KeyError:
                            division[k] = [val]
                #elif 's' in key:
                #    k = help_dic('switch1', key)
                  #  if k is not None:
                 #       try:
                  #          division[k].append(val)
                  #      except KeyError:
                   #         division[k] = [val]
            else:
                if host[0] in key:
                    k = help_dic(host[0], key)
                    if k is not None:
                        try:
                            division[k].append(val)
                        except KeyError:
                            division[k] = [val]
                elif '1_s' in key:
                    k = help_dic('switch2', key)
                    if k is not None:
                        try:
                            division[k].append(val)
                        except KeyError:
                            division[k] = [val]
                elif '2_s' in key:
                    k = help_dic('switch3', key)
                    if k is not None:
                        try:
                            division[k].append(val)
                        except KeyError:
                            division[k] = [val]
                elif '3_s' in key:
                    k = help_dic('switch4', key)
                    if k is not None:
                        try:
                            division[k].append(val)
                        except KeyError:
                            division[k] = [val]
    return division


if __name__ == '__main__':
    #  'att1': {}, 'att3': {}, 'att4': {}
    information_tot = {'normal': {}, 'att1': {}, 'att2': {}, 'att3': {}, 'att4': {}}
    score_tot = {'normal': {}, 'att1': {}, 'att2': {}, 'att3': {}, 'att4': {}}
    #'att2': {},
    #sorted
    for directory in (os.listdir(variables.PATH_ENTROPY)):
        path = variables.PATH_ENTROPY + directory + '/' + variables.DIR_V + '/'
        list_var = sorted(set(variables.day_dict.values()))
        try:
            for file in sorted(os.listdir(path + list_var[len(list_var) - 1])):
                with open(path + list_var[len(list_var) - 1] + '/' + file) as f:
                    norm_dic = ast.literal_eval(f.read())
                    norm_dic.pop('time', None)
                break
            for file in sorted(os.listdir(path + list_var[0])):
                with open(path + list_var[0] + '/' + file) as f:
                    att_1_dic = ast.literal_eval(f.read())
                    att_1_dic.pop('time', None)
            for file in sorted(os.listdir(path + list_var[1])):
                with open(path + list_var[1] + '/' + file) as f:
                    att_2_dic = ast.literal_eval(f.read())
                    att_2_dic.pop('time', None)
            for file in sorted(os.listdir(path + list_var[2])):
                with open(path + list_var[2] + '/' + file) as f:
                    att_3_dic = ast.literal_eval(f.read())
                    att_3_dic.pop('time', None)
            for file in sorted(os.listdir(path + list_var[3])):
                with open(path + list_var[3] + '/' + file) as f:
                    att_4_dic = ast.literal_eval(f.read())
                    att_4_dic.pop('time', None)
        except IndexError:
            pass

        status_dic = {
            'normal': division_fun(directory, norm_dic),
            'att1': division_fun(directory, att_1_dic),
            'att2': division_fun(directory, att_2_dic),
            'att3': division_fun(directory, att_3_dic),
            'att4': division_fun(directory, att_4_dic),
            }

        for status in status_dic.keys():
            information_tot[status][directory] = particular_score(directory, status_dic[status])
            score_tot[status][directory] = score_switch(directory, status_dic[status])

    level = set_network_threshold(score_tot['normal'])


    sw_status = verification_network(score_tot, level)
    thresh = set_particular_threshold(information_tot['normal'])
    pprint(information_tot['normal'])
    print("ATTACK 1 -----------------------------------------------------------------")
    result = localization(information_tot['att1'], thresh)
    pprint(result)
    print("ATTACK 2 -----------------------------------------------------------------")
    result = localization(information_tot['att2'], thresh)
    pprint(result)
    print("ATTACK 3 -----------------------------------------------------------------")
    result = localization(information_tot['att3'], thresh)
    pprint(result)

    print("ATTACK 4 -----------------------------------------------------------------")
    result = localization(information_tot['att4'], thresh)
    pprint(result)


