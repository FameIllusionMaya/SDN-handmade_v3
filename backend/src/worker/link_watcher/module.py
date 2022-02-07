from pymongo import MongoClient
import decimal
import requests


def get_all_link_utilization(controller_ip):
    """
    return all link utilization calculate by link_api sum of max in-out flow of 2 node
    """
    link_info = requests.get("http://" + controller_ip + ":5001/api/v1/link").json()['links']
    link_utilization = []
    for link in link_info:
        in_flow = int(max(link['src_in_use'], link['dst_out_use']))
        out_flow = int(max(link['src_out_use'], link['dst_in_use']))
        utilization_percent = round(decimal.Decimal((in_flow + out_flow)/(link['link_min_speed'])), 5)
        link_utilization.append({'link_oid':link['_id']['$oid'], 'utilization_percent':utilization_percent})
    return link_utilization

def get_link_utilization(controller_ip, link_id):
    """
    return link utilization 
    """
    all_link = get_all_link_utilization(controller_ip)
    for link in all_link:
        if link['link_oid'] == link_id:
            return link
