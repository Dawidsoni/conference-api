import json
import xml.etree.ElementTree as xmlEl
from db_connection import DbConnection
from connection_controller import ConnectionController
from auth_controller import AuthController
from user_controller import UserController
from query_helper import QueryHelper
from event_controller import EventController
from talk_controller import TalkController
from talk_proposal_controller import TalkProposalController
from query_config import QueryConfig
from json_encoder import JsonEncoder


class QueryHandler(object):

    def __init__(self):
        self.db_connection = DbConnection()
        self.connection_controller = ConnectionController(self.db_connection)
        self.auth_controller = AuthController(self.db_connection)
        self.user_controller = UserController(self.db_connection)
        self.event_controller = EventController(self.db_connection)
        self.talk_controller = TalkController(self.db_connection)
        self.talk_proposal_controller = TalkProposalController(self.db_connection)
        self.config_map = self.get_config()

    def process_query_config(self, config, config_map):
        name, controller, method_name = config["name"], config["controller"], config["method"]
        query_func = getattr(getattr(self, controller), method_name)
        config_map[name] = QueryConfig(query_func, config)

    def get_config(self):
        try:
            config_map = {}
            config_root = xmlEl.parse('config.xml').getroot()
            assert(config_root.tag == "query-map-config")
            for query_node in config_root:
                self.process_query_config(query_node.attrib, config_map)
            return config_map
        except Exception as exc:
            print("Error while processing config file")
            raise Exception("Query handler can't be initialized")

    @staticmethod
    def encode_query(query):
        return json.dumps(query, cls=JsonEncoder)

    @staticmethod
    def decode_query(query):
        return json.loads(query)

    def process_auth(self, query, query_config):
        if query_config.auth_type is None:
            return {}
        auth_type = query_config.auth_type
        login_field, password_field = query_config.login_field, query_config.password_field
        login, password = query[login_field], query[password_field]
        return self.auth_controller.auth_user(login, password, auth_type)

    def process_query(self, query):
        if len(query) == 0:
            return self.encode_query(QueryHelper.get_error_response())
        query_function = list(query.keys())[0]
        if query_function not in self.config_map:
            return QueryHelper.get_not_implemented_response()
        query = query[query_function]
        query_config = self.config_map[query_function]
        auth = self.process_auth(query, query_config)
        query_response = query_config.query_function(query, auth)
        return query_config.get_processed_query_response(query_response)

    def handle_query(self, query):
        try:
            query = self.decode_query(query)
            query_response = self.encode_query(self.process_query(query))
            self.db_connection.commit_transaction()
            return query_response
        except Exception as exc:
            self.db_connection.rollback_transaction()
            return self.encode_query(QueryHelper.get_error_response())
