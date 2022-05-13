import time
from pymongo import MongoClient
import requests
from threading import Thread
from ipaddress import IPv4Network, IPv4Address, ip_network

import logging
import socket
import threading
import traceback
from datetime import datetime, timedelta

import repository
import sdn_utils
from netflow.netflow_packet import ExportPacket


class Counter(Thread):
    def __init__(self, key, info, client, aging_time):
        Thread.__init__(self)
        self.key = key
        self.info = info
        self.timeout = aging_time
        self.client = client
        

    def run(self):
        def convert_ip_to_network(ip, mask):
            bi_mask = '1'*mask + '0'*(32-mask)
            bi_ip = ''.join([bin(int(i)+256)[3:] for i in str(ip).split('.')])
            bi_network = ''.join([(x, '0')[y == '0'] for x, y in zip(bi_ip, bi_mask)])
            network_address = str(IPv4Address(int(bi_network, 2)))
            return network_address

        print('2222222222222222222222222222')
        print('Start Countdown', self.key)
        print('2222222222222222222222222222')
        time.sleep(self.timeout)
        while True:
            print('333333333333333333333')
            print('Start search flow alive')
            print('333333333333333333333')
            query_filter = {}
            for i in self.key:
                if self.key[i].lower() != 'any':
                    if 'addr' in i:
                        ip_prefix = IPv4Address._prefix_from_ip_int(int(IPv4Address(self.info[i + '_wildcard']))^(2**32-1))
                        ip_network = IPv4Network(convert_ip_to_network(self.key[i], int(ip_prefix)) + '/' + str(ip_prefix))
                        query_filter[i] = {'$in':[str(i) for i in ip_network]}
                    else:
                        query_filter[i] = int(self.key[i])

            check = 0
            flows = self.client.sdn01.flow_stat.find(query_filter)
            for i in flows:
                check = 1
            
            if check:
                print('44444444444444444444444444')
                print('flow found continue counrdown')
                print('44444444444444444444444444')
                time.sleep(self.timeout)
            else:
                print('55555555555555555555555555')
                print('Delete Flow')
                print('55555555555555555555555555') 
                payload = {'flow_id': self.info['flow_id']}
                requests.delete("http://localhost:5001/api/v1/flow/routing",  params=payload)
                break


class TimerPolicyWorker(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.client = MongoClient('localhost', 27017)
        self.name = 'agingtime-sv'
        self.stop_flag = False

    def run(self):
        """ Create AgingTime Server
        """
        while not self.stop_flag:
            print('11111111111111111111111111')
            print('Policy Aging is Running....')
            print('11111111111111111111111111')
            self.flow = self.client.sdn01.flow_routing.find()
            for obj in self.flow:
                if len(obj) == 15:
                    key = {
                        'ipv4_src_addr' : obj['src_ip'],
                        'l4_src_port' : obj['src_port'],
                        'ipv4_dst_addr' : obj['dst_ip'],
                        'l4_dst_port' : obj['dst_port'],
                        }
                    info = {
                        'ipv4_src_addr_wildcard' : obj['src_wildcard'],
                        'ipv4_dst_addr_wildcard' : obj['dst_wildcard'],
                        'flow_id' : obj['flow_id']
                    }
                    print('HUEHUEHUE')
                    key = {i:obj[i] for i in ['src_ip', 'src_port', 'dst_ip', 'dst_port', 'src_wildcard', 'dst_wildcard', 'flow_id']}
                    if obj['aging_time']:
                        Counter(key, info, self.client, obj['aging_time']).start()
            time.sleep(10)


    def shutdown(self):
        """ Stop netflow Server
        """
        logging.info("AgingTime erver: shutdown...")
        self.stop_flag = True


    # def __init__(self):
    #     self.client = MongoClient('localhost', 27017)

    # def run(self):
    #     while True:
    #         print('11111111111111111111111111')
    #         print('Policy Aging is Running....')
    #         print('11111111111111111111111111')
    #         self.flow = self.client.sdn01.flow_routing.find()
    #         for obj in self.flow:
    #             if len(obj) == 15:
    #                 key = {
    #                     'ipv4_src_addr' : obj['src_ip'],
    #                     'l4_src_port' : obj['src_port'],
    #                     'ipv4_dst_addr' : obj['dst_ip'],
    #                     'l4_dst_port' : obj['dst_port'],
    #                     }
    #                 info = {
    #                     'ipv4_src_addr_wildcard' : obj['src_wildcard'],
    #                     'ipv4_dst_addr_wildcard' : obj['dst_wildcard'],
    #                     'flow_id' : obj['flow_id']
    #                 }
    #                 print('HUEHUEHUE')
    #                 key = {i:obj[i] for i in ['src_ip', 'src_port', 'dst_ip', 'dst_port', 'src_wildcard', 'dst_wildcard', 'flow_id']}
    #                 if obj['aging_time']:
    #                     Counter(key, info, self.client, obj['aging_time']).start()
    #         time.sleep(10)
