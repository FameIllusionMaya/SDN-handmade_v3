""" Database management """
import pymongo
# from config.database import MONGO_DB
import os
import settings

DEFAULT_CONNECTION_NAME = None


def set_connection_name(name):
    """Set the connection name by assign it to global variable name DEFAULT_CONNECTION_NAME"""
    global DEFAULT_CONNECTION_NAME
    DEFAULT_CONNECTION_NAME = name


_connections = {}


def get_mongodb(alias=None):
    """
    create connection handler with alias database and add to _connections dict
    and return the connection created.
    """
    # global _connections
    #if there are no alias, use global default connection name instead
    if not alias:
        alias = DEFAULT_CONNECTION_NAME
    alias_original = alias
    alias = alias + str(os.getpid())
    #if there are no connections with alias's database yet, get configuration of database from settings
    if _connections.get(alias) is None:
        #get alias's database configuration from settings
        config = settings.database.get(alias_original)
        #make sure that database is mongodb so we can handle with
        if config is not None:
            if config.get('driver', '') != 'mongodb':
                raise ValueError("config driver is not mongodb")
            #get max pool size of connection with alias's database (default is 10)
            max_pool_size = config.get('max_pool_size', 10)
            _connections[alias] = MongoDB(config['uri'], config['database'], max_pool_size)
        else:
            raise ValueError("Can't find config alias name %s" % alias)
    return _connections[alias]
    # if alias not in _connections:
    #     # Check mongodb configuration
    #     config = settings.database.get(alias_original)
    #     if config is not None:
    #         if config.get('driver', '') != 'mongodb':
    #             raise ValueError("config driver is not mongodb")
    #         max_pool_size = config.get('max_pool_size', 10)
    #         _connections[alias] = MongoDB(config['uri'], config['database'], max_pool_size)
    #     else:
    #         raise ValueError("Can't find config alias name %s" % alias)
    # return _connections[alias]


def disconnect(alias=DEFAULT_CONNECTION_NAME):
    """terminate connections with alias's database, delete connection's object from _connections also."""
    if alias in _connections:
        _connections[alias].client.close()
        del _connections[alias]

#Mongdo DB connection class use to store database configuration but not to manage anything
#GONNA fix this by add managing method to this class so we can manage database by this class object.
class MongoDB:
    def __init__(self, uri, database, max_pool_size=10):
        self.client = pymongo.MongoClient(uri, maxPoolSize=max_pool_size)
        self.pymongo = pymongo
        # Define Database
        self.db = self.client[database]

        # Define Collection
        self.netflow = self.db.netflow
        self.snmp = self.db.snmp
        self.device = self.db.device
        self.route = self.db.route

        self.flow_table = self.db.flow_table

        self.device_config = self.db.device_config
        self.cdp = self.db.cdp

        # Flow sequence
        self.flow_seq = self.db.flow_seq

        self.app = self.db.app
