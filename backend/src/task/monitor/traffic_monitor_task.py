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

    def check_before_run(self):
        if time.time() > self.last_run + self.delay:
            return True
        return False

    
    def get_all_link_utilization(self, controller_ip):
        """
        return all link utilization calculate by link_api sum of max in-out flow of 2 node
        """
        link_info = requests.get("http://" + controller_ip + ":5001/api/v1/link").json()['links']
        link_utilization = []
        for link in link_info:
            in_flow = int(max(link['src_in_use'], link['dst_out_use']))
            out_flow = int(max(link['src_out_use'], link['dst_in_use']))
            utilization_percent = round(decimal.Decimal((in_flow + out_flow)/(link['link_min_speed'])), 5)
            link_utilization.append({'link_oid':link['_id']['$oid'], 'utilization_percent':utilization_percent})
        return link_utilization

    def get_link_utilization(self, controller_ip, link_id):
        """
        return link utilization 
        """
        all_link = self.get_all_link_utilization(controller_ip)
        for link in all_link:
            if link['link_oid'] == link_id:
                return link


    def run(self, ssh_connection: SSHConnection = None):
        if not self.check_before_run():
            return

        # Update path

        print('--------------------')
        devices = self.device_repository.get_all()
        graphx = generate_graph.create_networkx_graph(devices)
        print(list(graphx.nodes))
        print(graphx.graph)
        print(list(graphx.edges))

        
        src_dst = '192.168.1.1,192.168.4.2'
        path_info = requests.get("http://10.50.34.15:5001/api/v1/path/" + src_dst).json()['paths']
        all_path = []
        for path in path_info:
            all_path.append(path['path'])

        print(all_path)
        print(self.get_all_link_utilization())
        print('--------------------')
        print('=======================')
