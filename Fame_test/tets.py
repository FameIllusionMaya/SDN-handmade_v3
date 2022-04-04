from pymongo import MongoClient
import requests
from ipaddress import *



# controller_ip = '10.50.34.15'

# src_net = '192.168.200.0'
# src_port = 'any'
# src_wildcard = '0.0.0.255'
# dst_net = '192.168.201.0'
# dst_port = 'any'
# dst_wildcard = '0.0.0.255'
# action = [{'device_id':'62349df46b3e4f9c9c661f40', 'action':2, 'data':'192.168.2.1'},
#  {'device_id':'62349dec6b3e4f9c9c661ed0', 'action':2, 'data':'192.168.1.1'}]
# new_flow = {'name':'Yukari', 'src_ip':src_net, 'src_port':src_port, 'src_subnet':src_wildcard, 'dst_ip':dst_net, 'dst_port':dst_port,\
#         'dst_subnet':dst_wildcard, 'actions':action, 'aging_time': 0}
# requests.post("http://10.50.34.15:5001/api/v1/flow/routing", json=new_flow)


# path_info = requests.get("http://10.50.34.15:5001/api/v1/path/192.168.1.1,192.168.10.1").json()
# all_path = []
# print('There are', len(path_info['paths']), ' possible paths')
# for path in path_info['paths']:
#     all_path.append(path['path'])
# print('Lowest hop use =', len(min(all_path)), 'hops')
# print('Path:', min(all_path))

# payload = {'flow_id': 8}
# requests.delete("http://10.50.34.15:5001/api/v1/flow/routing", params=payload)



# print(str(src_net.network))
# print(type(str(src_net.network)))


a = [
"192.168.13.2",
"192.168.12.2",
"192.168.12.1",
"192.168.16.2",
"192.168.67.2"
]
b = [
"192.168.13.2",
"192.168.45.1",
"192.168.67.2"
]
x = [
"192.168.13.2",
"192.168.67.2",
"192.168.45.1"
]
y = [
"192.168.67.2",
"192.168.45.1",
"192.168.13.2"
]
z = [
"192.168.13.2",
"192.168.12.2",
"192.168.12.1",
"192.168.16.2",
"192.168.67.2",
"192.168.13.2",
"192.168.45.1",
"192.168.67.2"
]

c = ['192.168.45.1', '192.168.67.2']
def check_dup_link(a, b):
    for i in range(len(a)):
        if i + 1 != len(a):
            src = a[i]
            dst = a[i+1]
        if (src == b[0] and dst == b[1]) or (src == b[1] and dst == b[0]):
            return True
    return False

print(check_dup_link(a, c))
print(check_dup_link(b, c))
print(check_dup_link(x, c))
print(check_dup_link(y, c))
print(check_dup_link(z, c))
