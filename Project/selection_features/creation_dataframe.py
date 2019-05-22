from global_variable import GlobalVariable
import os
from pprint import pprint
from ast import literal_eval

variables = GlobalVariable


def _analyzer_dict_(sub_dict, tot_data, ver = None):
    value_att = None
    for key in sub_dict:
        print(key, sub_dict[key])
        val = sub_dict[key]
        if key == ver:
            print(variables.max_val_dict[key])
            if val > variables.max_val_dict[key]:
                value_att = 1
            else:
                value_att = 0
        try:
            tot_data[key].append(val)
        except KeyError:
            tot_data[key] = [val]
        if value_att is not None:
            try:
                print('K ', key)
                tot_data['attack'].append(value_att)
                print('VAL ', value_att)
            except KeyError:
                tot_data['attack'] = [value_att]
                print('VAL ', value_att)
            value_att = None
    return tot_data


def __subtraction__(switch, obs, count, label, sub_dict, tot_data):
    path = variables.PATH_OBS + "/" + switch
    try:
        os.mkdir(path)
    except FileExistsError:
        pass
    path = variables.PATH_OBS + "/" + switch + "/obs_" + str(obs) + "_"
    try:
        os.mkdir(path + str(count))
    except FileExistsError:
        pass
    with open(path + str(count) + "/" + label + "_" + str(count), 'w') as file:
        pprint(sub_dict, file)
    if count != 0:
        with open(path + str(count - 1) + "/" + label + "_" + str(count - 1), 'r') as file:
            prev_sub = literal_eval(file.read())
        new_sub = {}
        for key in prev_sub:
            new_sub[key] = sub_dict[key] - prev_sub[key]
            if new_sub[key] < 0:
                new_sub[key] = 0
        tot_data = _analyzer_dict_(new_sub, tot_data)
    else:

        tot_data = _analyzer_dict_(sub_dict, tot_data)
    return tot_data


def _analyzer_list_(switch, obs, count, sub_dict, tot_data):
    for elem in sub_dict:
        for key in elem:
            if isinstance(elem[key], dict):

                if 'port_no' in list(elem.keys()):
                    try:
                        idx = variables.host_dict[elem['host_mac']]
                        label = 'port' + "_" + idx + "_" + key
                    except KeyError:
                        idx = 's'
                        label = 'port_' + elem['port_no'] + "_" + idx + "_" + key
                elif 'host_idx' in list(elem.keys()):
                    idx = variables.host_dict[elem['mac']]
                    label = idx + "_" + key
                try:
                    tot_data[label] = __subtraction__(switch, obs, count, label, elem[key], tot_data[label])
                except KeyError:
                    tot_data[label] = __subtraction__(switch, obs, count, label, elem[key], {})
    return tot_data


def probability_calculator(switch, obs, count, data, tot_data):
    print('OBS ', obs)
    try:
        attack = variables.day_dict[int(obs)]
    except KeyError:
        attack = 'reference'
    if '3' in attack:
        ver = 'port_udp_counts'
    elif '1' in attack:
        ver = 'tcp_failed'
    elif '2' in attack or '4' in attack:
        ver = 'port_counts'
    else:
        ver = 'unknown_protocol'
    for key in data:
        if isinstance(data[key], list):
            tot_data = _analyzer_list_(switch, obs, count, data[key], tot_data)
        elif isinstance(data[key], dict):
            try:
                tot_data[key] = _analyzer_dict_(data[key], tot_data[key], ver)
            except KeyError:
                tot_data[key] = _analyzer_dict_(data[key], {}, ver)
    return tot_data


def main():
    path_features = variables.PATH_DATABASE
    path_db = variables.PATH_STORE
    try:
        os.mkdir(path_db)
    except FileExistsError:
        pass
    try:
        os.mkdir(variables.PATH_OBS)
    except FileExistsError:
        pass
    for directory in os.listdir(path_features):
        try:
            os.mkdir(path_db + '/' + directory)
        except FileExistsError:
            pass
        count = 0
        day = 0
        tot_data = {}
        for file in sorted(os.listdir(path_features + "/" + directory)):
            print(file)
            print(directory)
            print(count)

            with open(path_features + "/" + directory + "/" + file, "r") as f:
                result = literal_eval(f.read())
            tot_data = probability_calculator(directory, day, count, result, tot_data)
            count += 1
            if count == variables.LIMIT_SNAP:
                new_tot_data = {}
                for key in tot_data:
                    for sub_key in tot_data[key]:
                        if key == 'connection_stats':
                            if sub_key == 'port_counts':
                                new_tot_data['tcp_port_counts'] = tot_data[key][sub_key]
                            else:
                                new_tot_data[sub_key] = tot_data[key][sub_key]
                        else:
                            new_tot_data[key + '_' + sub_key] = tot_data[key][sub_key]
                with open(path_db + '/' + directory + "/" + "dataframe_" + str(day) + ".json", "w") as new_f:
                    pprint(new_tot_data, new_f)
                day += 1
                count = 0
                tot_data = {}


if __name__ == '__main__':
    main()
