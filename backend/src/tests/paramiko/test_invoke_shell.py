import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.1', port=22, username='cisco', password='cisco')
# if SSHException: Server '192.168.5.1' not found in known_hosts use command >>>ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) and use command ssh.connect .. again
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
commands = ["configure terminal\n", "interface Serial0/1/0\n", "ip address 192.168.88.1 255.255.255.0\n", "no shutdown\n"]
#commands = ["show ip int br\n"]
for command in commands:
	remote_connect.send(command)
	time.sleep(0.1)
ssh.close()