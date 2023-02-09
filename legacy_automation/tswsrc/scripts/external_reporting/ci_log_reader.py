"""
========================================
Utility to parse through CI test run log
========================================
"""

import logging
import configparser
from path import Path
from runtime import src_path


__author__ = 'abhijeet'


class CILogParser:

    def __init__(self):
        self.ci_log_file = Path(self.__get_ci_file_path(src_path.joinpath('testlink.ini')))

    @staticmethod
    def __get_ci_file_path(tlink_file):
        if not tlink_file.exists():
            logging.error('Testlink file %s does not exist' % tlink_file)
            raise FileNotFoundError
        ini_reader = configparser.ConfigParser()
        ini_reader.read(tlink_file)
        if not 'testlink-conf' in ini_reader.sections():
            logging.error('testlink-conf section not found in %s' % tlink_file)
            raise
        if not 'tlink_log' in ini_reader['testlink-conf'].keys():
            logging.error('tlink_log property not found in testlink properties file %s' % tlink_file)
            raise
        return ini_reader['testlink-conf']['tlink_log']

    def read_testrun_stats_from_log(self):
        ci_log_file = self.ci_log_file
        if not ci_log_file.exists():
            logging.error('ci log file path %s does not exist' % ci_log_file)
            raise FileNotFoundError
        if not ci_log_file.isfile():
            logging.error('ci log file path %s exists but is not a file' % ci_log_file)
            raise FileNotFoundError
        failed_list = []
        passed_list = []
        blocked_list = []
        valid_status_dict = {'f': failed_list, 'p': passed_list, 'b': blocked_list}
        with open(ci_log_file, 'r') as logf:
            _, _, build_id_str = logf.readline().split(',')
            for line in logf.readlines():
                status, test_id, node_id = line.split(',')
                if not status in valid_status_dict.keys():
                    logging.warning(
                        'Status %s for test: %s:%s not an expected test result' * (status, test_id, node_id))
                    continue
                test_tuple = (test_id, node_id)
                valid_status_dict[status].append(test_tuple)
        stats_dict = {
            'build_id': build_id_str,
            'failed': failed_list,
            'passed': passed_list,
            'blocked': blocked_list
        }
        return stats_dict
