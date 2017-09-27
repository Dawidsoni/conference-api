import psycopg2 as pg


class DbConnection(object):
    DB_NAME = "db_conference"
    DB_USER = "application_user"
    DB_PASSWORD = "top_secret"

    def __init__(self):
        self.connection = None
        self.cursor = None

    def init_connection(self):
        db_name, login, password = DbConnection.DB_NAME, DbConnection.DB_USER, DbConnection.DB_PASSWORD
        self.connection = pg.connect(database=db_name, user=login, password=password)
        self.cursor = self.connection.cursor()

    def execute_query(self, query_string):
        self.cursor.execute(query_string)
        return self.cursor.fetchall()

    def execute_update(self, query_string):
        self.cursor.execute(query_string)

    def commit_transaction(self):
        if self.connection is not None:
            self.connection.commit()

    def rollback_transaction(self):
        if self.connection is not None:
            self.connection.rollback()

