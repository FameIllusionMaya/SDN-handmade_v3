from bson.json_util import dumps
from sanic.response import json
from sanic.views import HTTPMethodView


class LinkView(HTTPMethodView):

    def get(self, request, _id=None):  
        if _id is None:
            links = request.app.db['link_utilization'].get_all()
            return json({"links": links, "status": "ok"}, dumps=dumps)
        elif len(_id) == 24:
            link = request.app.db['link_utilization'].get_by_id(_id)
            return json({"link": link, "status": "ok"}, dumps=dumps)
        link = request.app.db['link_utilization'].get_by_name(_id)
        return json({"link": link, "status": "ok"}, dumps=dumps)

    def patch(self, request, _id=None):
        """edit link utilization treshold"""
        link_id = '6220de9b3e6eb1323c2d9692'
        print('-------------------')
        print(request.json)
        print('-------------------')
        request.app.db["link_utilization"].update_one({
            '_id': link_id
        }, {
            '$set': {
                'utilization_treshold': 50
            }
        }, upsert=True)
        return json({"status": True, "message": "Update link treshold!"})


        
