import sqlite3


class DbConnection(object):
    DB_NAME = "db_conference.db"

    def __init__(self):
        self.connection = None
        self.cursor = None

    def get_db_name(self):
        return self.DB_NAME

    def get_last_row_id(self):
        return self.cursor.lastrowid

    def init_connection(self):
        self.connection = sqlite3.connect(self.get_db_name())
        self.cursor = self.connection.cursor()

    def execute_query(self, query_string):
        self.cursor.execute(query_string)
        return self.cursor.fetchall()

    def execute_update(self, query_string):
        self.cursor.execute(query_string)

    def execute_script(self, query_string):
        self.cursor.executescript(query_string)

    def commit_transaction(self):
        if self.connection is not None:
            self.connection.commit()

    def rollback_transaction(self):
        if self.connection is not None:
            self.connection.rollback()

