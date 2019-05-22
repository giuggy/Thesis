import json
from datetime import datetime
from scipy.stats import entropy

LIMIT = 24


def _division_(num, dem):
    try:
        result = num / dem
    except ZeroDivisionError:
        result = 0
    return result


class Preprocessing:

    def __init__(self, path, day):
        self.data = None
        self.horizontal = None
        self.count = None
        self.path = path
        self.day = day

    def _add_(self, key, val):
        try:
            self.data[key].append(val)
        except KeyError:
            self.data[key] = [val]

    def __eval_fun_h__(self, evaluation):
        with open(self.path + "reference_h.json", "r") as jsonFile:
            reference = json.load(jsonFile)
        try:
            with open(self.path + "previous_day_h.json", "r") as jsonFile:
                previous = json.load(jsonFile)
        except FileNotFoundError:
            previous = None
        ref = reference[str(self.count)]
        eval_r = entropy(evaluation, ref)
        if previous is not None:
            prev = previous[str(self.count)]
            eval_p = entropy(evaluation, prev)
        else:
            eval_p = None
        try:
            with open(self.path + "entropy_h_" + str(self.day) + ".json", "r") as jsonFile:
                h = json.load(jsonFile)
        except FileNotFoundError:
            h = {}
        h[self.count] = {"previous": eval_p, "reference": eval_r}
        self.horizontal[self.count] = evaluation
        with open(self.path + "entropy_h_" + str(self.day) + ".json", "w") as jsonFile:
            json.dump(h, jsonFile)
        with open(self.path + "current_day_h.json", "w") as jsonFile:
            json.dump(self.horizontal, jsonFile)

    def __eval_fun_v__(self):
        with open(self.path + "reference_v.json", "r") as jsonFile:
            reference = json.load(jsonFile)
        try:
            with open(self.path + "previous_day_v.json", "r") as jsonFile:
                previous = json.load(jsonFile)
        except FileNotFoundError:
            previous = None
        result = {"time": str(datetime.now())}
        for key in reference:
            if key != 'count':
                entr_ref = entropy(self.data[key], reference[key])
                if previous is not None:
                    entr_prev = entropy(self.data[key], previous[key])
                else:
                    entr_prev = None
                result[key] = {"reference": entr_ref, "previous": entr_prev}

        with open(self.path + "entropy_v_" + str(self.day) + ".json", "w") as jsonFile:
            json.dump(result, jsonFile)
        with open(self.path + "previous_day_v.json", "w") as jsonFile:
            json.dump(self.data, jsonFile)
        with open(self.path + "previous_day_h.json", "w") as jsonFile:
            json.dump(self.horizontal, jsonFile)
        with open(self.path + "current_day_v.json", "w") as jsonFile:
            json.dump({}, jsonFile)
        with open(self.path + "current_day_h.json", "w") as jsonFile:
            json.dump({}, jsonFile)

    def probability_calculation(self, results, flag_learning):

        if flag_learning:
            try:
                with open(self.path + "reference_v.json", "r") as jsonFile:
                    self.data = json.load(jsonFile)
            except FileNotFoundError:
                self.data = {}
            try:
                with open(self.path + "reference_h.json", "r") as jsonFile:
                    self.horizontal = json.load(jsonFile)
            except FileNotFoundError:
                self.horizontal = {}
        else:
            try:
                with open(self.path + "current_day_v.json", "r") as jsonFile:
                    self.data = json.load(jsonFile)
            except FileNotFoundError:
                self.data = {}
            try:
                with open(self.path + "current_day_h.json", "r") as jsonFile:
                    self.horizontal = json.load(jsonFile)
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
            self._add_(key="p_src_pkt", val=p_src_pkt)
            self._add_(key="p_src_bytes", val=p_src_bytes)
            self._add_(key="p_dst_pkt", val=p_dst_pkt)
            self._add_(key="p_dst_bytes", val=p_dst_bytes)

        st = results["tcp_stats"]
        tot_tcp = st["tcp_failed"] + st["tcp_connection"] + st["rst"]
        tot = st["tcp_failed"] + st["tcp_connection"] + st["rst"] + st["unknown_protocol"]

        p_tcp = _division_(st["tcp_failed"], tot_tcp)
        p_port = _division_(st["port_counts"], tot)

        evaluation += [p_tcp, p_port]
        self._add_(key="p_tcp", val=p_tcp)
        self._add_(key="p_port", val=p_port)

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
            self._add_(key='p_pkt_rx', val=p_pkt_rx)
            self._add_(key='p_drop_rx', val=p_drop_rx)
            self._add_(key='p_bytes_rx', val=p_bytes_rx)
            self._add_(key='p_err_rx', val=p_err_rx)
            self._add_(key='p_frame', val=p_frame)
            self._add_(key='p_over', val=p_frame)
            self._add_(key='p_crc', val=p_crc)

            self._add_(key='p_pkt_tx', val=p_pkt_tx)
            self._add_(key='p_drop_tx', val=p_drop_tx)
            self._add_(key='p_bytes_tx', val=p_bytes_tx)
            self._add_(key='p_err_tx', val=p_err_tx)

        if flag_learning:
            with open(self.path + "reference_v.json", "w") as jsonFile:
                json.dump(self.data, jsonFile)
            with open(self.path + "reference_h.json", "w") as jsonFile:
                self.horizontal[self.count] = evaluation
                json.dump(self.horizontal, jsonFile)
            if self.count == LIMIT:
                flag_learning = False
                self.day += 1
        else:
            self.__eval_fun_h__(evaluation)

            if self.count == LIMIT:
                self.__eval_fun_v__()
                self.day += 1
            else:
                with open(self.path + "current_day_v.json", "w") as jsonFile:
                    json.dump(self.data, jsonFile)
        return flag_learning, self.count, self.day
