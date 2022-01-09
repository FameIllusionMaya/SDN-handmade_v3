from bson.json_util import dumps
from sanic.response import json
from sanic.views import HTTPMethodView

from tools import PathFinder


class PathView(HTTPMethodView):

    def get(self, request, src_dst):
        src, dst = src_dst.split(',')
        path_finder = PathFinder()
        paths = path_finder.all_by_manage_ip(src, dst)
        list_path = []
        for path in paths:
            set_path = {
                'route_id' : path[0]+","+('0.0.0.0' if len(path)<=2 else path[1])+","+path[-1],
                'start_node' : path[0],
                'nexthop_node' : '0.0.0.0' if len(path)<=2 else path[1],
                'end_node' : path[-1],
                'path' : path
            }
            list_path.append(set_path)
        return json({"paths": list_path, "status": "ok"}, dumps=dumps)
