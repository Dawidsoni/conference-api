import os
from query_helper import QueryHelper


class ConnectionController(object):
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def init_connection(self, _query, _auth):
        self.db_connection.init_connection()
        if os.stat(self.db_connection.get_db_name()).st_size != 0:
            return QueryHelper.get_ok_response()
        with open("model_script.sql", "r") as script_file:
            init_query = script_file.read()
            self.db_connection.execute_script(init_query)
        return QueryHelper.get_ok_response()
