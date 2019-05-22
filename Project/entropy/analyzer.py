import os
import ast
from pprint import pprint
from global_variable import GlobalVariable

global_variables = GlobalVariable


def _analyzer_dict_(sub_dict, tot_data):
    no_bins = global_variables.no_bins
    for key in sub_dict:

        if 'bytes' in key:
            if no_bins:
                val = sub_dict[key]
            else:
                val = round(sub_dict[key] / global_variables.round_val_bytes) * global_variables.round_val_bytes
        elif 'pkt' in key:
            if no_bins:
                val = sub_dict[key]
            else:
                val = round(sub_dict[key] / global_variables.round_val_pkt) * global_variables.round_val_pkt
        else:
            val = sub_dict[key]

        try:
            tot_data[key][val] += 1
        except KeyError:
            try:
                tot_data[key][val] = 1
            except KeyError:
                tot_data[key] = {val: 1}
    return tot_data


def __subtraction__(switch, obs, count, label, sub_dict, tot_data):
    path = global_variables.PATH_OBS + "/" + switch
    try:
        os.mkdir(path)
    except FileExistsError:
        pass
    path = global_variables.PATH_OBS + "/" + switch + "/obs_" + str(obs) + "_"
    try:
        os.mkdir(path + str(count))
    except FileExistsError:
        pass
    with open(path + str(count) + "/" + label + "_" + str(count), 'w') as file:
        pprint(sub_dict, file)
    if count != 0:
        with open(path + str(count - 1) + "/" + label + "_" + str(count - 1), 'r') as file:
            prev_sub = ast.literal_eval(file.read())
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
                        idx = global_variables.host_dict[elem['host_mac']]
                        label = 'port' + "_" + idx + "_" + key
                    except KeyError:
                        idx = 's'
                        label = 'port_' + elem['port_no'] + "_" + idx + "_" + key
                elif 'host_idx' in list(elem.keys()):
                    idx = global_variables.host_dict[elem['mac']]
                    label = idx + "_" + key
                try:
                    tot_data[label] = __subtraction__(switch, obs, count, label, elem[key], tot_data[label])
                except KeyError:
                    tot_data[label] = __subtraction__(switch, obs, count, label, elem[key], {})
    return tot_data


def probability_calculator(switch, obs, count, data, tot_data):
    for key in data:
        if isinstance(data[key], list):
            tot_data = _analyzer_list_(switch, obs, count, data[key], tot_data)
        elif isinstance(data[key], dict):
            try:
                tot_data[key] = _analyzer_dict_(data[key], tot_data[key])
            except KeyError:
                tot_data[key] = _analyzer_dict_(data[key], {})
    return tot_data


def main():
    path_features = global_variables.PATH_FEATURES
    path_db = global_variables.PATH_PROB
    try:
        os.mkdir(path_db)
    except FileExistsError:
        pass
    try:
        os.mkdir(global_variables.PATH_OBS)
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
            print(count)

            with open(path_features + "/" + directory + "/" + file, "r") as f:
                result = ast.literal_eval(f.read())
            tot_data = probability_calculator(directory, day, count, result, tot_data)
            pprint(tot_data)
            count += 1
            if count == global_variables.LIMIT_SNAP:
                with open(path_db + '/' + directory + "/" + "probability_" + str(day) + ".json", "w") as f:
                    pprint(tot_data, f)
                day += 1
                count = 0
                tot_data = {}


if __name__ == '__main__':
    main()
