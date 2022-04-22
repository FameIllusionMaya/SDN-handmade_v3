from ast import Try
import datetime
import logging
import time

from matplotlib.style import available

import sdn_utils
from repository import get, PolicyRoute
from tools import PathFinder
from worker.ssh.ssh_worker import SSHConnection
import pprint
import generate_graph
import networkx as nx
import requests
from pymongo import MongoClient
import decimal
from ipaddress import *



class TrafficMonitorTask:
    def __init__(self):
        self.device_repository = get('device')
        self.flow_stat_repository = get('flow_stat')
        self.copied_route_repository = get('copied_route')
        self.link_utilization_repository = get('link_utilization')
        self.flow_routing_repository = get('flow_routing')
        self.last_run = 0
        self.delay = 1
        self.path_finder = PathFinder(auto_update_graph=False)
        self.use_port = False
        self.active_paths = []
        self.utilize = 85
        self.reverse_path = []
        self.reverse_path_link = []
        self.current_flow = None
        self.explorer_neighbor = []
        self.controller_ip = '10.50.34.15'

    def check_before_run(self):
        if time.time() > self.last_run + self.delay:
            return True
        return False

    def run(self, ssh_connection: SSHConnection = None):
        def find_problem_flow(problem_link, client):
            #running_flow = [{'oid':'xxxx'}, {'oid':'xxxx'}, {'oid':'xxxx'}]
            url = "http://localhost:5001/api/v1/link/" + str(problem_link['link_oid'])
            running_flow_id_json = requests.get(url).json()['link'][0]['running_flows']
            running_flow_id = [str(i['$oid']) for i in running_flow_id_json]
            problem_flow = []
            flow_database = client.sdn01.flow_stat
            for flow in flow_database.find():
                if str(flow['_id']) in running_flow_id:
                    flow_data = {
                        'flow_id':str(flow['_id']),
                        'in_bytes':flow['in_bytes'],
                        'src_ip': flow['ipv4_src_addr'] + '/' + str(flow['src_mask']),
                        'dst_ip': flow['ipv4_dst_addr'] + '/' + str(flow['dst_mask']),
                        'src_port': flow['l4_src_port'],
                        'dst_port': flow['l4_dst_port']
                    }
                    problem_flow.append(flow_data)
            problem_flow_sorted = sorted(problem_flow, key=lambda d: d['in_bytes'], reverse=True)

            return problem_flow_sorted

        def stable_policy(all_policy):
            for policy in all_policy:
                if len(policy) != 15:
                    return False
            return True

        def do_loadbalance(problem_flow_sorted, link):
            all_link = requests.get("http://localhost:5001/api/v1/link").json()['links']
            def find_mmip(ip_and_slash):
                all_device = requests.get("http://localhost:5001/api/v1/device").json()['devices']
                for device in all_device:
                    for interface in device['interfaces']:
                        try:
                            ip4 = IPv4Network((0, interface['subnet']))
                            device_ip = interface['ipv4_address'] + '/' + str(ip4.prefixlen)
                            device_net_ip = IPv4Interface(device_ip)
                            if str(device_net_ip.network) == str(IPv4Interface(ip_and_slash).network):
                                return device['management_ip']
                        except:
                            # print('Interface not setting IP ignore it')
                            pass

            def check_dup_link(path, link_info, all_link, flow):
                link_list = []
                available_bandwidth_per_link = []
                for node_index in range(len(path)):
                    if node_index + 1 != len(path):
                        src = path[node_index]
                        dst = path[node_index+1]

                        

                        for each_link in all_link:
                            link_list.append(each_link)
                            if (src == each_link['src_node_ip'] or src == each_link['dst_node_ip']) \
                                and (dst == each_link['src_node_ip'] or dst == each_link['dst_node_ip']):
                                in_flow = int(max(each_link['src_in_use'], each_link['dst_out_use'])) + flow['in_bytes']
                                out_flow = int(max(each_link['src_out_use'], each_link['dst_in_use'])) + flow['in_bytes']
                                utilization_percent = round(decimal.Decimal((in_flow + out_flow)/(each_link['link_min_speed'])), 5)

                                available_bandwidth = float(each_link['link_min_speed'])*float(each_link['utilization_threshold']) - (in_flow + out_flow)

                                available_bandwidth_per_link.append(available_bandwidth)
                                if each_link['utilization_threshold'] < utilization_percent:
                                    return [True, available_bandwidth_per_link]
                            
                    if (src == link_info['link_mmip'][0] and dst == link_info['link_mmip'][1])\
                         or (src == link_info['link_mmip'][1] and dst == link_info['link_mmip'][0]):
                        return [True, available_bandwidth_per_link]
                return [False, available_bandwidth_per_link]
            
            def get_nexthop_from_management_ip(device_id1, device_id2, all_link):
                for link in all_link:
                    if device_id1 == link['src_node_ip'] and device_id2 == link['dst_node_ip']:
                        return link['dst_ip']
                    elif device_id1 == link['dst_node_ip'] and device_id2 == link['src_node_ip']:
                        return link['src_ip']
                return ['NOT FOUND']

            # def check_dup_policy(new_flow, all_policy):
            #     for policy in all_policy:
            #         try:
            #             policy_name = policy['name']
            #         except:
            #             policy_name = policy['new_flow']['name']
            #         if new_flow['name'] == policy_name:
            #             return True

            for flow in problem_flow_sorted:
                """
                flow = {
                'flow_id':str(flow['_id']),
                'in_bytes': '12345',
                'src_ip': '192.168.2.1/24',
                'dst_ip': '192.168.1.1/24'
                }
                """
                src_mmip = find_mmip(flow['src_ip'])
                dst_mmip = find_mmip(flow['dst_ip'])

                all_path = requests.get("http://localhost:5001/api/v1/path/" + src_mmip + "," + dst_mmip).json()['paths']
                
                # print('====================')
                
                path_index = 0
                use_path = None
                for path in all_path:
                    path_result = check_dup_link(path['path'], link, all_link, flow)
                    if not path_result[0]:
                        lowest_path_bandwidth = min(path_result[1])
                        if path_index == 0:
                            use_path = path
                            previous_lowest_path_bandwidth = min(path_result[1])
                        elif lowest_path_bandwidth > previous_lowest_path_bandwidth:
                            use_path = path
                        path_index += 1
                # print('====================')
                # print('#############')
                # print(use_path)
                # print('#############')

                
                if use_path != None:
                    src_info = flow['src_ip'].split('/')
                    dst_info = flow['dst_ip'].split('/')
                    new_flow = {
                        'name': src_info[0] + ':' +  str(flow['src_port']) + '-' + dst_info[0] + ':' + str(flow['dst_port']),
                        'src_ip': src_info[0], 
                        'src_port': flow['src_port'], 
                        'src_subnet':str(IPv4Address(int(IPv4Address._make_netmask(src_info[1])[0])^(2**32-1))), 
                        'dst_ip': dst_info[0], 
                        'dst_port': flow['dst_port'], 
                        'dst_subnet':str(IPv4Address(int(IPv4Address._make_netmask(dst_info[1])[0])^(2**32-1))), 
                        'actions':[]
                    }

                    for i in range(len(use_path['path'])-1):
                        device = requests.get("http://localhost:5001/api/v1/device/mgmtip/{}".format(
                            use_path['path'][i]
                        )).json()
                        device_id = device['device']['_id']['$oid']
                        next_hop_ip = get_nexthop_from_management_ip(use_path['path'][i], use_path['path'][i+1], all_link)
                        print(next_hop_ip)
                        action = {'device_id':device_id, 'action':2, 'data':next_hop_ip}
                        new_flow['actions'].append(action)


                    # print('$$$$$$$$$$$$$$$$$$$$')
                    # print(new_flow['name'])
                    # print('$$$$$$$$$$$$$$$$$$$$')


                    # requests.post("http://localhost:5001/api/v1/flow/routing", json=new_flow)
                    time.sleep(5)
                    break



        if not self.check_before_run():
            return

        # Update path

        print('--------------------')
        # devices = self.device_repository.get_all()
        # graphx = generate_graph.create_networkx_graph(devices)
        # print(list(graphx.nodes))
        # print(graphx.graph)
        # print(list(graphx.edges))

        # src_dst = '192.168.1.1,192.168.4.2'
        # path_info = requests.get("http://10.50.34.15:5001/api/v1/path/" + src_dst).json()['paths']
        # all_path = []
        # for path in path_info:
        #     all_path.append(path['path'])
        # print(all_path)



        link_utilization = []
        client = MongoClient('localhost', 27017)
        linK_database = client.sdn01.link_utilization
        for link in linK_database.find():
            in_flow = int(max(link['src_in_use'], link['dst_out_use']))
            out_flow = int(max(link['src_out_use'], link['dst_in_use']))
            utilization_percent = round(decimal.Decimal((in_flow + out_flow)/((link['link_min_speed'])/10)), 5)
            try:
                link_utilization.append({
                    'link_oid':link['_id'],
                    'utilization_percent':utilization_percent,
                    'treshold':link['utilization_threshold'],
                    'link_mmip':[link['src_node_ip'], link['dst_node_ip']]
                    })
            except:
                # print('no init utilization for this link yet now adding')
                linK_database.update_one({
                    "_id": link['_id']
                    }, {"$set": {
                    "utilization_threshold": 1,
                }})
        # print(link_utilization)
        for link in link_utilization:
            # print(a, type(a), a + 1, type(a + 1))
            print(link['utilization_percent'], link['treshold'], link['link_mmip'])
            if link['utilization_percent'] > link['treshold']:
                print('$$$$$$$$$$$$$$$$$$$$$$$$')
                print(link['utilization_percent'], link['link_oid'])
                print('$$$$$$$$$$$$$$$$$$$$$$$$')
                problem_flow_sorted = find_problem_flow(link, client)
                print(problem_flow_sorted)
                print('######################')
                all_policy = requests.get("http://localhost:5001/api/v1/flow/routing").json()['flows']
                if stable_policy(all_policy):
                    do_loadbalance(problem_flow_sorted, link)        
                """
                1. watch in link sort all flow 
                2. each flow have another possible path
                2.1 possible path
                """

#ไม่เจอ path ไปได้เลยทำไง ?
#เช็ค policy ซ้ำ


