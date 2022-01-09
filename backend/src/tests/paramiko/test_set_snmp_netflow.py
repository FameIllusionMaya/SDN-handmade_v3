import paramiko
import time
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
devices = client.week1_2019.device.find() #client.(database).(collection).find()

for device in devices:
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(device['management_ip'], port=22, username=device['ssh_info']['username'], password=device['ssh_info']['password'])
	remote_connect = ssh.invoke_shell()
	output = remote_connect.recv(1000)
	if output.decode("utf-8")[-1] == "#":
		print("Privileged mode")
	elif output.decode("utf-8")[-1] == ">":
		print("User mode")
		remote_connect.send("enable\n")
		time.sleep(0.1)
		remote_connect.send(input()+"\n")
	else:
		pass
	interface = 'f0/1' #interface connect to management ip
	ip = '192.168.1.100' #ip management device
	port = '23456'
	source_interface = 'f0/1'
	netflow_commands = ['interface '+interface+'\n', 'ip route-cache flow\n', 'exit\n', 'ip flow-export destination '+ip+' '+port+'\n', 'ip flow-export source '+source_interface+'\n', 'ip flow-export version 9\n', 'ip flow-cache timeout active 1\n', 'ip flow-cache  timeout inactive 15\n', 'ip flow-export template refresh-rate 1\n']
	snmp_commands = ['snmp-server enable traps\n', 'snmp-server community public RO\n', 'snmp-server community private RW\n']
	commands = ['conf t\n']+netflow_commands+snmp_commands
	for command in commands:
		remote_connect.send(command)
		time.sleep(0.1)
	ssh.close()