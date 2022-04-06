from ast import Try
import datetime
import logging
import time

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
                        'in_pkts':flow['in_pkts'],
                        'src_ip': flow['ipv4_src_addr'] + '/' + str(flow['src_mask']),
                        'dst_ip': flow['ipv4_dst_addr'] + '/' + str(flow['dst_mask'])
                    }
                    problem_flow.append(flow_data)
            problem_flow_sorted = sorted(problem_flow, key=lambda d: d['in_pkts'], reverse=True)
            return problem_flow_sorted

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

            def check_dup_link(path, link_src_dst, all_link, flow):
                link_path_list = []
                for node_index in range(len(path)):
                    if node_index + 1 != len(path):
                        src = path[node_index]
                        dst = path[node_index+1]
                        for link in all_link:
                            print(src, dst, link['dst_node_ip'], link['src_node_ip'])
                            if (src == link['src_node_ip'] or src == link['dst_node_ip']) and (dst == link['src_node_ip'] or dst == link['dst_node_ip']):
                                in_flow = int(max(link['src_in_use'], link['dst_out_use'])) + flow['in_pkts']
                                out_flow = int(max(link['src_out_use'], link['dst_in_use'])) + flow['in_pkts']
                                utilization_percent = round(decimal.Decimal((in_flow + out_flow)/(link['link_min_speed'])), 5)
                                link_path_list.append(link['_id'])
                    if (src == link_src_dst[0] and dst == link_src_dst[1]) or (src == link_src_dst[1] and dst == link_src_dst[0]):
                        return [True, link_path_list]
                print(link_path_list)
                return [False, link_path_list]


            for flow in problem_flow_sorted:
                """
                flow = {
                'flow_id':str(flow['_id']),
                'in_pkts': '12345',
                'src_ip': '192.168.2.1/24',
                'dst_ip': '192.168.1.1/24'
                }
                """
                src_mmip = find_mmip(flow['src_ip'])
                dst_mmip = find_mmip(flow['dst_ip'])
                path_choice = []
                all_path = requests.get("http://localhost:5001/api/v1/path/" + src_mmip + "," + dst_mmip).json()['paths']
                print('====================')
                for path in all_path:
                    if not check_dup_link(path['path'], link['link_mmip'], all_link, flow)[0]:
                        path_choice.append(path['path'])
                print('====================')
                print(path_choice)
                print(src_mmip, dst_mmip)
                print(link)
                print('====================')
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
            utilization_percent = round(decimal.Decimal((in_flow + out_flow)/(link['link_min_speed'])), 5)
            try:
                link_utilization.append({
                    'link_oid':link['_id'],
                    'utilization_percent':utilization_percent,
                    'treshold':link['utilization_treshold'],
                    'link_mmip':[link['src_node_ip'], link['dst_node_ip']]
                    })
            except:
                # print('no init utilization for this link yet now adding')
                linK_database.update_one({
                    "_id": link['_id']
                    }, {"$set": {
                    "utilization_treshold": 1,
                }})
        # print(link_utilization)
        for link in link_utilization:
            # print(a, type(a), a + 1, type(a + 1))
            print(link['utilization_percent'], link['treshold'])
            if link['utilization_percent'] > link['treshold']:
                problem_flow_sorted = find_problem_flow(link, client)
                do_loadbalance(problem_flow_sorted, link)

                """
                1. watch in link sort all flow 
                2. each flow have another possible path
                2.1 possible path
                """



