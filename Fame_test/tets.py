from threading import Thread

class set_netflow_worker(Thread):
    def run(seld, device):
        try:
            print('[', device)
            for i in range(10):
                if i == 5:
                    a = int(sdfsdfs)
                print(i)
        except:
            print('error')

def init_netflow_setting():
    for device in range(10):
        set_netflow_worker().run(device)

init_netflow_setting()
