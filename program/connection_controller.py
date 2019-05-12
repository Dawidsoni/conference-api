import psycopg2 as pg
from query_helper import QueryHelper
from db_connection import DbConnection


class ConnectionController(object):
    def __init__(self, db_connection):
        self.db_connection = db_connection

    @staticmethod
    def is_db_inited():
        try:
            test_connection = DbConnection()
            test_connection.init_connection()
            return True
        except Exception as exc:
            return False

    @staticmethod
    def create_database(db_name, login, password):
        connection = pg.connect(database=db_name, user=login, password=password)
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute("DROP DATABASE IF EXISTS db_conference;")
        cursor.execute("DROP USER IF EXISTS application_user;")
        cursor.execute("CREATE DATABASE db_conference;")
        cursor.execute("CREATE USER application_user WITH password 'top_secret';")
        connection.close()

    def init_database(self):
        self.db_connection.init_connection()
        with open("model_script.sql", "r") as script_file:
            init_query = script_file.read()
            self.db_connection.execute_update(init_query)
            self.db_connection.commit_transaction()

    def init_connection(self, query, auth):
        if self.is_db_inited():
            self.db_connection.init_connection()
            return QueryHelper.get_ok_response()
        db_name, login, password = query["baza"], query["login"], query["password"]
        self.create_database(db_name, login, password)
        self.init_database()
        return QueryHelper.get_ok_response()
