"""
=======================================
Script to parse through CI test run log
=======================================
"""
import logging
import configparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from path import Path
from runtime import src_path


__author__ = 'abhijeet'


SMTP_SERVER = 'localhost'
SMTP_PORT = 8432
FROM_ADDRESS = 'abhijeet.negi@intel.com'
TO_ADDRESS = 'abhijeet.negi@intel.com'
CC_ADDRESS = ['abhijeet.negi@intel.com']
HTML = """\
<html>
    <head></head>
    <body>
        <p>
            Testrun ID = %(build_id)s</br>
            Total test count = %(total_tests_count)s</br>
            Passed = %(passed_tests_count)s</br>
            Failed = %(failed_tests_count)s</br>
            Blocked = %(blocked_tests_count)s</br>
        </p>
    </body>
</html>
"""


class EmailReport:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.from_address = FROM_ADDRESS
        self.to_address = TO_ADDRESS
        self.cc_address = CC_ADDRESS
        self.ci_log_file = Path(self.__get_ci_file_path(src_path.joinpath('testlink.ini')))
        self.testrun_stats_dict = self.__read_testrun_stats_from_log(self.ci_log_file)
        self.subject = 'Testrun report'

    def email_report(self):
        msg = MIMEMultipart()
        msg['From'] = self.from_address
        msg['To'] = self.to_address
        msg['Subject'] = self.subject
        msg['Cc'] = ', '.join(self.cc_address)
        recipients = [self.to_address] + self.cc_address
        testrun_data = {
            'build_id': self.testrun_stats_dict['build_id'],
            'total_tests_count': len(self.testrun_stats_dict['passed']) + len(self.testrun_stats_dict['failed']) +
                           len(self.testrun_stats_dict['blocked']),
            'passed_tests_count': len(self.testrun_stats_dict['passed']),
            'blocked_tests_count': len(self.testrun_stats_dict['blocked']),
            'failed_tests_count': len(self.testrun_stats_dict['failed'])
        }
        html = HTML % testrun_data
        html_msg = MIMEText(html, 'html')
        msg.attach(html_msg)
        failed_tests = '\n'.join(x[1].strip().strip('\n') for x in self.testrun_stats_dict['failed'])
        failed_tests_msg = MIMEText(failed_tests, 'plain')
        msg.attach(failed_tests_msg)
        try:
            server = smtplib.SMTP(self.smtp_server, port=self.smtp_port)
            server.set_debuglevel(1)
            server.sendmail(self.from_address, recipients, '%s' % msg)
            server.quit()
        except:
            logging.error('Unable to send mail.')
            raise
        logging.info('Email sent.')

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

    @staticmethod
    def __read_testrun_stats_from_log(ci_log_file):
        if not ci_log_file.exists():
            logging.error('ci log file path %s does not exist' % ci_log_file)
            raise
        if not ci_log_file.isfile():
            logging.error('ci log file path %s exists but is not a file' % ci_log_file)
            raise
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


if __name__ == '__main__':
    er = EmailReport()
    er.email_report()
