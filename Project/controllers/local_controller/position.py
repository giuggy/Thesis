import http.client
import json


class PositionApi:

    def __init__(self, server, mac):
        self.server = server
        self.mac = mac

    def get(self):
        ret = self.rest_call({}, 'GET')
        return self.get_hosts(json.loads(ret[2]))

    def get_hosts(self, devices):
        hosts = {}
        for i in devices["devices"]:
            res = list(filter(lambda item: item['switch'] == self.mac, i['attachmentPoint']))
            if len(res) != 0:
                try:
                    hosts[i['attachmentPoint'][0]["port"]] = (i['ipv4'][0], i['mac'][0])
                except IndexError:
                    hosts[i['attachmentPoint'][0]["port"]] = (i['ipv6'][0], i['mac'][0])
        return hosts

    def rest_call(self, data, action):
        path = '/wm/device/'
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
        }
        body = json.dumps(data)
        conn = http.client.HTTPConnection(self.server, 8080)
        conn.request(action, path, body, headers)
        response = conn.getresponse()
        ret = (response.status, response.reason, response.read())
        conn.close()
        return ret
