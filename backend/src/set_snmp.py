from netmiko import ConnectHandler
import time
from pymongo import MongoClient
from threading import Thread
from router_command.policy_command import generate_snmp_init_command



client = MongoClient('localhost', 27017)
# devices = client.sdn01.device.find() #client.(database).(collection).find()

class set_snmp_worker(Thread):
    def run(self, device):
        try:
            if device['is_snmp_connect'] and device['cdp_enable']:
                return []
            print(device)
            device_shell_info = {
                    'device_type': device['type'],
                    'host': device['management_ip'],
                    'username': device['ssh_info']['username'],
                    'password': device['ssh_info']['password'],
                    'secret':  device['ssh_info']['secret'],
                    'port': device['ssh_info']['port']
                    }
                
            ssh = ConnectHandler(**device_shell_info)
            ssh.enable()
            # set netflow
            cmds = generate_snmp_init_command(device['type'])
            print('***********')
            _ = [print(i) for i in cmds]

            ssh.send_config_set(cmds)
            ssh.close()
            return []
        except :
            return [device['management_ip']]


def sleep(device_connection):
    while(device_connection.recv(65535).decode("utf-8")[-1] not in "#>"):
        time.sleep(0.1)


def init_snmp_setting(devices):
    problem_devices = []
    for device in devices:
        problem_devices += set_snmp_worker().run(device)
    return problem_devices
