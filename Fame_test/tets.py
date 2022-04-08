from pymongo import MongoClient
import requests
from ipaddress import *



# controller_ip = '10.50.34.15'
path = ['192.168.13.2', '192.168.12.1', '192.168.16.2', '192.168.67.2']
# src_net = '192.168.100.0'
# src_port = 'any'
# src_wildcard = '0.0.0.255'
# dst_net = '192.168.110.0'
# dst_port = 'any'
# dst_wildcard = '0.0.0.255'
# action = [
#     {'device_id':'62418a3c6b3e4f9c9c55a13c', 'action':2, 'data':'192.168.12.1'},
#     {'device_id':'62418a2d6b3e4f9c9c55a109', 'action':2, 'data':'192.168.16.2'},
#     {'device_id':'62418a526b3e4f9c9c55a1a4', 'action':2, 'data':'192.168.67.2'}
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

src_net = '192.168.100.0'
src_port = 'any'
src_wildcard = '0.0.0.255'
dst_net = '192.168.110.0'
dst_port = 'any'
dst_wildcard = '0.0.0.255'
action = [
    {'device_id':'62418a3c6b3e4f9c9c55a13c', 'action':2, 'data':'192.168.13.1'}
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





