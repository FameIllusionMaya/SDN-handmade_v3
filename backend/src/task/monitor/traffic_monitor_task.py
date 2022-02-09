import datetime
import logging
import time

import sdn_utils
from repository import get, PolicyRoute
from tools import PathFinder
from worker.ssh.ssh_worker import SSHConnection
import pprint


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

    def run(self, ssh_connection: SSHConnection = None):
        if not self.check_before_run():
            return





        # Update path
        self.path_finder.update_graph()
        print('--------------------')
        print(self.path_finder.get_links())

        print('--------------------')
        # self.path_finder.save_graph_img()


        
    def find_available_path(self, src_node_ip, dst_node_ips, initial=False):
        # Todo Getting available paths
        src_flow = self.current_flow['_id']['ipv4_src_addr']
        dst_flow = self.current_flow['_id']['ipv4_dst_addr']

        # first_switched = self.current_flow['_id']

        # Finding path
        if not initial:
            for dst_node_ip in dst_node_ips:
                paths = self.path_finder.find_by_available_bandwidth(
                    src_node_ip,
                    dst_node_ip,
                    PathFinder.SelectBy.HIGHEST,
                    self.current_flow['in_bytes_per_sec'] * 8  # Minimum free bandwidth
                )
                for path in paths:
                    # Source is R3
                    #  Active => [R1, R2, R3, R4, R5]
                    #  Case 1   => [R3, R2, R1, ...] X because R2 is reverse path -> looping
                    #  Case 2   => [R3, R6, ...] Y
                    #  Case 3   => [R3, R6, R2, R3, ...] Todo Checking
                    #
                    #  Check loop
                    for active_path in self.active_paths:  # many src_node -> many dst_node
                        if active_path is None:
                            continue
                        for _active_path in active_path:  # some path have multiple paths
                            try:
                                node_active_path_index = list(_active_path).index(src_node_ip)
                            except ValueError:
                                continue
                            before_node = _active_path[node_active_path_index - 1]
                            logging.debug("before_node: %s", before_node)
                            logging.debug("src node ip: %s, dst node ip: %s <=> Active path is %s", src_node_ip,
                                          dst_node_ip, _active_path)

                            # Case 1
                            #  path['path'][1] mean next node ip
                            if path['path'][1] == before_node:  # Detect loop, skip
                                continue
                            # Case 3
                            elif src_node_ip in path['path'][1:]:
                                continue
                            # Case 2
                            else:
                                logging.debug("Found path: %s, Available bw %s", path['path'],
                                              path['available_bandwidth'])
                                return path
        else:
            self.reverse_path.append(src_node_ip)

        # If can't find a new path
        # Find neighbor link device
        if src_node_ip in self.explorer_neighbor:
            logging.debug("Explorer neighbor %s, next explore %s", self.explorer_neighbor, src_node_ip)
            return
        node_ips = self.find_neighbor_link(src_node_ip, src_flow, dst_flow)
        self.explorer_neighbor.append(src_node_ip)
        for node_ip in node_ips:
            # logging.debug(node_ip)
            # if initial:
            self.reverse_path.append(node_ip['src_node_ip'])
            self.reverse_path_link.append({
                'out': node_ip['src_if_ip'],
                'in': node_ip['dst_if_ip']
                # 'out': node_ip['dst_if_ip'],
                # 'in': node_ip['src_if_ip']
            })

            # Find path from prevent path of active flow
            new_path = self.find_available_path(node_ip['src_node_ip'], dst_node_ips)
            # If found new path
            if new_path:
                # self.reverse_path.append(node_ip['src_if_ip'])
                return new_path

            # Remove not used path.
            self.reverse_path = self.reverse_path[:-1]
            self.reverse_path_link = self.reverse_path_link[:-1]
        return None

    def find_neighbor_link(self, src_node_ip, src_ip, dst_ip):
        logging.debug("Find neighbor: %s %s %s", src_node_ip, src_ip, dst_ip)
        # Find interfaces than receive this flow
        flow_from = self.flow_stat_repository.model.aggregate([{
            '$match': {
                'ipv4_src_addr': src_ip,
                'ipv4_dst_addr': dst_ip,
                # Todo support port, protocol
                'from_ip': src_node_ip
            }
        }, {
            '$group': {
                '_id': {
                    'input_snmp': '$input_snmp'
                },
                'in_bytes': {'$sum': '$in_bytes'}
            }
        }])
        # flow_from = self.netflow_service.netflow.find({
        #     'ipv4_src_addr': src_ip,
        #     'ipv4_dst_addr': dst_ip,
        #     'from_ip': src_node_ip
        # })

        node_ips = []

        for _flow in flow_from:
            # TODO Improve performance
            # Get interface index
            src_if_index = _flow['_id']['input_snmp']
            # src_if_ip = self.device_service.get_if_ip_by_if_index(src_node_ip, src_if_index)
            # my_links = self.link_service.find_by_if_ip(src_if_ip)
            # Find links than connected
            my_links = self.link_utilization_repository.find_by_if_index(src_node_ip, src_if_index)
            # Loop all links
            for link in my_links:
                # logging.debug(link)
                if link['src_node_ip'] == src_node_ip:
                    src_node_ip = link['dst_node_ip']
                    src_if_ip = link['dst_if_ip']
                    dst_node_ip = link['src_node_ip']
                    dst_if_ip = link['src_if_ip']
                else:
                    src_node_ip = link['src_node_ip']
                    src_if_ip = link['src_if_ip']
                    dst_node_ip = link['dst_node_ip']
                    dst_if_ip = link['dst_if_ip']
                node_ips.append({
                    'src_node_ip': src_node_ip,
                    'dst_node_ip': dst_node_ip,
                    'src_if_ip': src_if_ip,
                    'dst_if_ip': dst_if_ip
                })
        return node_ips
