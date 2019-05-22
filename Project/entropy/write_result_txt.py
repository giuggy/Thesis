import os
import ast
import numpy as np
import json
import matplotlib.pyplot as plt
from global_variable import GlobalVariable

variables = GlobalVariable


def __save_txt__(switch, features, norm_lst, att_lst, title):

    file = 'switch ' + switch + '_' + title + '.json'


    try:
        os.mkdir(variables.save_txt + switch)
    except FileExistsError:
        pass
    with open(variables.save_txt + switch + "/" + variables.switch_name[switch] + '_' + file, 'w') as f:

        f.write('normal' + '\n')
        json.dump(norm_lst, f)
        f.write('\n')

        f.write('attack'+ '\n')
        json.dump(att_lst, f)


def results(path, switch):
    list_var = sorted(set(variables.day_dict.values()))
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

    features_1 = variables.features[list_var[0]][str(switch)]
    features_2 = variables.features[list_var[1]][str(switch)]
    features_3 = variables.features[list_var[2]][str(switch)]
    features_4 = variables.features[list_var[3]][str(switch)]

    title = 'SYN FLOODING'
    title_plot = 'SYN Attack'

    norm_lst = {}
    att_1_lst = {}
    for key in features_1:
        norm_lst[key] = norm_dic[key]['reference']
        att_1_lst[key] = att_1_dic[key]['reference']

    __save_txt__(switch, features_1, norm_lst, att_1_lst, title)

    title = 'Single Target TCP Portscan'
    title_plot = 'TCP PORTSCAN Attack'
    norm_lst = {}
    att_2_lst = {}
    for key in features_2:
        norm_lst[key] = norm_dic[key]['reference']
        att_2_lst[key] = att_2_dic[key]['reference']
    __save_txt__(switch, features_2, norm_lst, att_2_lst, title)

    title = 'Single Target UDP Portscan'
    title_plot = 'UDP PORTSCAN Attack'
    norm_lst = {}
    att_3_lst = {}
    for key in features_3:
        norm_lst[key] = norm_dic[key]['reference']
        att_3_lst[key] = att_3_dic[key]['reference']
    __save_txt__(switch, features_3, norm_lst, att_3_lst, title)

    title = 'Multiple Targets TCP Portscan'
    title_plot = 'TCP PORTSCAN Attack Multi-target'
    norm_lst = {}
    att_4_lst = {}
    for key in features_4:
        norm_lst[key] = norm_dic[key]['reference']
        att_4_lst[key] = att_4_dic[key]['reference']
    __save_txt__(switch, features_4, norm_lst, att_4_lst, title)


def main():
    for directory in os.listdir(variables.PATH_ENTROPY):
        dir_v = variables.PATH_ENTROPY + directory + '/' + variables.DIR_V + '/'
        # dir_h = variables.PATH_ENTROPY + directory + '/' + variables.DIR_H + '/'

        results(path=dir_v, switch=directory)
        # plot(path=dir_h, switch=directory)


if __name__ == '__main__':
    main()
