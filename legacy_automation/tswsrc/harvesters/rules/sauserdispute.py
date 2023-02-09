# -*- coding: utf-8 -*-
from harvesters.harvester_config import SAUserDisputesConfig

__author__ = 'Anurag'
import urllib.request
import urllib.error
import urllib.parse
import io
from random import choice
from datetime import date

from lib.exceptions import TestFailure
from harvesters.harvester import *
from lib.db.mssql import TsMsSqlWrap










#Sanity tests
#----------------------
#1. Is webservice available
#2. Is preprocessor available
#3. Is preprocessor poiting to correct websource
#4. Check for correct version of jar files in harvester_manager.sh


class SAUserDisputesSanity(SandboxedTest):

    @classmethod
    def setUpClass(cls):
        cls.hcon = SAUserDisputesConfig()
        cls.host = 'localhost'
        cls.user = 'toolguy'
        cls.host_location = 'http://tsqasvc01.wsrlab/sa/default.csv'
        cls.ssh_obj = runtime.get_ssh(cls.host,cls.user)
        cls.preprocessor = '/opt/sftools/bin/get_sa_user_disputes.sh'

    def test_01(self):
        """Checks if hosted location is available"""
        status = urllib.request.urlopen(self.host_location)
        if status.code != 200:
            raise TestFailure('HTTP return code is %s' %status.code)

    def test_02(self):
       """Validate preprocessor is present"""
       if not self.ssh_obj._file_exists(self.preprocessor):raise TestFailure('Preprocessor file ' + self.preprocessor +' is not present')

    def test_03(self):
        """Check if preprocessor points to exact web service"""
        local_file_name = self.preprocessor.split('/')[-1]
        self.ssh_obj.get(self.preprocessor,local_file_name)
        fp = open(local_file_name)
        for line in fp.readlines():
            line = line.strip()
            if line.startswith('url'):
                line = line.strip().split('=')
                logging.info('Hosted at ' + line[1])
                if not self.host_location in line[1]:
                    logging.info('Hosted at ' + line[1])
                    logging.info('Preprocessor does not point to ' + self.host_location)

    def test_04(self):
        """saved to location feed"""
        run_preprocessor = 'sh ' + self.preprocessor
        local_file_name = self.preprocessor.split('/')[-1]
        self.ssh_obj.get(self.preprocessor,local_file_name)
        fp = open(local_file_name)
        for line in fp.readlines():
            line = line.strip()
            if line.startswith('op_dir'):
                op_dir = line.strip().split('=')[1]
                logging.info('Output directory is ' + op_dir)
        delete_op_dir = 'rm ' + op_dir + '/*'
        chk_op_dir = 'ls ' + op_dir
        self.ssh_obj.execute(delete_op_dir)
        self.ssh_obj.execute(run_preprocessor)
        stdout,stderr = self.ssh_obj.execute(chk_op_dir)
        if stderr != '':
            raise TestFailure(stderr)
        buff = io.StringIO(stdout)
        year  = str(date.today().year)
        month = date.today().month
        day = date.today().day
        if month < 10:
            month = '0' + str(month)
        month = str(month)
        day -= 1
        if day < 10:
            day = '0' + str(day)
        day = str(day)
        file_name = 'sauser' + year + month + day + '.csv'
        for line in buff.readlines():
            line = line.strip()
            if line == '':
                raise TestFailure('No file fetched')
            if line != file_name:
                raise TestFailure('File name does not match ' + file_name)

    def test_05(self):
        """Check in database for presence of SAUserDispute Queue"""
        sql_obj = TsMsSqlWrap('U2')
        query = "select * from queue_types where queue_name = '" + SAUserDisputesConfig.harvester_name + "'"
        result = sql_obj.get_select_data(query)
        logging.info(result)
        if len(result) == 0:
            raise TestFailure(SAUserDisputesConfig.harvester_name + ' is not present in Queue_types table')
        if len(result) > 1:
            raise TestFailure(SAUserDisputesConfig.harvester_name + ' is present ' + str(len(result)) + ' times in queue_types table')

class SAUserDisputesFunc(SandboxedHarvesterTest):
    default_har_config = SAUserDisputesConfig
    preprocessor = runtime.data_path + '/tsw/harvesters/sauserdisputes/get_qa.sh'
    queue_id = 358

    def test_01(self):
        """Non resume mode"""
        hcon = SAUserDisputesConfig()
        hcon.rules_matched['(Salience=000000) Queue user dispute URL'] = '2'
        hcon.action_taken['Urls Queued'] = '2'
        hobj = Harvester(hcon,"partial")
        hobj.run_preprocessor(self.preprocessor)
        hobj.test_harvester_base(source_file=None,resume_mode = False,copy_to_source=False)

    def test_02(self):
        """Resume mode"""
        hcon = SAUserDisputesConfig()
        hcon.rules_matched['(Salience=000000) Queue user dispute URL'] = '2'
        hcon.action_taken['Urls Queued'] = '2'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('sauserdisputes/02.csv', hcon.action_taken, hcon.rules_matched)

    def test_03(self):
        """Check if queue got updated for non locked security queue"""
        url = '*://ask.com'
        q_id = 332 #FAKEAV
        sql_obj = TsMsSqlWrap('U2')
#Updating queue for url
        query = "select url_id from urls where url like '" + url + "'"
        url_id_list = sql_obj.get_select_data(query)
        url_id = str(url_id_list[0]['url_id'])
        update_query = "update queue set queue = " + str(q_id) + " where url_id = " + str(url_id)
        sql_obj.execute_sql_commit(update_query)
#Run harvester
        hcon = SAUserDisputesConfig()
        hcon.rules_matched['(Salience=000000) Queue user dispute URL'] = '2'
        hcon.action_taken['Urls Queued'] = '2'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('sauserdisputes/02.csv', hcon.action_taken, hcon.rules_matched)
#Check for change of queue
        query = "select queue from queue where url_id=" + str(url_id)
        result = sql_obj.get_select_data(query)
        if result[0]['queue'] != self.queue_id:
            logging.info('Security QUEUE is not changed . It is %s' % result[0]['queue'])
        logging.info(str(result[0]['queue']) + ' is the queue for ' + url)

    def test_04(self):
        """Check that queue should not get updated for locked queue"""
        sql_obj = TsMsSqlWrap('U2')
        locked_queues_list = []
        query = 'select queue_id from queue_types where is_locked = 1'
        locked_queues = sql_obj.get_select_data(query)
        for i in locked_queues:
            locked_queues_list.append(i['queue_id'])
        logging.warning(locked_queues_list)
        q_id = choice(locked_queues_list)
        logging.info(str(q_id) + ' locked queue is selected')
        url = "*://ask.com"
#Updating queue for url
        query = "select url_id from urls where url like '" + url + "'"
        url_id_list = sql_obj.get_select_data(query)
        url_id = str(url_id_list[0]['url_id'])
        update_query = "update queue set queue = " + str(q_id) + " where url_id = " + str(url_id)
        sql_obj.execute_sql_commit(update_query)
#Run harvester
        hcon = SAUserDisputesConfig()
        hcon.rules_matched['(Salience=000000) Queue user dispute URL'] = '2'
        hcon.action_taken['Urls Queued'] = '2'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('sauserdisputes/02.csv', hcon.action_taken, hcon.rules_matched)
#Check for change of queue. It should not change
        query = "select queue from queue where url_id=" + str(url_id)
        result = sql_obj.get_select_data(query)
        if result[0]['queue'] == self.queue_id or result[0]['queue'] != q_id:
            logging.info('LOCKED QUEUE has changed . It is ' + result[0]['queue'])
        logging.info(str(result[0]['queue']) + ' is the queue for ' + url)

    def test_05(self):
        """Check that a new url gets queued"""
        preprocessor = runtime.data_path + '/tsw/harvesters/sauserdisputes/get1.sh'
        hcon = SAUserDisputesConfig()
        hcon.rules_matched['(Salience=000000) Queue user dispute URL'] = '1'
        hcon.action_taken['Urls Queued'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.run_preprocessor(preprocessor)
        hobj.test_harvester_base(source_file=None,resume_mode = False,copy_to_source=False)


    def test_06(self):
        """Check user suggested cats in url_meta_data"""
        url = '*://example.com'
        cat = 'Sports'
        preprocessor = runtime.data_path + '/tsw/harvesters/sauserdisputes/get3.sh'
        hcon = SAUserDisputesConfig()
        hcon.rules_matched['(Salience=000000) Queue user dispute URL'] = '1'
        hcon.action_taken['Urls Queued'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.run_preprocessor(preprocessor)
        hobj.test_harvester_base(source_file=None,resume_mode = False,copy_to_source=False)
        query_id = "select url_id from urls where url like '" + url + "'"
        sql_obj = TsMsSqlWrap('U2')
        url_id = sql_obj.get_select_data(query_id)
        url_id = (url_id[0])['url_id']
        logging.warning(url_id)
        query_umd = "select attribute_value from url_meta_data where url_id = %s and attribute_name = %s"%(url_id,"'category'")
        logging.warning(query_umd)
        attribute_value = sql_obj.get_select_data(query_umd)
        attribute_value = ((attribute_value[0])['attribute_value']).strip()
        if attribute_value != cat:
            raise TestFailure('Category found is %s instead of %s'%(attribute_value,cat))

    def test_07(self):
        """Urls with special characters in it"""
        preprocessor = runtime.data_path + '/tsw/harvesters/sauserdisputes/get4.sh'
        hcon = SAUserDisputesConfig()
        hcon.rules_matched['(Salience=000000) Queue user dispute URL'] = '1'
        hcon.action_taken['Urls Queued'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.run_preprocessor(preprocessor)
        hobj.test_harvester_base(source_file=None,resume_mode = False,copy_to_source=False)


    def test_08(self):
        """IDN urls and characters in comments"""
        preprocessor = runtime.data_path + '/tsw/harvesters/sauserdisputes/get2.sh'
        hcon = SAUserDisputesConfig()
        hcon.rules_matched['(Salience=000000) Queue user dispute URL'] = '1'
        hcon.action_taken['Urls Queued'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.run_preprocessor(preprocessor)
        hobj.test_harvester_base(source_file=None,resume_mode = False,copy_to_source=False)

    def test_09(self):
        """Check for comments in url_info table"""
        url = "*://arabictestbyanurag.com"
        comment = "صلاة (صلاة (صلاة (صلاة (صلاة (صلاة (صلاة (صلاة (صلاة"
        preprocessor = runtime.data_path + '/tsw/harvesters/sauserdisputes/get5.sh'
        hcon = SAUserDisputesConfig()
        hcon.rules_matched['(Salience=000000) Queue user dispute URL'] = '1'
        hcon.action_taken['Urls Queued'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.run_preprocessor(preprocessor)
        hobj.test_harvester_base(source_file=None,resume_mode = False,copy_to_source=False)
        query_id = "select url_id from urls where url like '" + url + "'"
        sql_obj = TsMsSqlWrap('U2')
        url_id = sql_obj.get_select_data(query_id)
        url_id = (url_id[0])['url_id']
        query_info = "select memo from url_info where url_id = %s"%url_id
        memo = sql_obj.get_select_data(query_info)
        memo = (memo[0])['memo']
        if comment not in memo:
            raise TestFailure('%s present in memo instead of %s'%(memo,comment))





