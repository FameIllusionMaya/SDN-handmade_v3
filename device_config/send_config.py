from netmiko import ConnectHandler

username = 'cisco'
password = 'cisco'

for device_num in range(1, 40):
    device_ip = '192.168.' + str(device_num) + '.1'
    device_par = {'device_type': 'cisco_ios',
                  'ip': device_ip,
                  'username': username,
                  'password': password,
                  }

    with ConnectHandler(**device_par) as ssh:
        """config loopback / ACL for ssh / CDP interface description"""
        file_config = 'R' + str(device_num) + '.txt'
        config_sent = ssh.send_config_from_file(config_file=file_config)

        """show interface brief and save config"""
        # result = ssh.send_command('sh ip int br') + "\n"
        # result = result + ssh.send_command('sh ip access-lists') + "\n"
        # result = result + ssh.send_command('sh ip route') + "\n"
        # result = result + ssh.send_command('sh cdp') + "\n"
        # print(result)
        # ssh.send_command('write')  # save config
