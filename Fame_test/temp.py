from netmiko import ConnectHandler
import time
from pymongo import MongoClient
from threading import Thread




client = MongoClient('localhost', 27017)



def run():

    device_shell_info = {
            'device_type': 'cisco_ios',
            'host': '192.168.58.1',
            'username': 'cisco',
            'password': 'cisco',
            'secret':  'cisco',
            'port': 22
            }

    print(device_shell_info)
        
    ssh = ConnectHandler(**device_shell_info)
    ssh.enable()
    # set netflow
    cmds = ['snmp-server enable traps', 'snmp-server community public RO', 'snmp-server community private RW']
    print('***********')
    _ = [print(i) for i in cmds]

    ssh.send_config_set(cmds)
    return []
    # ssh.close()
    # return []



print(run())
