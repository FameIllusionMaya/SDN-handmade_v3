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
        devices = self.device_repository.get_all()
        link_info = self.path_finder.get_links()
        print('--------------------')
        print(devices)
        print('--------------------')

        print('=======================')
        # self.path_finder.save_graph_img()


