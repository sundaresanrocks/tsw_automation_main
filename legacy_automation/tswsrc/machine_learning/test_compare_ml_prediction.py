import os
import requests
import configparser
import wsr_mongo_lib
from datetime import datetime, timedelta
import unittest


class TestMLServer(unittest.TestCase):

    def setUp(self):
        properties = self.load_properties('ML.properties')

        self.prod_ml_server_url = properties.get('QA', 'prod_ml_server_url')
        self.qa_ml_server_url = properties.get('QA', 'qa_ml_server_url')
        self.urldb_host = properties.get('QA', 'urldb_host')
        self.urldb_port = properties.get('QA', 'urldb_port')
        self.urldb_username = properties.get('QA', 'urldb_username')
        self.urldb_password = properties.get('QA', 'urldb_password')
        self.workflow_name = properties.get('QA', 'workflow_name')
        self.urldb_result_file = properties.get('QA', 'urldb_result_file')
        self.urldb_queury_limit = int(properties.get('QA', 'urldb_queury_limit'))

        self.extract_urldb()

    def test_compare_ml_predictions(self):

        with open(self.urldb_result_file) as f:
            for line in f:
                result_str = '{\"models\":\"all\", \"data\":' + line.replace('\n', '') + '}'
                try:
                    prod_ml_prediction = requests.post(self.prod_ml_server_url, result_str).text
                    qa_ml_prediction = requests.post(self.qa_ml_server_url, result_str).text
                    self.assertEqual(prod_ml_prediction, qa_ml_prediction)
                except Exception as e:
                    self.fail('Failed to connect to ml server. ' + str(e))

    def extract_urldb(self):
        try:
            mongo_handle = wsr_mongo_lib.initialize_mongo_client(self.urldb_username, self.urldb_password, self.urldb_host, self.urldb_port)
            start_date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
            end_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
            df_temp = wsr_mongo_lib.extract_records_to_df(mongo_handle, start_date, end_date, self.workflow_name, self.urldb_queury_limit)
        except Exception as e:
            self.fail('Unable to connect to URLDB. ' + str(e))
        df_temp.to_json(self.urldb_result_file, orient='records', lines=True, default_handler=str)

    def load_properties(self, file_path):
        config = configparser.RawConfigParser()
        config.read(file_path)
        return config

    def tearDown(self):
        # Cleaning up URLDB file
        os.remove(self.urldb_result_file)


if __name__ == '__main__':
    unittest.main()
