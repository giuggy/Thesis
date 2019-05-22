import os
import ast
import numpy as np
import matplotlib.pyplot as plt
from global_variable import GlobalVariable

variables = GlobalVariable

def plot(path, switch):
    print(variables.day_dict.values())
    list_var = sorted(set(variables.day_dict.values()))
    print(list_var)
    for file in sorted(os.listdir(path + list_var[len(list_var) - 1])):
        with open(path + list_var[len(list_var) - 1] + '/' + file) as f:
            norm_dic = ast.literal_eval(f.read())
            norm_dic.pop('time', None)
            norm_lst = list(map(lambda x: x['reference'], list(norm_dic.values())))
        break
    for file in sorted(os.listdir(path + list_var[0])):
        with open(path + list_var[0] + '/' + file) as f:
            att_1_dic = ast.literal_eval(f.read())
            att_1_dic.pop('time', None)
            att_1_lst = list(map(lambda x: x['reference'], list(att_1_dic.values())))
    for file in sorted(os.listdir(path + list_var[1])):
        with open(path + list_var[1] + '/' + file) as f:
            att_2_dic = ast.literal_eval(f.read())
            att_2_dic.pop('time', None)
            att_2_lst = list(map(lambda x: x['reference'], list(att_2_dic.values())))
    for file in sorted(os.listdir(path + list_var[2])):
        with open(path + list_var[2] + '/' + file) as f:
            att_3_dic = ast.literal_eval(f.read())
            att_3_dic.pop('time', None)
            att_3_lst = list(map(lambda x: x['reference'], list(att_3_dic.values())))
    for file in sorted(os.listdir(path + list_var[3])):
        with open(path + list_var[3] + '/' + file) as f:
            att_4_dic = ast.literal_eval(f.read())
            att_4_dic.pop('time', None)
            att_4_lst = list(map(lambda x: x['reference'], list(att_4_dic.values())))

    fig, axes = plt.subplots(nrows=2, ncols=2)
    fig.canvas.set_window_title('Results switch '+ switch)
    ax1, ax2, ax3, ax4 = axes.flatten()

    features = list(norm_dic.keys())
    n_groups = len(features)
    index = np.arange(n_groups)
    bar_width = 0.35
    rotation = 90

    a1 = ax1.bar(index, norm_lst, bar_width, color='green', label='Normal Status')
    a2 = ax1.bar(index + bar_width, att_1_lst, bar_width, color='red', label='SYN FLOODING')

    ax1.set_xlabel('Features')
    ax1.set_ylabel('Entropy')
    ax1.legend(prop={'size': 10})
    ax1.set_title('Plot SYN Attack')
    ax1.set_xticks(index + bar_width / 2)
    ax1.set_xticklabels(features, rotation=rotation)

    b1 = ax2.bar(index, norm_lst, bar_width, color='green', label='Normal Status')
    b2 = ax2.bar(index + bar_width, att_2_lst, bar_width, color='red', label='Single Target TCP Portscan')

    ax2.set_xlabel('Features')
    ax2.set_ylabel('Entropy')
    ax2.legend(prop={'size': 10})
    ax2.set_title('Plot PortScan Attack')
    ax2.set_xticks(index + bar_width / 2)
    ax2.set_xticklabels(features, rotation=rotation)

    c1 = ax3.bar(index, norm_lst, bar_width, color='green', label='Normal Status')
    c2 = ax3.bar(index + bar_width, att_3_lst, bar_width, color='red', label='Single Target UDP Portscan')

    ax3.set_xlabel('Features')
    ax3.set_ylabel('Entropy')
    ax3.legend(prop={'size': 10})
    ax3.set_title('Plot PortScan Attack')
    ax3.set_xticks(index + bar_width / 2)
    ax3.set_xticklabels(features, rotation=rotation)

    d1 = ax4.bar(index, norm_lst, bar_width, color='green', label='Normal Status')
    d2 = ax4.bar(index + bar_width, att_4_lst, bar_width, color='red', label='More Targets -sV FLOODING')

    ax4.set_xlabel('Features')
    ax4.set_ylabel('Entropy')
    ax4.legend(prop={'size': 10})
    ax4.set_title('Plot PortScan Attack')
    ax4.set_xticks(index + bar_width / 2)
    ax4.set_xticklabels(features, rotation=rotation)

    fig.tight_layout()
    plt.show()


def main():
    for directory in os.listdir(variables.PATH_ENTROPY):
        dir_v = variables.PATH_ENTROPY + directory + '/' + variables.DIR_V + '/'
        # dir_h = variables.PATH_ENTROPY + directory + '/' + variables.DIR_H + '/'

        plot(path=dir_v, switch=directory)
        # plot(path=dir_h, switch=directory)




if __name__ == '__main__':
    main()
