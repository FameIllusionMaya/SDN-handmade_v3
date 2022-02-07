# from pymongo import MongoClient
# import decimal
# import requests

from module import *

controller_ip = '10.50.34.15'

link_u = get_all_link_utilization(controller_ip)
link_u = get_link_utilization(controller_ip, '61fe0ac03e6eb1323cdb5e52')
print(link_u)
