import paramiko
import time
from pymongo import MongoClient
from threading import Thread
import repository

client = MongoClient('localhost', 27017)
# devices = client.sdn01.device.find() #client.(database).(collection).find()

class set_netflow_worker(Thread):
    def run(seld, device, management_ip):
        try:
            if device['is_netflow']:
                return []
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(device['management_ip'], port=22, username=device['ssh_info']['username'], password=device['ssh_info']['password'])
            remote_connect = ssh.invoke_shell()
            output = remote_connect.recv(65535)
            print(output.decode("utf-8"))
            print("connect to "+device['management_ip'], end=" ")
            if output.decode("utf-8")[-1] == "#":
                print("Privileged mode")
            elif output.decode("utf-8")[-1] == ">":
                print("User mode")
                remote_connect.send("enable\n")
                time.sleep(0.5)
                remote_connect.send(device['ssh_info']['secret']+"\n")
                time.sleep(0.5)
            # set netflow
            interfaces = client.sdn01.device.find({'management_ip': device['management_ip']}, {'_id':0, 'interfaces': 1})
            remote_connect.send('conf t\n')
            time.sleep(0.5)
            for interface in interfaces:
                for iface in interface['interfaces']:
                    if "ipv4_address" in iface:
                        for command in ['interface '+iface["description"]+'\n', 'ip policy route-map SDN-handmade\n', 'ip route-cache flow\n', 'exit\n']:
                            print(command)
                            remote_connect.send(command)
                            time.sleep(0.5)
                            #print(remote_connect.recv(10000))
            ip = management_ip #ip management device get from db later
            port = '23456'
            for command in ['ip flow-export destination '+ip+' '+port+'\n', 'ip flow-export version 9\n', 'ip flow-cache timeout active 1\n', 'ip flow-cache timeout inactive 2\n', 'ip flow-export template refresh-rate 1\n']:
                remote_connect.send(command)
                time.sleep(0.5)
            print('Hi I AM here')
            print('Hi I AM here')
            print('Hi I AM here')
            print('Hi I AM here')
            device_repository = repository.get("device")
            device_repository.set_snmp_is_connect_by_mgmt_ip(management_ip, True)
            print('heyqqqqqqqqqqqqqqqqqqqqqqq')
            ssh.close()
        except:
            print('device error while netflow maybe ssh refuse')
            # device_repository.set_snmp_is_connect_by_mgmt_ip(host, False)
            return [device['management_ip']]

def init_netflow_setting(devices, management_ip):
    problem_devices = []
    for device in devices:
        problem_devices += set_netflow_worker().run(device, management_ip)
    return problem_devices
