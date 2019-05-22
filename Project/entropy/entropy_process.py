import os
import ast
from global_variable import GlobalVariable
from scipy.stats import entropy
from pprint import pprint

global_variables = GlobalVariable


def _cleaner_(p, q):
    val_p, prob_p = zip(*p)
    val_q, prob_q = zip(*q)
    omega = list(set(val_p + val_q))
    eval = []
    ref = []
    for idx, x in enumerate(omega):
        if x in val_p and x in val_q:
            idx_p = list(val_p).index(x)
            idx_q = list(val_q).index(x)
            eval.append(prob_p[idx_p])
            ref.append(prob_q[idx_q])
        elif x in val_p and x not in val_q:
            idx_p = list(val_p).index(x)
            eval.append(prob_p[idx_p])
            ref.append(1e-06)
        elif x not in val_p and x in val_q:
            idx_q = list(val_q).index(x)
            eval.append(1e-06)
            ref.append(prob_q[idx_q])
    return eval, ref


def entropy_calculation(path, day, data):
    evaluation = writer_prob(path + 'prob_' + str(day) + '.json', data)
    with open(path + 'reference_prob.json', 'r') as f:
        reference = ast.literal_eval(f.read())
    if day > 1:

        with open(path + 'prob_' + str(day - 1) + '.json', 'r') as f:
            previous = ast.literal_eval(f.read())
    else:
        previous = None
    output = {}
    for key in reference:
        if 'err' in key or 'drop' in key:
            continue
        clean_eval, clean_ref = _cleaner_(evaluation[key], reference[key])
        entr_ref = entropy(clean_eval, clean_ref)

        if previous is not None:
            clean_eval, clean_ref = _cleaner_(evaluation[key], previous[key])
            entr_prev = entropy(clean_eval, clean_ref)
        else:
            entr_prev = None
        output[key] = {"reference": entr_ref, "previous": entr_prev}

    with open(path + global_variables.DIR_V + '/' + global_variables.day_dict[day] + '/' + "entropy_" + str(day)
              + ".json", "w") as jsonFile:
        pprint(output, jsonFile)


def _prob_helper(data, label):
    result = {}
    for key in data:
        new_label = ''
        if 'port_counts' == key:
            print(key)
            new_label = 'tcp_'
        print("NAME ", label + key)
        keys = list(data[key].keys())
        probs = list(map(lambda x: x/global_variables.LIMIT_SNAP, list(data[key].values())))
        out = list(zip(keys, probs))
        result[new_label + label + key] = out
    return result


def writer_prob(path, data):
    result = {}
    for key in data:
        if 'h_s' in key:
            continue
        if 'connection' in key:
            label = ''
        elif 'h' in key:
            label = key + "_"
        else:
            if 'port' in key:
                label = key + "_"
            else:
                label = "port_" + key + "_"
        result.update(_prob_helper(data[key], label))
    with open(path, 'w') as f:
        pprint(result, f)
    return result


def main():
    path_db = global_variables.PATH_ENTROPY
    path_features = global_variables.PATH_PROB
    try:
        os.mkdir(path_db)
    except FileExistsError:
        pass

    for directory in os.listdir(path_features):
        if directory != global_variables.name_dir_obs:
            flag_learning = True
            path = path_db + directory + '/'
            if flag_learning:
                try:
                    os.mkdir(path)
                except FileExistsError:
                    pass
                try:
                    os.mkdir(path + global_variables.DIR_V)
                except FileExistsError:
                    pass
                for name_dir in set(global_variables.day_dict.values()):
                    try:
                        os.mkdir(path + global_variables.DIR_V + "/" + name_dir)
                    except FileExistsError:
                        pass
            for f in sorted(os.listdir(path_features + "/" + directory + "/")):
                print(f)
                lst = f.split('_')
                day = int(lst[len(lst) - 1].split('.')[0])
                with open(path_features + "/" + directory + "/" + f, "r") as f:
                    data = ast.literal_eval(f.read())
                if day > 0:
                    entropy_calculation(path, day, data)

                else:
                    writer_prob(path + 'reference_prob.json', data)
                day += 1


if __name__ == '__main__':
    main()
