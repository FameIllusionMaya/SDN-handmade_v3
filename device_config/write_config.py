"""

host R2
int g0/0
ip add 192.168.2.1 255.255.255.0
no shut
int g0/1
ip add 192.168.1.2 255.255.255.0
no shut
router ospf 1
net 192.168.1.0 0.0.0.255 a 0
net 192.168.2.0 0.0.0.255 a 0
"""
for i in range(2,6):
    file_name = 'R' + str(i) + '.txt'
    f = open(file_name, "w")
    line = 'host R' + str(i) + '\n'
    f.write(line)
    line = 'int g0/0\n'
    f.write(line)
    line = 'ip add 192.168.' + str(i) + '.1 255.255.255.0\n'
    f.write(line)
    line = 'no shut\n'
    f.write(line)
    line = 'int g0/1\n'
    f.write(line)
    line = 'ip add 192.168.' + str(i-1) + '.2 255.255.255.0\n'
    f.write(line)
    line = 'no shut\n'
    f.write(line)
    line = 'router ospf 1\n'
    f.write(line)
    line = 'net 192.168.' + str(i-1) + '.0 0.0.0.255 a 0'
    f.write(line)
    line = 'net 192.168.' + str(i) + '.0 0.0.0.255 a 0'
    f.write(line)

    f.close()
