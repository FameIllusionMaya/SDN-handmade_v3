from tools import PathFinder
import logging
import time
import traceback

from concurrent.futures import ThreadPoolExecutor



class TrafficDisWorker:
    def __init__(self):
        self.test = 'No'

    def start(self):
        self.pool = ThreadPoolExecutor(1)
        # Start control worker queue
        self.pool.submit(self._control_worker_queue, self.results_q, self.stop_control_q)
        time.sleep(1)
        # Todo initial task

        # -------------------
        while True:

            try:
                print('fdfsdfsdfsdfsdfsfs')
                print('fdfsdfsdfsdfsdfsfs')
                print('fdfsdfsdfsdfsdfsfs')
                print('fdfsdfsdfsdfsdfsfs')
                time.sleep(3)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error(traceback.format_exc())
