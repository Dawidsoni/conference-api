import unittest
from unittest import mock
from connection_controller import ConnectionController


class QueryHandlerTest(unittest.TestCase):

    @mock.patch('db_connection.DbConnection')
    @mock.patch.object(ConnectionController, 'is_db_inited')
    def test_init_connection(self, is_db_inited_mock, db_connection_mock):
        is_db_inited_mock.return_value = True
        connection_controller = ConnectionController(db_connection_mock)
        connection_controller.init_connection({"baza": "xyz", "login": "dwegner", "password": "pass"}, None)
        db_connection_mock.init_connection.assert_called_once()

    @mock.patch.object(ConnectionController, 'is_db_inited')
    @mock.patch('db_connection.DbConnection')
    @mock.patch('psycopg2.connect')
    @mock.patch('connection_controller.open')
    def test_init_database(self, open_mock, pg_connect_mock, db_connection_mock, is_db_inited_mock):
        is_db_inited_mock.return_value = False
        connection_controller = ConnectionController(db_connection_mock)
        connection_controller.init_connection({"baza": "xyz", "login": "dwegner", "password": "pass"}, None)
        pg_connect_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()
