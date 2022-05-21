from pymongo import MongoClient
import requests
from ipaddress import *
import random
import ccxt
import pandas as pd
import time
from datetime import datetime
import csv
import math
import requests




# src_net = '192.168.100.2'
# src_port = 'any'
# src_wildcard = '0.0.0.255'
# dst_net = '192.168.200.10'
# dst_port = 'any'
# dst_wildcard = '0.0.0.255'
# action = [
#     {'device_id':'62654a8955c5ba593f059d16', 'action':3, 'data':'192.168.23.2'},
#     {'device_id':'62654aab55c5ba593f059e00', 'action':3, 'data':'192.168.34.2'}
#     ]
# new_flow = {
#     'name':'test',
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

# { <field1>: <value>, <field2>: <value> ... }
#{'$in':[str(i) for i in ip_network]}
# client = MongoClient('10.50.34.15', 27017)
# # flows = client.sdn01.flow_stat.find({'ipv4_dst_addr': {'$in':['192.168.69.1', '10.50.34.15']}})
# flows = client.sdn01.flow_stat.find({'ipv4_dst_addr': ''})
# for i in flows:
#     print(i)
#     print()

client = MongoClient('localhost', 27017)
maya_var = client.MayaDB.BTC_Grid_DadFame

go_in = {
    '29999': 0,
    '29749': 0
}
go_in = {}
for i in range(9999, 99999, 250):
    go_in[str(float(i))] = {'Money': 0, 'Asset':0, 'Trigered_Count':0}

print(go_in)
def edit_db():
    a = maya_var.find()
    id = a[0]['_id']

    maya_var.update_one({
        "_id": id
        }, {"$set": {
        "9999": {'Money': 0, 'Asset':150, 'Trigered_Count':0},
    }})




# maya_var.insert(go_in)
