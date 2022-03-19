"""Adding device by calling API"""

from pymongo import MongoClient
import requests


controller_ip = '10.50.34.15'
# device_list = ['192.168.11.1', '192.168.12.1', '192.168.13.1', '192.168.14.1', '192.168.15.1', '192.168.16.1']
device_list = []
for i in range(1, 7):
    device_list.append('100.1.' + str(i) + '.1')
print(device_list)



def add_device():
    for device in device_list:
        print("adding device", device)
        payload = {
            'management_ip': device,
            'type': 'cisco_ios',
            'ssh_info':{
                'username':'cisco',
                'password':'cisco',
                'port':22,
                'secret':'cisco'
            },
            'snmp_info':{
                'version':'2c',
                'community':'public',
                'port':161
            }
        }
        requests.post("http://" + controller_ip +  ":5001/api/v1/device", json=payload)


def remove_all_device():
    device_list = requests.get("http://" + controller_ip + ":5001/api/v1/device").json()
    for device in device_list['devices']:
        remove_device(device['_id']['$oid'])

def remove_device(id):
    print("send command remove device id:", id)
    requests.delete("http://" + controller_ip + ":5001/api/v1/device",  params={'device_id': id})

def initialize():
    requests.post("http://" + controller_ip +  ":5001/api/v1/initialization", json={'service': 'snmp', 'management_ip':controller_ip})

def set_netflow():
    requests.post("http://" + controller_ip +  ":5001/api/v1/initialization", json={'service': 'netflow', 'management_ip':controller_ip})

def do_all():
    add_device()
    initialize()
    set_netflow()

def policy_test():
    src_net = '192.168.8.0'
    src_port = 'any'
    src_wildcard = '0.0.0.255'
    dst_net = '192.168.10.0'
    dst_port = '5555'
    dst_wildcard = '0.0.0.255'
    action = [{'device_id':'6231e19f3e6eb1323cb9c426', 'action':2, 'data':'192.168.7.49'}]
    new_flow = {'name':'new_route', 'src_ip':src_net, 'src_port':src_port, 'src_subnet':src_wildcard, 'dst_ip':dst_net, 'dst_port':dst_port,\
         'dst_subnet':dst_wildcard, 'actions':action, 'aging_time': 60}
    requests.post("http://"+controller_ip+":5001/api/v1/flow/routing", json=new_flow)
    action = [{'device_id':'61baf53414f944ac9726c332', 'action':2, 'data':'192.168.7.34'}]

def test():
    print(requests.patch("http://10.50.34.15:5001/api/v1/link", json={'link_id':'622302333e6eb1323c50ca39' ,'utilization_treshold': 0.01}))


def main():
    print("1 : Add Device")
    print("2 : Remove All Device ")
    print("3 : Set Initialization")
    print("4 : Set NetFlow")
    print("5 : Add Device + Init + Netflow")
    print("6 : test function")
    print("9 : add policy [Test]")
    action = input("Action : ")
    if action == '1':
        add_device()
    elif action == '2':
        remove_all_device()
    elif action == '3':
        initialize()
    elif action == '4':
        set_netflow()
    elif action == '6':
        test()
    elif action == '5':
        do_all()
    else:
        policy_test()

main()


