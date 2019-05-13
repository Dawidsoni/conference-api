import unittest
from query_config import QueryConfig
import unittest.mock as mock


class QueryConfigTest(unittest.TestCase):

    def test_get_processed_query_response(self):
        query_config = QueryConfig(mock.Mock(), {"response": "c1, c2"})
        response_data = [["val1", "val2"], ["val3", "val4"]]
        processed_response = query_config.get_processed_query_response({"status": "OK", "data": response_data})
        self.assertEqual([{"c1": "val1", "c2": "val2"}, {"c1": "val3", "c2": "val4"}], processed_response["data"])

    @unittest.expectedFailure
    def test_get_invalid_query_response(self):
        query_config = QueryConfig(mock.Mock(), {"response": "col1, col2"})
        response_data = [["val1", "val2", "val3"], ["val4", "val5", "val6"]]
        query_config.get_processed_query_response({"status": "OK", "data": response_data})


if __name__ == '__main__':
    unittest.main()
