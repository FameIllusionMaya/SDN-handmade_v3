from netmiko import ConnectHandler
import time
from pymongo import MongoClient
from threading import Thread
import repository
from router_command.policy_command import generate_netflow_init_command

client = MongoClient('localhost', 27017)
# devices = client.sdn01.device.find() #client.(database).(collection).find()

class set_netflow_worker(Thread):
    def run(seld, device, controller_ip):
        # try:
        # if device['is_netflow']:
        #     return []
        
        device_shell_info = {
            'device_type': device['type'],
            'host': device['management_ip'],
            'username': device['ssh_info']['username'],
            'password': device['ssh_info']['password'],
            'secret':  device['ssh_info']['secret'],
            'port': device['ssh_info']['port']
            }
        
        ssh = ConnectHandler(**device_shell_info)

        # set netflow
        interfaces = client.sdn01.device.find({'management_ip': device['management_ip']}, {'_id':0, 'interfaces': 1})
        cmds = generate_netflow_init_command(device['type'], controller_ip, interfaces)
        ssh.enable()
        ssh.send_config_set(cmds)

        device_repository = repository.get("device")
        device_repository.set_netflow_is_connect_by_mgmt_ip(device['management_ip'], True)
        return []
        # ssh.close()
        # return []

        # except:
            # return [device['management_ip']]

def init_netflow_setting(devices, management_ip):
    problem_devices = []
    for device in devices:
        problem_devices += set_netflow_worker().run(device, management_ip)
    return problem_devices
