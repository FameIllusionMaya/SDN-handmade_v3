from pymongo import MongoClient
import requests


controller_ip = '10.50.34.15'

src_net = '192.168.200.0'
src_port = 'any'
src_wildcard = '0.0.0.255'
dst_net = '192.168.201.0'
dst_port = 'any'
dst_wildcard = '0.0.0.255'
action = [{'device_id':'62349df46b3e4f9c9c661f40', 'action':2, 'data':'192.168.2.1'},
 {'device_id':'62349dec6b3e4f9c9c661ed0', 'action':2, 'data':'192.168.1.1'}]
new_flow = {'name':'Yukari', 'src_ip':src_net, 'src_port':src_port, 'src_subnet':src_wildcard, 'dst_ip':dst_net, 'dst_port':dst_port,\
        'dst_subnet':dst_wildcard, 'actions':action, 'aging_time': 0}
requests.post("http://"+controller_ip+":5001/api/v1/flow/routing", json=new_flow)
