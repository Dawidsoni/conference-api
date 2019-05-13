import unittest
from unittest import mock
from db_connection import DbConnection
from query_config import QueryConfig
from query_handler import QueryHandler


class QueryHandlerTest(unittest.TestCase):

    def setUp(self):
        self.query_function_mock = mock.Mock()
        self.query_function_mock.return_value = {"status": "OK"}
        self.get_config_mock = mock.patch.object(QueryHandler, 'get_config').start()
        self.get_config_mock.return_value = {"open": QueryConfig(self.query_function_mock, {})}

    def tearDown(self):
        self.get_config_mock.stop()

    @mock.patch.object(DbConnection, 'commit_transaction')
    def test_commit_transaction(self, commit_transaction_mock):
        query_handler = QueryHandler()
        response = query_handler.handle_query('{"open": {"baza": "dwegner_db", "login": "dwegner", "password": "xyz"}}')
        self.assertEqual('{"status": "OK"}', response)
        commit_transaction_mock.assert_called_once()

    @mock.patch.object(DbConnection, 'rollback_transaction')
    def test_rollback_transaction(self, rollback_transaction_mock):
        query_handler = QueryHandler()
        query_handler.handle_query("")
        rollback_transaction_mock.assert_called_once()


if __name__ == '__main__':
    unittest.main()
