__author__ = 'Anurag'
import logging
import time

from lib.properties.sshprop import SSHProperties
from framework.test import SandboxedTest
from lib.sfimport import sfimport
from ar.lib.arutils import insert_and_autorate, enable_scorers_from_prod
from lib.db.mssql import TsMsSqlWrap
from lib.utils.serverstatus import is_app_server_up
import runtime
from lib.exceptions import TestFailure
from libx.vm import get_snapshot_wrapper
from libx.process import OSProcessHandler
from lib.db.u2_scorers import ScorerMap,U2Scorers
from lib.db.mdbautorating import MongoWrapAR
from ar.lib.resultfactparser import ResultFactParser


class AutoratingFlow(SandboxedTest):


    @classmethod
    def setUpClass(self):
        self.username = 'toolguy'
        self.CONF_HOME = '/opt/sftools/conf/'
        self.ssh_obj = runtime.get_ssh(runtime.SCORER.host, user=self.username)
        self.webcache = '/tmp/webcache/'
        DB_vm_warp = get_snapshot_wrapper(runtime.DB.U2_host)
        self.start_scorer_cmd = 'nohup %s %s %s > /dev/null 2>&1 &' %\
        (runtime.SCORER.bin_acs, runtime.SCORER.prop_scorer, runtime.SCORER.prop_fetcher)
        self.start_queue_populator = 'nohup %s %s > /dev/null 2>&1 &' % (runtime.SCORER.bin_aqp, runtime.SCORER.prop_worktask)
        self.score_url = '%s %s ' % (runtime.SCORER.bin_qa_ausubmit, runtime.AppServer.host)
        self.url_scheduler = 'nohup %s %s > /dev/null 2>&1 &' %\
        (runtime.SCORER.bin_aus, runtime.SCORER.prop_url_schduler,)
        local_ssh = runtime.get_ssh('localhost',user='root')
        local_ssh.put(localpath=runtime.data_path+'/tsw/ar/odbc.ini',remotepath='/etc/odbc.ini')
        local_ssh.put(localpath=runtime.data_path+'/tsw/ar/freetds.conf',remotepath='/etc/freetds/freetds.conf')


    def test_06(self):
        """WorkTask Validations for a single URL"""
        urls = ['*://example.com']
        cat = 'bl'
        obj=sfimport()
        sfimportResult = obj.append_category(urls,cat)
        url_dict = obj.url_dict()
        logging.info("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.info("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.info("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.info("Total Number of URLS  : %s"%(len(urls)))
        if not (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure('Errors found in Sfimport log')
        logging.warning(url_dict)
        url_id = int(list(url_dict.keys())[0])
        #insert it into worktask
        #schedule a url for autorating by inserting into work task.
        mssql_obj = TsMsSqlWrap('U2')
        del_query = 'delete from u2.dbo.worktask'
        mssql_obj.execute_sql_commit(del_query)
        status = insert_and_autorate(url_id,self.ssh_obj)
        if status != 'completed':
            raise TestFailure('Autorating on %s is not complete. It is %s ' % (url_id, status))
        #kill ChainedScorer and QueuePopulator
        process_obj = OSProcessHandler('java',full_format=True,ssh_con=self.ssh_obj)
        if process_obj.is_running():
            process_obj.kill_processes()

    def test_07(self):
        """Validate Scorers.log for a Single URL autorated"""
        #enable parked domain , Residential scorers
        enabled_scorers = [4,12]
        err_list = []
        clear_log = 'rm %s ; touch %s' % (runtime.SCORER.scorer_log,runtime.SCORER.scorer_log)
        self.ssh_obj.execute(clear_log)
        u2_scorer_obj = U2Scorers()
        for i in enabled_scorers:
            u2_scorer_obj.enable_id(i)
        urls = ['*://tests.com']
        cat = 'bl'
        obj=sfimport()
        sfimportResult = obj.append_category(urls,cat)
        url_dict = obj.url_dict()
        logging.info("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.info("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.info("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.info("Total Number of URLS  : %s"%(len(urls)))
        if not (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure('Errors found in Sfimport log')
        logging.warning(url_dict)
        url_id = int(list(url_dict.keys())[0])
        #insert it into worktask
        #schedule a url for autorating by inserting into work task.
        del_query = 'delete from u2.dbo.worktask'
        mssql_obj = TsMsSqlWrap('U2')
        mssql_obj.execute_sql_commit(del_query)
        status = insert_and_autorate(url_id,self.ssh_obj)
        if status != 'completed':
            raise TestFailure('Autorating on %s is not complete. It is %s ' % (url_id, status))
        tail_scorers_log = 'tail -1000 %s > /home/toolguy/tail.log' % runtime.SCORER.scorer_log
        self.ssh_obj.execute(tail_scorers_log)
        time.sleep(5)
        self.ssh_obj.get('/home/toolguy/tail.log')
        log_content = open('tail.log','r').read()
        if 'ERROR' in log_content or 'Exception' in log_content:
            err_list.append('Errors found in scorers.log')
        default_scorer_names = []
        for scorer in runtime.SCORER.default_scorers:
            default_scorer_names.append(ScorerMap.get_name(scorer))
        for i in enabled_scorers:
            default_scorer_names.append(ScorerMap.get_name(i))
        for sc_name in default_scorer_names:
            if sc_name not in log_content:
                err_list.append('%s not in scorers.log. It is expected to run by default' % (sc_name))
        process_obj = OSProcessHandler('java',full_format=True,ssh_con=self.ssh_obj)
        if process_obj.is_running():
            process_obj.kill_processes()
        if len(err_list) != 0:
            raise TestFailure('\n'.join(err_list))        

    def test_01(self):
        """Check for scorers entries in scorers table"""
        err_list = []
        scorers_data_file = runtime.data_path + '/tsw/ar/scorers.txt'
        scorer_dict = eval(open(scorers_data_file,'r').read())
        for key in list(scorer_dict.keys()):
            if (ScorerMap.get_name(key) != scorer_dict[key]):
                err_list.append('Mismatch : %s %s for key %s' %(ScorerMap.get_name(key), scorer_dict[key], key))
        if len(err_list) != 0:
            raise TestFailure('\n'.join(err_list))


    def test_04(self):
        """Check for skipZerofacts property in scorer.properties and mongo must not preserve 0 results"""
        urls = ['*://gmail.com']
        result_list = []
        err_list = []
        clear_log = 'rm %s ; touch %s' % (runtime.SCORER.scorer_log,runtime.SCORER.scorer_log)
        self.ssh_obj.execute(clear_log)
        cat = 'bl'
        obj=sfimport()
        sfimportResult = obj.append_category(urls,cat)
        url_dict = obj.url_dict()
        enable_scorers_from_prod()
        logging.info("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.info("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.info("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.info("Total Number of URLS  : %s"%(len(urls)))
        if not (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure('Errors found in Sfimport log')
        logging.warning(url_dict)
        url_id = int(list(url_dict.keys())[0])
        mssql_obj = TsMsSqlWrap('U2')
        del_query = 'delete from u2.dbo.worktask'
        mssql_obj.execute_sql_commit(del_query)
        status = insert_and_autorate(url_id,self.ssh_obj)
        if status != 'completed':
            raise TestFailure('Autorating on %s is not complete. It is %s ' % (url_id, status))
        #kill ChainedScorer and QueuePopulator
        process_obj = OSProcessHandler('java',full_format=True,ssh_con=self.ssh_obj)
        if process_obj.is_running():
            process_obj.kill_processes()
        arssh = runtime.get_ssh(runtime.SCORER.host, self.username)
        expected_property = 'skipZeroScoreFacts'
        expected_value = 'true'
        arpo = SSHProperties(arssh, self.CONF_HOME + 'scorer.properties')
        if arpo.pobj[expected_property] != expected_value:
            err_list.append('%s file has appserver as %s instead of %s'%(self.CONF_HOME+'scorer.properties',arpo.pobj[expected_property],expected_value))
        mngo = MongoWrapAR('automated_autorating', dbname='autorating')
        url_doc = mngo.get_latest_by_url_id(url_id)
        rfp = ResultFactParser(url_doc)
        result_list.append(rfp.residential_ip())
        result_list.append(rfp.language_determiner())
        result_list.append(rfp.nutch_language_determiner())
        result_list.append(rfp.parked_domain())
        result_list.append(rfp.parked_domain())
        result_list.append(rfp.preproc_fact_bool())
        result_list.append(rfp.rating_fact_bool())
        result_list.append(rfp.rtc_dict())
        result_list.append(rfp.web_fetcher_http_code())
        for result in result_list:
            if result == 0:
                if result is not False:
                    err_list.append("%s fact value is zero even if skipZeroScoreFacts=true" % result)
        if len(err_list) != 0:
            raise TestFailure('\n'.join(err_list))

    def test_05(self):
        """Disable all scorers and check for run of default scorers on a URL"""
        url = 'http://test05.com'
        clear_log = 'rm %s ; touch %s' % (runtime.SCORER.scorer_log,runtime.SCORER.scorer_log)
        self.ssh_obj.execute(clear_log)
        default_scorer_names = []
        err_list = []
        for scorer in runtime.SCORER.default_scorers:
            default_scorer_names.append(ScorerMap.get_name(scorer))

        u2_scorer_obj = U2Scorers()
        u2_scorer_obj.disable_all()
        logging.info('Starting Scorer')
        self.ssh_obj.execute(self.start_scorer_cmd)
        self.ssh_obj.execute(self.score_url + url)
        for i in range(10):
            time.sleep(6)
        #tail scorers.log to a file and get it here
        tail_scorers_log = 'tail -1000 %s > /home/toolguy/tail.log' % runtime.SCORER.scorer_log
        self.ssh_obj.execute(tail_scorers_log)
        self.ssh_obj.get('/home/toolguy/tail.log')
        log_content = open('tail.log','r').read()
        if 'ERROR' in log_content or 'Exception' in log_content:
            err_list.append('Errors found in scorers.log')
        for sc_name in default_scorer_names:
            if sc_name not in log_content:
                err_list.append('%s not in scorers.log. It is expected to run by default' % (sc_name))
        process_obj = OSProcessHandler('java',full_format=True,ssh_con=self.ssh_obj)
        if process_obj.is_running():
            process_obj.kill_processes()
        if len(err_list) != 0:
            raise TestFailure('\n'.join(err_list))

    def test_02(self):
        """TS-1475"""
        logging.info('Starting Scorer')
        self.ssh_obj.execute(self.start_scorer_cmd)
        process_obj = OSProcessHandler('java',full_format=True,ssh_con=self.ssh_obj)
        if process_obj.is_running():
            process_obj.kill_processes()
        if (is_app_server_up(runtime.AppServer.host) is False): #Is app server up?
            raise TestFailure('App Server is Down because of stopping chained scorer')

    def test_03(self):
        """TS-1476"""
        logging.info('Starting Worktask populator')
        self.ssh_obj.execute(self.start_queue_populator)
        process_obj = OSProcessHandler('java',full_format=True,ssh_con=self.ssh_obj)
        if process_obj.is_running():
            process_obj.kill_processes()
        if (is_app_server_up(runtime.AppServer.host) is False): #Is app server up?
            raise TestFailure('App Server is Down because of stopping Queue Populator')

    def test_08(self):
        """enable all scorers from production and start autorating
        Fails because scorers are not setup properly"""
        urls = ['*://gmail.com']
        clear_log = 'rm %s ; touch %s' % (runtime.SCORER.scorer_log,runtime.SCORER.scorer_log)
        self.ssh_obj.execute(clear_log)
        err_list = []
        cat = 'bl'
        obj=sfimport()
        sfimportResult = obj.append_category(urls,cat)
        url_dict = obj.url_dict()
        enable_scorers_from_prod()
        logging.info("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.info("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.info("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.info("Total Number of URLS  : %s"%(len(urls)))
        if not (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure('Errors found in Sfimport log')
        logging.warning(url_dict)
        url_id = int(list(url_dict.keys())[0])
        #insert it into worktask
        #schedule a url for autorating by inserting into work task.
        mssql_obj = TsMsSqlWrap('U2')
        del_query = 'delete from u2.dbo.worktask'
        mssql_obj.execute_sql_commit(del_query)
        status = insert_and_autorate(url_id,self.ssh_obj)
        if status != 'completed':
            raise TestFailure('Autorating on %s is not complete. It is %s ' % (url_id, status))
        #kill ChainedScorer and QueuePopulator
        process_obj = OSProcessHandler('java',full_format=True,ssh_con=self.ssh_obj)
        if process_obj.is_running():
            process_obj.kill_processes()
        tail_scorers_log = 'tail -5000 %s > /home/toolguy/tail.log' % runtime.SCORER.scorer_log
        self.ssh_obj.execute(tail_scorers_log)
        time.sleep(10)
        self.ssh_obj.get('/home/toolguy/tail.log')
        log_content_lines = open('tail.log','r').readlines()
        for single_line in log_content_lines:
            if 'ERROR' in single_line or 'Exception' in single_line:
                err_list.append(single_line)
        if len(err_list) != 0:
            raise TestFailure('\n'.join(err_list))

    def test_09(self):
        """Enable all scorers running on production.Error in one scorer should not
        quit others from running"""
        urls = ['*://www.wikipedia.org/']
        clear_log = 'rm %s ; touch %s' % (runtime.SCORER.scorer_log,runtime.SCORER.scorer_log)
        self.ssh_obj.execute(clear_log)
        err_list = []
        cat = 'bl'
        obj=sfimport()
        sfimportResult = obj.append_category(urls,cat)
        url_dict = obj.url_dict()
        enabled_names = enable_scorers_from_prod()
        logging.info("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.info("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.info("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.info("Total Number of URLS  : %s"%(len(urls)))
        if not (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure('Errors found in Sfimport log')
        logging.info(url_dict)
        url_id = int(list(url_dict.keys())[0])
        #insert it into worktask
        #schedule a url for autorating by inserting into work task.
        mssql_obj = TsMsSqlWrap('U2')
        del_query = 'delete from u2.dbo.worktask'
        mssql_obj.execute_sql_commit(del_query)
        status = insert_and_autorate(url_id,self.ssh_obj)
        if status != 'completed':
            raise TestFailure('Autorating on %s is not complete. It is %s ' % (url_id, status))
        #kill ChainedScorer and QueuePopulator
        process_obj = OSProcessHandler('java',full_format=True,ssh_con=self.ssh_obj)
        if process_obj.is_running():
            process_obj.kill_processes()
        tail_scorers_log = 'tail -5000 %s > /home/toolguy/tail.log' % runtime.SCORER.scorer_log
        self.ssh_obj.execute(tail_scorers_log)
        time.sleep(10)
        self.ssh_obj.get('/home/toolguy/tail.log')
        fp = open('tail.log','r')
        log_content = fp.read()
        fp.close()
        log_content_lines = open('tail.log','r').readlines()
        for single_line in log_content_lines:
            if 'ERROR' in single_line or 'Exception' in single_line:
                logging.error(single_line)
        for name in enabled_names:
            if name not in log_content:
                err_list.append('%s not in scorers.log' % name)
            else:
                logging.info('validated %s' % name)
        if len(err_list) != 0:
            logging.error('\n'.join(err_list))

    def test_10(self):
        """verify the run of Autorating UrlScheduler"""
        clear_log = 'rm %s ; touch %s' % (runtime.SCORER.scorer_log,runtime.SCORER.scorer_log)
        self.ssh_obj.execute(clear_log)
        err_list = []
        self.ssh_obj.execute(self.url_scheduler)
        time.sleep(10)
        process_obj = OSProcessHandler('java',full_format=True,ssh_con=self.ssh_obj)
        if process_obj.is_running():
            process_obj.kill_processes()
        tail_scorers_log = 'tail -1000 %s > /home/toolguy/tail.log' % runtime.SCORER.scorer_log
        self.ssh_obj.execute(tail_scorers_log)
        time.sleep(5)
        self.ssh_obj.get('/home/toolguy/tail.log')
        log_content = open('tail.log','r').readlines()
        for single_line in log_content:
            if 'ERROR' in single_line or 'Exception' in single_line:
                err_list.append(single_line)
        if len(err_list) != 0:
            raise TestFailure('\n'.join(err_list))

    def test_11(self):
        """enable all scorers in scorers table.Other scorers should work if any scorer quits due to error"""
        raise TestFailure('Check if this is the expected behaviour . It fails for now at SiteadvisorMaint scorer')

    def test_12(self):
        """check if a url from a security queue gets autorated"""
        enabled_scorers = [4,12]
        err_list = []
        clear_log = 'rm %s ; touch %s' % (runtime.SCORER.scorer_log,runtime.SCORER.scorer_log)
        self.ssh_obj.execute(clear_log)
        u2_scorer_obj = U2Scorers()
        for i in enabled_scorers:
            u2_scorer_obj.enable_id(i)
        urls = ['*://themalicious.com']
        cat = 'ms'
        obj=sfimport(queue_name='Sandbox')
        sfimportResult = obj.queue(urls)
        url_dict = obj.url_dict()
        logging.info("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.info("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.info("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.info("Total Number of URLS  : %s"%(len(urls)))
        if not (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure('Errors found in Sfimport log')
        logging.warning(url_dict)
        url_id = int(list(url_dict.keys())[0])
        del_query = 'delete from u2.dbo.worktask'
        mssql_obj = TsMsSqlWrap('U2')
        mssql_obj.execute_sql_commit(del_query)
        status = insert_and_autorate(url_id,self.ssh_obj)
        if status != 'completed':
            raise TestFailure('Autorating on %s is not complete as the url is on a Security Queue. It is %s ' % (url_id, status))

    def test_13(self):
        """Check if a url from locked_queue gets autorated. Customer queue is locked"""
        enabled_scorers = [4,12]
        err_list = []
        clear_log = 'rm %s ; touch %s' % (runtime.SCORER.scorer_log,runtime.SCORER.scorer_log)
        self.ssh_obj.execute(clear_log)
        u2_scorer_obj = U2Scorers()
        for i in enabled_scorers:
            u2_scorer_obj.enable_id(i)
        urls = ['*://theprinceofindia.com']
        cat = 'bl'
        obj=sfimport(queue_name='Customer')
        sfimportResult = obj.queue(urls)
        url_dict = obj.url_dict()
        logging.info("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.info("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.info("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.info("Total Number of URLS  : %s"%(len(urls)))
        if not (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure('Errors found in Sfimport log')
        logging.warning(url_dict)
        url_id = int(list(url_dict.keys())[0])
        del_query = 'delete from u2.dbo.worktask'
        mssql_obj = TsMsSqlWrap('U2')
        mssql_obj.execute_sql_commit(del_query)
        status = insert_and_autorate(url_id,self.ssh_obj)
        if status != 'completed':
            raise TestFailure('Autorating on %s is not complete as the url is in a Locked Queue. It is %s ' % (url_id, status))

    def test_14(self):
        """Check if a url with a policy cat gets autorated"""
        enabled_scorers = [4,12]
        err_list = []
        clear_log = 'rm %s ; touch %s' % (runtime.SCORER.scorer_log,runtime.SCORER.scorer_log)
        self.ssh_obj.execute(clear_log)
        u2_scorer_obj = U2Scorers()
        for i in enabled_scorers:
            u2_scorer_obj.enable_id(i)
        urls = ['*://phishingcategory.com']
        cat = 'ph'
        obj=sfimport()
        sfimportResult = obj.append_category(urls,cat)
        url_dict = obj.url_dict()
        logging.info("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.info("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.info("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.info("Total Number of URLS  : %s"%(len(urls)))
        if not (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure('Errors found in Sfimport log')
        logging.warning(url_dict)
        url_id = int(list(url_dict.keys())[0])
        del_query = 'delete from u2.dbo.worktask'
        mssql_obj = TsMsSqlWrap('U2')
        mssql_obj.execute_sql_commit(del_query)
        status = insert_and_autorate(url_id,self.ssh_obj)
        if status != 'completed':
            raise TestFailure('Autorating on %s is not complete as the url is in a Locked Queue. It is %s ' % (url_id, status))






