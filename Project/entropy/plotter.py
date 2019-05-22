import os
import ast
import numpy as np
import matplotlib.pyplot as plt
from global_variable import GlobalVariable

variables = GlobalVariable


def __set_plot__(switch, features, norm_lst, att_lst, title, title_plot, value=15):

    n_groups = len(features)
    index = np.arange(n_groups)
    bar_width = 0.35
    rotation = 0

    fig, ax = plt.subplots()
    fig.canvas.set_window_title('Results switch ' + switch)

    a1 = ax.barh(index, norm_lst, bar_width, color='green', label='Normal Status')
    a2 = ax.barh(index + bar_width, att_lst, bar_width, color='red', label=title)

    ax.set_ylabel('Features')
    ax.set_xlabel('Divergence')
    ax.legend(prop={'size': 10})
    ax.set_title(title_plot)
    ax.set_xlim([0, value])
    ax.set_yticks(index + bar_width / 2)
    ax.set_yticklabels(features, rotation=rotation)

    fig.tight_layout()
    try:
        os.mkdir(variables.save_pic + switch)
    except FileExistsError:
        pass
    fig.savefig(variables.save_pic + switch + "/" + variables.switch_name[switch] + '_' + title_plot + ".png")
    plt.close()


def plot(path, switch):
    print(variables.day_dict.values())
    list_var = sorted(set(variables.day_dict.values()))
    print(list_var)
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
    norm_lst = []
    att_1_lst = []
    for key in features_1:
        norm_lst.append(norm_dic[key]['reference'])
        att_1_lst.append(att_1_dic[key]['reference'])

    __set_plot__(switch, features_1, norm_lst, att_1_lst, title, title_plot)

    title = 'Single Target TCP Portscan'
    title_plot = 'TCP PORTSCAN Attack'
    norm_lst = []
    att_2_lst = []
    for key in features_2:
        norm_lst.append(norm_dic[key]['reference'])
        att_2_lst.append(att_2_dic[key]['reference'])
    __set_plot__(switch, features_2, norm_lst, att_2_lst, title, title_plot, value=6)

    title = 'Single Target UDP Portscan'
    title_plot = 'UDP PORTSCAN Attack'
    norm_lst = []
    att_3_lst = []
    for key in features_3:
        norm_lst.append(norm_dic[key]['reference'])
        att_3_lst.append(att_3_dic[key]['reference'])
    __set_plot__(switch, features_3, norm_lst, att_3_lst, title, title_plot)

    title = 'Multiple Targets TCP Portscan'
    title_plot = 'TCP PORTSCAN Attack Multi-target'
    norm_lst = []
    att_4_lst = []
    for key in features_4:
        norm_lst.append(norm_dic[key]['reference'])
        att_4_lst.append(att_4_dic[key]['reference'])
    __set_plot__(switch, features_4, norm_lst, att_4_lst, title, title_plot)


def main():
    for directory in os.listdir(variables.PATH_ENTROPY):
        dir_v = variables.PATH_ENTROPY + directory + '/' + variables.DIR_V + '/'
        # dir_h = variables.PATH_ENTROPY + directory + '/' + variables.DIR_H + '/'

        plot(path=dir_v, switch=directory)
        # plot(path=dir_h, switch=directory)


if __name__ == '__main__':
    main()
