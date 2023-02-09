"""
======================================================
Script to update CI test run result to QA dashboard DB
======================================================
"""

import subprocess
import logging
import pymysql
from pymysql import Error
from scripts.external_reporting.ci_log_reader import CILogParser


HOST = 'vm-nikitha.wsrlab'
PORT = 3306
USER = 'qa-auto'
PASS = 'xdr5tgb'
DB = 'qadashboarddb'


def get_wsr_rpm_version():
    version_number = None
    try:
        child = subprocess.Popen("rpm -qa | grep -i wsr-core", stdout=subprocess.PIPE, shell=True)
        output = child.communicate()[0]
    except Error as error:
        logging.error('Error while attempting to read rpm version number')
        raise error
    output_string = output.decode()
    if not output_string is None:
        version_number = output_string.strip('\n')[-5:]
    return version_number


def update_qa_dash_db():
    version_number = get_wsr_rpm_version()
    ci_log_reader = CILogParser()
    testrun_stats_dict = ci_log_reader.read_testrun_stats_from_log()
    testrun_data = {
        'rpm_version': version_number,
        'build_id': testrun_stats_dict['build_id'],
        'total_tests_count': len(testrun_stats_dict['passed']) + len(testrun_stats_dict['failed']) +
                             len(testrun_stats_dict['blocked']),
        'passed_tests_count': len(testrun_stats_dict['passed']),
        'blocked_tests_count': len(testrun_stats_dict['blocked']),
        'failed_tests_count': len(testrun_stats_dict['failed'])
    }
    sql = "insert into ciresults (codebuild, buildid, totaltc, passtc, failtc, blockedtc) values('%(rpm_version)s', '%(build_id)s', %(total_tests_count)s, %(passed_tests_count)s, " \
          "%(failed_tests_count)s, %(blocked_tests_count)s)" % testrun_data
    try:
        conn = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASS, db=DB)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    except Error as error:
        logging.error('Error while attempting write to database')
        raise error
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    update_qa_dash_db()
