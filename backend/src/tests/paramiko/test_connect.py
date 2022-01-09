import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.5.1', port=22, username='cisco', password='cisco')
# if SSHException: Server '192.168.5.1' not found in known_hosts use command >>>ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) and use command ssh.connect .. again
stdin, stdout, stderr = ssh.exec_command('show ip interface brief')
output = stdout.readlines()
print('\n'.join(output))
