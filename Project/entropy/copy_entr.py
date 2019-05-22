import os
import ast
from global_variable import GlobalVariable
from datetime import datetime
from scipy.stats import entropy
from pprint import pprint

global_variables = GlobalVariable


def _division_(num, dem):
    try:
        result = num / dem
    except ZeroDivisionError:
        if num != 0.0:
            result = num / 1
        else:
            result = 0.0
    return result


def _cleaner_(p, q):
    res = []
    res1 = []
    for a, b in zip(p, q):
        if a != 0 and b != 0:
            res.append(a)
            res1.append(b)
        elif a == 0 and b != 0:
            res.append(1e-06)
            res1.append(b)
        elif a != 0 and b == 0:
            res.append(a)
            res1.append(1e-06)

    return res, res1


class EntropyCalculator:

    def __init__(self, path, day):
        self.data = None
        self.horizontal = None
        self.count = None
        self.path = path
        self.path_entropy_v = path + global_variables.DIR_V
        self.path_entropy_h = path + global_variables.DIR_H
        self.day = day

    def _add_(self, key, val):
        try:
            self.data[key].append(val)
        except KeyError:
            self.data[key] = [val]

    def __eval_fun_h__(self, evaluation):
        with open(self.path + "reference_h.json", "r") as jsonFile:
            reference = ast.literal_eval(jsonFile.read())
        try:
            with open(self.path + "previous_day_h_" + str(self.day - 1) + ".json", "r") as jsonFile:
                previous = ast.literal_eval(jsonFile.read())
        except FileNotFoundError:
            previous = None

        ref = reference[self.count]
        clean_eval, clean_ref = _cleaner_(evaluation, ref)
        eval_r = entropy(clean_eval, clean_ref)

        if previous is not None:
            prev = previous[self.count]
            clean_eval, clean_prev = _cleaner_(evaluation, prev)
            eval_p = entropy(clean_eval, clean_prev)
        else:
            eval_p = None
        try:
            with open(self.path_entropy_h + '/' + global_variables.day_dict[self.day] + '/' + "entropy_h_" + str(self.day) + ".json", "r") as jsonFile:
                h = ast.literal_eval(jsonFile.read())
        except FileNotFoundError:
            h = {}
        h[self.count] = {"previous": eval_p, "reference": eval_r}
        self.horizontal[self.count] = evaluation
        with open(self.path_entropy_h + '/' + global_variables.day_dict[self.day] + '/' + "entropy_h_" + str(self.day) + ".json", "w") as jsonFile:
            pprint(h, jsonFile)
        with open(self.path + "current_day_h.json", "w") as jsonFile:
            pprint(self.horizontal, jsonFile)

    def __eval_fun_v__(self):
        with open(self.path + "reference_v.json", "r") as jsonFile:
            reference = ast.literal_eval(jsonFile.read())
        try:
            with open(self.path + "previous_day_v_" + str(self.day - 1) + ".json", "r") as jsonFile:
                previous = ast.literal_eval(jsonFile.read())
        except FileNotFoundError:
            previous = None
        result = {"time": str(datetime.now())}
        for key in reference:
            if key != 'count':
                clean_eval, clean_ref = _cleaner_(self.data[key], reference[key])
                entr_ref = entropy(clean_eval, clean_ref)
                if key == 'p_tcp':
                    print('R ', clean_ref)
                    print('E ', clean_eval)
                if previous is not None:
                    clean_eval, clean_ref = _cleaner_(self.data[key], previous[key])
                    entr_prev = entropy(clean_eval, clean_ref)
                else:
                    entr_prev = None
                result[key] = {"reference": entr_ref, "previous": entr_prev}

        with open(self.path_entropy_v + '/' + global_variables.day_dict[self.day] + '/' + "entropy_v_" + str(self.day) + ".json", "w") as jsonFile:
            pprint(result, jsonFile)
        with open(self.path + "previous_day_v_" + str(self.day) + ".json", "w") as jsonFile:
            pprint(self.data, jsonFile)
        with open(self.path + "previous_day_h_" + str(self.day) + ".json", "w") as jsonFile:
            pprint(self.horizontal, jsonFile)
        with open(self.path + "current_day_v.json", "w") as jsonFile:
            pprint({}, jsonFile)
        with open(self.path + "current_day_h.json", "w") as jsonFile:
            pprint({}, jsonFile)

    def probability_calculation(self, results, flag_learning):

        if flag_learning:
            try:
                with open(self.path + "reference_v.json", "r") as jsonFile:
                    self.data = ast.literal_eval(jsonFile.read())
            except FileNotFoundError:
                self.data = {}
            try:
                with open(self.path + "reference_h.json", "r") as jsonFile:
                    self.horizontal = ast.literal_eval(jsonFile.read())
            except FileNotFoundError:
                self.horizontal = {}
        else:
            try:
                with open(self.path + "current_day_v.json", "r") as jsonFile:
                    self.data = ast.literal_eval(jsonFile.read())
            except FileNotFoundError:
                self.data = {}
            try:
                with open(self.path + "current_day_h.json", "r") as jsonFile:
                    self.horizontal = ast.literal_eval(jsonFile.read())
            except FileNotFoundError:
                self.horizontal = {}
        try:
            self.data["count"] += 1
        except KeyError:
            self.data["count"] = 1
        self.count = self.data["count"]
        evaluation = []
        for st in results["host_stats"]:
            elem = list(filter(lambda x: x['host_mac'] == st["mac"], results['port_stats']))[0]
            p_src_pkt = _division_(st['src']['pkt'], elem['tx']['pkt'])
            p_src_bytes = _division_(st['src']['bytes'], elem['tx']['bytes'])
            p_dst_pkt = _division_(st['dst']['pkt'], elem['rx']['pkt'])
            p_dst_bytes = _division_(st['dst']['bytes'], elem['rx']['bytes'])
            evaluation += [p_src_pkt, p_src_bytes, p_dst_pkt, p_dst_bytes]
            self._add_(key="src_pkt", val=p_src_pkt)
            self._add_(key="src_bytes", val=p_src_bytes)
            self._add_(key="dst_pkt", val=p_dst_pkt)
            self._add_(key="dst_bytes", val=p_dst_bytes)

        st = results["tcp_stats"]
        tot_tcp = st["tcp_connection"]
        tot = st["tcp_failed"] + st["tcp_connection"] + st["rst"] + st["unknown_protocol"]

        p_tcp = _division_(st["tcp_failed"], tot_tcp)
        print(p_tcp)
        print("F ", st["tcp_failed"], " T", tot_tcp)
        p_rst_tcp = _division_(st["rst"], tot_tcp)
        p_port = _division_(st["port_counts"], global_variables.TOTAL_PORTS)

        evaluation += [p_tcp, p_rst_tcp, p_port]
        self._add_(key="tcp_fail", val=p_tcp)
        self._add_(key="tcp_rst", val=p_rst_tcp)
        self._add_(key="tcp_port", val=p_port)

        for st in results["port_stats"]:
            p_pkt_rx = _division_(st["rx"]["pkt"], (st["rx"]["pkt"] + st["tx"]["pkt"]))
            p_drop_rx = _division_(st["rx"]["drop"], (st["rx"]["drop"] + st["tx"]["drop"]))
            p_bytes_rx = _division_(st["rx"]["bytes"], (st["rx"]["bytes"] + st["tx"]["bytes"]))
            p_err_rx = _division_(st["rx"]["error"], (st["rx"]["error"] + st["tx"]["error"]))
            p_frame = _division_(st["rx"]["frame_err"], st["rx"]["error"])
            p_over = _division_(st["rx"]["over_err"], st["rx"]["error"])
            p_crc = _division_(st["rx"]["crc_err"], st["rx"]["error"])

            p_pkt_tx = _division_(st["tx"]["pkt"], (st["rx"]["pkt"] + st["tx"]["pkt"]))
            p_drop_tx = _division_(st["tx"]["drop"], (st["rx"]["drop"] + st["tx"]["drop"]))
            p_bytes_tx = _division_(st["tx"]["bytes"], (st["rx"]["bytes"] + st["tx"]["bytes"]))
            p_err_tx = _division_(st["tx"]["error"], (st["rx"]["error"] + st["tx"]["error"]))

            evaluation += [p_pkt_rx, p_drop_rx, p_bytes_rx, p_err_rx, p_frame, p_over, p_crc, p_pkt_tx, p_drop_tx,
                           p_bytes_tx, p_err_tx]
            self._add_(key='pkt_rx', val=p_pkt_rx)
            self._add_(key='drop_rx', val=p_drop_rx)
            self._add_(key='bytes_rx', val=p_bytes_rx)
            self._add_(key='err_rx', val=p_err_rx)
            self._add_(key='frame', val=p_frame)
            self._add_(key='over', val=p_frame)
            self._add_(key='crc', val=p_crc)

            self._add_(key='pkt_tx', val=p_pkt_tx)
            self._add_(key='drop_tx', val=p_drop_tx)
            self._add_(key='bytes_tx', val=p_bytes_tx)
            self._add_(key='err_tx', val=p_err_tx)

        if flag_learning:
            with open(self.path + "reference_v.json", "w") as jsonFile:
                pprint(self.data, jsonFile)
            with open(self.path + "reference_h.json", "w") as jsonFile:
                self.horizontal[self.count] = evaluation
                pprint(self.horizontal, jsonFile)
            if self.count == global_variables.LIMIT:
                flag_learning = False
                self.day += 1
        else:
            self.__eval_fun_h__(evaluation)

            if self.count == global_variables.LIMIT:
                self.__eval_fun_v__()
                self.day += 1
            else:
                with open(self.path + "current_day_v.json", "w") as jsonFile:
                    pprint(self.data, jsonFile)
        return flag_learning, self.day




def main():
    path_db = global_variables.PATH_ENTROPY
    path_features = global_variables.PATH_FEATURES
    for directory in os.listdir(path_features):
        flag_learning = True
        day = 0
        print(path_features + "/" + directory)
        path = path_db + directory + '/'
        if flag_learning:
            os.mkdir(path)
            os.mkdir(path + global_variables.DIR_V)
            os.mkdir(path + global_variables.DIR_H)
            for name_dir in set(global_variables.day_dict.values()):
                os.mkdir(path + global_variables.DIR_V + "/" + name_dir)
                os.mkdir(path + global_variables.DIR_H + "/" + name_dir)
        for file in sorted(os.listdir(path_features + "/" + directory)):
            print(file)
            print(day)
            with open(path_features + "/" + directory + "/" + file, "r") as f:

                result = ast.literal_eval(f.read())
                flag_learning, day = EntropyCalculator(path=path, day=day).probability_calculation(results=result,
                                                                                                   flag_learning=
                                                                                                   flag_learning)
        break


if __name__ == '__main__':
    main()
