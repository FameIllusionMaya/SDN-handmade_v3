from bson.json_util import dumps, loads
from sanic.response import json
from sanic.views import HTTPMethodView
import networkx as nx

class GraphView(HTTPMethodView):

    def get(self, request):
        links_data = loads(dumps(request.app.db['link_utilization'].get_all()))
        devices_data = loads(dumps(request.app.db['link_utilization'].get_all()))

        

        nodes = {}
        edges = {}
        for link in links_data:
            src_node = link['src_node_hostname']
            dst_node = link['dst_node_hostname']
            nodes.update({
                src_node:{
                    'name': link['src_node_hostname'], 
                    'management_ip': link['src_node_ip']
                    }
                })
            nodes.update({
                dst_node:{
                    'name': link['dst_node_hostname'], 
                    'management_ip': link['dst_node_ip']
                    }
                })

            edges[f'edge{len(edges)}'] = {
                'dst_if_ip':link['dst_if_ip'], 
                'src_if_ip':link['src_if_ip'], 
                'source':nodes[src_node]['name'], 
                'target':nodes[dst_node]['name'], 
                'src_port':link['src_port'],  
                'dst_port':link['dst_port']
            }
        layout = graph_align(nodes.keys(), [(edges[eid]['source'], edges[eid]['target']) for eid in edges])
        graph = {"nodes":nodes, "edges":edges, 'layout':layout}
        return json({"graph": graph, "status": "ok"})

    def post(self, request):

        filters = request.json['filters']
        port_filters = [int(i) for i in filters['port_num']]
        source_filters = filters['src_ip']
        dest_filters = filters['dst_ip']
        # print(filters)


        links_data = loads(dumps(request.app.db['link_utilization'].get_all()))
        nodes = {}
        edges = {}

        flows_by_edge = {}

        flows = request.app.db['flow_stat'].get_all().sort("in_bytes", -1)
        flows_data = []
        links_with_flows = []
        for flow in flows:
            flow_data = {
                'src_ip':flow['ipv4_src_addr'], 
                'dst_ip':flow['ipv4_dst_addr'], 
                'src_port':flow['l4_src_port'],
                'dst_port':flow['l4_dst_port'],
                'next_hop_ip':flow['ipv4_next_hop'], 
                }
            if flow.get('Mbits_per_sec', ''):
                flow_data['flow_rate'] = '%.4f'%flow['Mbits_per_sec']
            else:
                flow_data['flow_rate'] = ''
            in_port_filters = (flow['l4_dst_port'] in port_filters) or (flow['l4_src_port'] in port_filters) or not port_filters
            in_src_filters = (flow['ipv4_src_addr'] in source_filters) or not source_filters
            in_dst_filter = (flow['ipv4_dst_addr'] in dest_filters) or not dest_filters
            if  in_port_filters and in_src_filters and in_dst_filter:
                links_with_flows.append(flow['ipv4_next_hop'])
                flows_data.append(flow_data)


        for link in links_data:
            src_node = link['src_node_hostname']
            dst_node = link['dst_node_hostname']
            nodes.update({
                src_node:{
                    'name': link['src_node_hostname'], 
                    'management_ip': link['src_node_ip']
                    }
                })
            nodes.update({
                dst_node:{
                    'name': link['dst_node_hostname'], 
                    'management_ip': link['dst_node_ip']
                    }
                })
            edge_id = f'edge{len(edges)}'
            edges[edge_id] = {
                'source':nodes[src_node]['name'], 
                'target':nodes[dst_node]['name'], 
                'src_port':link['src_port'],  
                'dst_port':link['dst_port'],
                'utilization_threshold':link['utilization_threshold']
            }
            
            flows_by_edge[edge_id] = []
            if link['dst_if_ip'] in links_with_flows or link['src_if_ip'] in links_with_flows:
                edges[edge_id]['animate'] = True
            for flow_data in flows_data:
                if flow_data['next_hop_ip'] in (link['dst_if_ip'], link['src_if_ip']):
                    if flow_data['src_port'] in port_filters or flow_data['dst_port'] in port_filters or not port_filters:
                        flows_by_edge[edge_id].append(flow_data)
        
        # nodes = {nodes[i]:{'name':i} for i in nodes}
        layout = graph_align(nodes.keys(), [(edges[eid]['source'], edges[eid]['target']) for eid in edges])
        graph = {"nodes":nodes, "edges":edges, "flows":flows_by_edge, 'layout':layout}
        return json({"graph": graph, "flows_data":flows_by_edge, "status": "ok"})
 
def convert_ip_to_network(ip, mask):
    bi_mask = '1'*mask + '0'*(32-mask)
    bi_ip = ''.join([bin(int(i)+256)[3:] for i in str(ip).split('.')])
    bi_network = ''.join([(x, '0')[y == '0'] for x, y in zip(bi_ip, bi_mask)])
    network_address = str(IPv4Address(int(bi_network, 2)))
    return network_address

def graph_align(nodes, edges, spread=100):
    """
    align the graph with fruchterman_reingold_layout
    nodes is list of node's name eg. [1, 2, 3]
    edges is list of tuples which contain name of pair nodes eg. [(1, 2), (2, 3), (2, 1)]
    """
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    position = nx.fruchterman_reingold_layout(graph)
    position = {'nodes':{name:{'x':position[name][0]*spread, 'y':position[name][1]*spread} for name in position}}

    return position
