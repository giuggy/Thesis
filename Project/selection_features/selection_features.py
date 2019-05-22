from pprint import pprint
from copy import deepcopy
import pandas
from sklearn.feature_selection import mutual_info_classif
from ast import literal_eval
from sklearn.ensemble import ExtraTreesClassifier
import os
import numpy as np
import matplotlib.pyplot as plt
from global_variable import GlobalVariable
import json

variables = GlobalVariable



def __set_plot__(switch, features, x_name, att_lst, title_plot):

    n_groups = len(features)
    index = np.arange(n_groups)
    bar_width = 0.35
    rotation = 0

    fig, ax = plt.subplots()
    fig.canvas.set_window_title('Results switch ' + switch)

    a1 = ax.barh(index, att_lst, bar_width, color='purple')

    ax.set_ylabel('Features')
    ax.set_xlabel(x_name)
    ax.legend(prop={'size': 10})
    ax.set_title(title_plot)
    ax.set_xlim([0, 1])
    ax.set_yticks(index + bar_width / 2)
    ax.set_yticklabels(features, rotation=rotation)

    fig.tight_layout()

    if variables.traffic:
        no = '_with'
    else:
        no = '_without'

    #fig.savefig(variables.PATH_EVAL + '/' + switch + "/" + title_plot + '_' + variables.switch_name[switch] + no + ".png")
    plt.plot()
    plt.close()


def model(switch, features, X, Y, title):
    model = ExtraTreesClassifier()
    model.fit(X, Y)
    res = model.feature_importances_
    new_feat = []
    new_lst = []
    print(variables.traffic)
    print(title)
    print(switch)
    print('IMPORTANCE')
    for f, v in zip(features, res):
        if v >= 0.01:
            print(f, v)
            new_feat.append(f)
            new_lst.append(v)
    __set_plot__(switch=switch, features=new_feat, x_name='Importance', att_lst=new_lst, title_plot=title + ' Importance')


def mutual_info(switch, data, title):
    df = pandas.DataFrame(data=data)
    array = df.values
    X = array[:, 1:(df.shape[1] + 1)]
    Y = array[:, 0]
    print(title)
    print(switch)
    print('MUTUAL')
    t = mutual_info_classif(X, Y)
    features = list(df.keys())[1:]
    new_feat = []
    new_lst = []
    for f, v in zip(features, t):
        if v >= 0.1:
            print(f, v)
            new_feat.append(f)
            new_lst.append(v)

    __set_plot__(switch=switch, features=new_feat, x_name='Mutual Information', att_lst=new_lst, title_plot=title + ' Mutual Information')
    model(switch, features, X, Y, title)


def __update_dict__(new, read):

    for key, value in read.items():
        new[key].extend(value)
    return new


def __writer__(path, data):
    with open(path, 'w') as f:
        pprint(data, f)


def main():
    path_db = variables.PATH_STORE
    path_eval = variables.PATH_EVAL
    for directory in sorted(os.listdir(path_db)):
        c = 0
        try:
            os.mkdir(path_eval + '/' + directory)
        except FileExistsError:
            pass
        if directory == 'observations':
            continue
        path_prob = path_db + '/' + directory
        for file in sorted(os.listdir(path_prob)):
            with open(path_prob + "/" + file, "r") as f:
                print(path_prob + "/" + file)
                df = literal_eval(f.read())
                if c == 0:
                    print(1)
                    dataframe_tot = deepcopy(df)
                    dataframe_1 = deepcopy(df)
                    dataframe_2 = deepcopy(df)
                    dataframe_3 = deepcopy(df)
                    dataframe_4 = deepcopy(df)
                elif c == 1:
                    print(2)
                    dataframe_tot = __update_dict__(deepcopy(dataframe_tot), deepcopy(df))
                    dataframe_1 = __update_dict__(deepcopy(dataframe_1), deepcopy(df))
                    dataframe_2 = __update_dict__(deepcopy(dataframe_2), deepcopy(df))
                    dataframe_3 = __update_dict__(deepcopy(dataframe_3), deepcopy(df))
                    dataframe_4 = __update_dict__(deepcopy(dataframe_4), deepcopy(df))
                elif c == 2:
                    print(3)
                    dataframe_tot = __update_dict__(deepcopy(dataframe_tot), deepcopy(df))
                    dataframe_1 = __update_dict__(deepcopy(dataframe_1), deepcopy(df))
                    print(c, "t ", len(dataframe_tot['attack']))
                    print(c, " 1", len(dataframe_1['attack']))
                    print(c, " 2", len(dataframe_2['attack']))
                elif c == 3:
                    print(4)
                    dataframe_tot = __update_dict__(deepcopy(dataframe_tot), deepcopy(df))
                    dataframe_2 = __update_dict__(deepcopy(dataframe_2), deepcopy(df))
                    print(c, "t ", len(dataframe_tot['attack']))
                    print(c, " 1", len(dataframe_1['attack']))
                    print(c, " 2", len(dataframe_2['attack']))
                elif c == 4:
                    print(5)
                    print(c, " ", len(dataframe_tot['attack']))
                    dataframe_tot = __update_dict__(deepcopy(dataframe_tot), deepcopy(df))
                    dataframe_3 = __update_dict__(deepcopy(dataframe_3), deepcopy(df))
                elif c == 5:
                    print(6)
                    print(c, " ", len(dataframe_tot['attack']))
                    dataframe_tot = __update_dict__(deepcopy(dataframe_tot), deepcopy(df))
                    dataframe_4 = __update_dict__(deepcopy(dataframe_4), deepcopy(df))
                print(c, " ", len(dataframe_tot['attack']))
                print(c, " ", len(dataframe_1['attack']))
                print(c, " ", len(dataframe_2['attack']))
                c += 1
        __writer__(path_eval + '/' + directory + '/' + 'data_tot.json', dataframe_tot)
        __writer__(path_eval + '/' + directory + '/' + 'data_1.json', dataframe_1)
        __writer__(path_eval + '/' + directory + '/' + 'data_2.json', dataframe_2)
        __writer__(path_eval + '/' + directory + '/' + 'data_3.json', dataframe_3)
        __writer__(path_eval + '/' + directory + '/' + 'data_4.json', dataframe_4)

        mutual_info(directory, dataframe_tot, 'BINARY CLASSIFIER')
        mutual_info(directory, dataframe_1, 'SYN ATTACK')
        mutual_info(directory, dataframe_2, 'TCP PORTSCAN ATTACK')
        mutual_info(directory, dataframe_3, 'UDP PORTSCAN ATTACK')
        mutual_info(directory, dataframe_4, 'TCP PORTSCAN ATTACK MULTI_TARGET')


if __name__ == '__main__':
    main()
