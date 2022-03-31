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
        def do_loadbalacing(problem_link, client):
            #running_flow = [{'oid':'xxxx'}, {'oid':'xxxx'}, {'oid':'xxxx'}]
            url = "http://localhost:5001/api/v1/link/" + str(problem_link['link_oid'])
            running_flow_id_json = requests.get(url).json()['link'][0]['running_flows']
            running_flow_id = [str(i['$oid']) for i in running_flow_id_json]
            print(running_flow_id)
            flow_database = client.sdn01.flow_stat
            for flow in flow_database.find():
                print(str(flow['_id']))

                
            print('do load balance')
            print('I load balace please')
            print('++++++++++++++')
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
                link_utilization.append({'link_oid':link['_id'], 'utilization_percent':utilization_percent, 'treshold':link['utilization_treshold']})
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
                do_loadbalacing(link, client)

                """
                1. watch in link sort all flow 
                2. each flow have another possible path
                2.1 possible path
                """



