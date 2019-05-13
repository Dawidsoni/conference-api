import unittest
from json_encoder import JsonEncoder
from datetime import date


class JsonEncoderTest(unittest.TestCase):
    def test_date_encoding(self):
        encoded_json = JsonEncoder().encode({'startTime': date.min})
        self.assertEqual('{"startTime": "0001-01-01"}', encoded_json)


if __name__ == '__main__':
    unittest.main()
