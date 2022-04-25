from pymongo import MongoClient
import requests
from ipaddress import *
import random

# controller_ip = '10.50.34.15'
# path = ['192.168.13.2', '192.168.12.1', '192.168.16.2', '192.168.67.2']



src_net = '192.168.100.2'
src_port = 'any'
src_wildcard = '0.0.0.255'
dst_net = '192.168.200.10'
dst_port = 'any'
dst_wildcard = '0.0.0.255'
action = [
    {'device_id':'62654a8955c5ba593f059d16', 'action':2, 'data':'192.168.23.2'},
    {'device_id':'62654aab55c5ba593f059e00', 'action':2, 'data':'192.168.34.2'}
    ]
new_flow = {
    'name':'Yukari',
    'src_ip':src_net,
    'src_port':src_port,
    'src_subnet':src_wildcard, 
    'dst_ip':dst_net, 
    'dst_port':dst_port,
    'dst_subnet':dst_wildcard,
    'actions':action,
    'aging_time': 0
    }
requests.post("http://10.50.34.15:5001/api/v1/flow/routing", json=new_flow)



# src_net = '192.168.110.0'
# src_port = 'any'
# src_wildcard = '0.0.0.255'
# dst_net = '192.168.100.0'
# dst_port = 'any'
# dst_wildcard = '0.0.0.255'
# action = [
#     {'device_id':'62418a5a6b3e4f9c9c55a1bd', 'action':2, 'data':'192.168.16.2'},
#     {'device_id':'62418a526b3e4f9c9c55a1a4', 'action':2, 'data':'192.168.12.1'},
#     {'device_id':'62418a2d6b3e4f9c9c55a109', 'action':2, 'data':'192.168.13.2'}
#     ]
# new_flow = {
#     'name':'test+back',
#     'src_ip':src_net,
#     'src_port':src_port,
#     'src_subnet':src_wildcard, 
#     'dst_ip':dst_net, 
#     'dst_port':dst_port,
#     'dst_subnet':dst_wildcard,
#     'actions':action,
#     'aging_time': 0
#     }
# requests.post("http://10.50.34.15:5001/api/v1/flow/routing", json=new_flow)

# src_net = '192.168.100.2'
# src_port = 'any'
# src_wildcard = '0.0.0.255'
# dst_net = '192.168.110.0'
# dst_port = 'any'
# dst_wildcard = '0.0.0.255'
# action = [
#     {'device_id':'62418a3c6b3e4f9c9c55a13c', 'action':2, 'data':'192.168.13.1'}
#     ]
# new_flow = {
#     'name':'Yukari',
#     'src_ip':src_net,
#     'src_port':src_port,
#     'src_subnet':src_wildcard, 
#     'dst_ip':dst_net, 
#     'dst_port':dst_port,
#     'dst_subnet':dst_wildcard,
#     'actions':action,
#     'aging_time': 0
#     }
# requests.post("http://10.50.34.15:5001/api/v1/flow/routing", json=new_flow)


# ip = '192.168.1.5/25'
# src_info = ip.split('/')
# print(src_info)
# a = str(IPv4Address(int(IPv4Address._make_netmask('24')[0])^(2**32-1)))
# print(a)

# all_policy = requests.get("http://10.50.34.15:5001/api/v1/flow/routing").json()['flows']

# for policy in all_policy:
#     print(policy)




# cash_tour = 0
# cash_single = 0
# for i in range(1000):
#     cash_tour -= 10
#     cash_single -= 10


#     num_single = random.randint(1, 2)
#     num_tour = random.randint(1, 2)

#     if num_single == 1:
#         cash_single += 18
#     else:
#         cash_single += 0
    
#     if num_tour == 1:
#         num_tour2 = random.randint(1, 2)
#         if num_tour2 == 1:
#             cash_tour += 27
#         else:
#             cash_tour += 9
#     else:
#         cash_tour -= 10
#     print(num_single, cash_single)

# print(cash_tour, cash_single)
    