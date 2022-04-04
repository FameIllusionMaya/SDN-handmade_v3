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


problem_flow = {
    'flow_id':str(12345),
    'in_bytes': 55555,
    'src_ip': '192.168.110.2/24',
    'dst_ip': '192.168.100.3/24'
}
all_device = requests.get("http://10.50.34.15:5001/api/v1/device").json()['devices']
for device in all_device:
    for interface in device['interfaces']:
        try:
            ip4 = IPv4Network((0, interface['subnet']))
            device_ip = interface['ipv4_address'] + '/' + str(ip4.prefixlen)
            device_net_ip = IPv4Interface(device_ip)
            if str(device_net_ip.network) == str(IPv4Interface(problem_flow['src_ip']).network):
                mm = device['management_ip']
                print('yes')
                print(mm)
        except:
            print('Error')
            pass

src_net = 'test'
# print(str(src_net.network))
# print(type(str(src_net.network)))


path = requests.get("http://10.50.34.15:5001/api/v1/path/192.168.12.1,192.168.45.2").json()
print(path)