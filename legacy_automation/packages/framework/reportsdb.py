"""
Results mySql DB Config
***********************
"""
__author__ = 'manoj'


UPDATE_RESULTS_DB = True
# UPDATE_RESULTS_DB = False
#False will not update db(testing/dev work)
#:check: must be True for reports in db
import os
#import io
import zlib
import logging
import platform
import socket
import binascii
import pymysql
import urllib.request
import urllib.error
import urllib.parse
import urllib.parse

from datetime import datetime as dt


HOST_NAME = platform.node()
IP_ADDRESS = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close())
              for s in [socket.socket(type=socket.SOCK_DGRAM)]][0][1]


class ResultsInMySqlDB:
    """mySql db settings"""
    host = '172.22.81.112'
    user = 'automation'
    password = 'auto1234'
    db = 'ts_automation'
    # table = 'debug_report'
    table = 'tsa_report'


def get_results_sql_wrap_obj():
    """
    Establishes connection with results database with mysql wrapper
    :returns: mySqlHelper object
    """
    from libx.sqlwrap import mySqlHelper

    return mySqlHelper(host=ResultsInMySqlDB.host,
                       user=ResultsInMySqlDB.user,
                       passwd=ResultsInMySqlDB.password,
                       db=ResultsInMySqlDB.db)


def create_run_error_entry_with_id(title='', desc='', jenkins_id='', start_time=''):

    if not UPDATE_RESULTS_DB:
        print('UPDATE_RESULTS_DB is False')
        return
    if not jenkins_id:
        jenkins_id = 0
    sql_obj = get_results_sql_wrap_obj()
    if not start_time:
        start_time = dt.now()
    _dict = {'jenkins_id': int(jenkins_id),
             'start_time': str(start_time).strip(),
             'host_name': HOST_NAME,
             'test_title': str(title).strip(),
             'test_desc': str(desc).strip(),
             'ip_address': str(IP_ADDRESS).strip()}

    sql_obj.query('insert into %s ' % ResultsInMySqlDB.table + sql_obj.make_insert(_dict))
    return sql_obj.db.insert_id()


def get_run_id(title, desc, jenkins_id, start_time):

    if not UPDATE_RESULTS_DB:
        raise Exception('UPDATE_RESULTS_DB is False')
    sql_obj = get_results_sql_wrap_obj()
    _dict = {'jenkins_id': int(jenkins_id),
             'start_time': str(start_time).strip(),
             'host_name': HOST_NAME,
             'test_title': str(title).strip(),
             'test_desc': str(desc).strip(),
             'ip_address': str(IP_ADDRESS).strip()}
    sql_obj.query('insert into %s ' % ResultsInMySqlDB.table + sql_obj.make_insert(_dict))
    return sql_obj.db.insert_id()


def get_build_changelog(url):
    """#. get build changelog for given build_url
    #. extract using beautiful soup
    #. get images, convert to base 64
    """

    #logging.info('Extracting svn changelist from: %s', url)
    if str(url).startswith('http:/') and not (str(url).startswith('http://')):
        url = url.replace('http:/', 'http://')
    urlsplit = urllib.parse.urlsplit(url)
    netloc = urlsplit.scheme + '://' + urlsplit.netloc

    html = urllib.request.urlopen(url).read()
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html).find(lambda tag: tag.name == 'td' and 'id' in tag and tag['id'] == "main-panel")

    #remove td
    contents = BeautifulSoup(''.join(str(c_str) for c_str in soup.contents))
    for div in contents('div'):
        div.extract()
    for anchor in contents('a', {'name': 'skip2content'}):
        anchor.extract()

    for anchor in contents.findAll('a'):
        anchor['href'] = url + anchor['href']
    for img in contents.findAll('img'):
        i_url = netloc + img['src']
        i_str = urllib.request.urlopen(i_url).read().encode('base64').replace('\n', '')
        img['src'] = 'data:image/png;base64,{0}'.format(i_str)

    #logging.warning('Contents: %s', str(contents))

    return '''<table style="font-family: Verdana, Helvetica, 'sans serif';">
<tr>
%s
</tr>
''' % str(contents)


def put_svn_changlog_in_db(test_info):
    """#. exit if the smallest run_id for jenkins id is not null
    #. get build changelog and compress
    #. for all jenkins id in db, save the report to smallest value
    """
    try:
        jid = test_info.jenkins_id
        j_url = test_info.jenkins_url
        if not UPDATE_RESULTS_DB:
            raise Exception('UPDATE_RESULTS_DB is set to False.')
        if jid <= 0:
            raise Exception('Jenkins id <= 0. Cannot update results.')

        sql_obj = get_results_sql_wrap_obj()
        query = 'select min(run_id),svn_changelog from ' + ResultsInMySqlDB.table + ' where jenkins_id=%s' % str(jid)
        result = sql_obj.query(query)
        run_id = result[1][0][0]
        if run_id is None:
            raise Exception('min(run_id) not found for jenkins id.')
        svn_blob = result[1][1][0]
        if svn_blob != '':
            raise Exception('svn changelog found in db. Cannot rewrite.')

        html_data = '''Job info found at: %s''' % j_url
        if j_url:
            try:
                html_data = get_build_changelog(j_url)
            except:
                logging.warning('Improper BUILD_URL: %s', j_url)
        _dict = {'svn_changelog': zlib.compress(html_data, 9)}
        query = 'update ' + ResultsInMySqlDB.table + ' ' + sql_obj.make_insert(_dict) \
                + ' where run_id=' + str(run_id)
        sql_obj.query(query)
    except Exception as err:
        logging.warning('Unable to update svn changelog in database: %s' % err.args[0])


def put_results_in_db(test_info):
    if not UPDATE_RESULTS_DB:
        logging.warning('Unable to update results count in database: UPDATE_RESULTS_DB is set to False.')
        return
    try:
        if not(os.path.isfile(test_info.report_file)):
            raise Exception('File not found for db upload: %s' % test_info.report_file)
        sqlobj = get_results_sql_wrap_obj()
        with open(test_info.report_file, 'rb') as fpr:
            html_data = fpr.read()

            _dict = {'test_title': test_info.title,
                     'test_desc': test_info.desc,
                     'end_time': str(dt.now())}

        query = 'update %s ' % ResultsInMySqlDB.table + sqlobj.make_insert(_dict) + \
                ' where run_id=%s' % test_info.run_id
        sqlobj.query(query)
            #### update the html report
        zreport = binascii.hexlify(zlib.compress(html_data, 9))
        query = "update %s " % ResultsInMySqlDB.table + " set zreport=0x%s" % zreport.decode() + \
                " where run_id=%s" % test_info.run_id
        sqlobj.query(pymysql.escape_string(query))
    except Exception as err:
        logging.warning('Unable to update results file in database: %s' % err)


def update_result_counts(run_id, _test_count, _test_pass, _test_fail, _test_error, _test_skip):
    if not UPDATE_RESULTS_DB:
        logging.warning('Unable to update results count in database: UPDATE_RESULTS_DB is set to False.')
        return
    try:
        from libx.sqlwrap import mySqlHelper
        sql_obj = get_results_sql_wrap_obj()
        query = 'select count_tests, count_pass, count_fail, count_error, ' \
                + 'count_skip from %s where run_id=%s' % (ResultsInMySqlDB.table, run_id)
        temp_data = sql_obj.query(query)

        _dict = {'count_tests': _test_count + int(temp_data[1][0][0]),
                 'count_pass': _test_pass + int(temp_data[1][1][0]),
                 'count_fail': _test_fail + int(temp_data[1][2][0]),
                 'count_error': _test_error + int(temp_data[1][3][0]),
                 'count_skip': _test_skip + int(temp_data[1][4][0])}
        query = 'update %s ' % ResultsInMySqlDB.table + sql_obj.make_insert(_dict) + \
                ' where run_id=%s' % run_id
        sql_obj.query(query)
    except Exception as err:
        logging.warning('Unable to update results count in database: %s' % err)


