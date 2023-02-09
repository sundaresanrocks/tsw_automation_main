"""
=============================
TMAN TESTS
=============================
"""
import time
import logging

from framework.test import SandboxedTest
from dbtools.agents import Agents
from lib.exceptions import TestFailure, ValidationError
from lib.db.mssql import TsMsSqlWrap
from framework.ddt import testdata_file, tsadriver
from lib.sfimport import sfimport
import runtime
import random


@tsadriver
class TMAN(SandboxedTest):
    testprefix = 'test'
    agent = 'tman'

    @testdata_file(runtime.data_path + '/tsw/agents/tman/help.txt')
    def test_tman_help(self, search_list):
        """TMAN: Help option"""
        obj = Agents(self.agent)
        obj.tmpl_agent_stdout_check('-h', search_list)

    @testdata_file(runtime.data_path + '/tsw/agents/tman/version.txt')
    def test_tman_version(self, search_list):
        """Version check"""
        obj = Agents(self.agent)
        obj.tmpl_agent_stdout_check('-V', search_list)

    def test_log_default_plain(self):
        """tman run - default log"""
        obj = Agents(self.agent)
        args = ' -u -i -d -s '
        obj.tmpl_agent_log(args, default_log=True, debug_log=False)

    def test_log_default_debug(self):
        """tman run - debug log enabled."""
        obj = Agents(self.agent)
        args = ' -u -i -d -s -D '
        obj.tmpl_agent_log(args, default_log=True, debug_log=True)

    def test_log_named_plain(self):
        """tman run named log"""
        obj = Agents(self.agent)
        args = ' -u -i -d -s '
        obj.tmpl_agent_log(args, default_log=False, debug_log=False)

    def test_log_named_debug(self):
        """tman run named log (with debugging enabled)"""
        obj = Agents(self.agent)
        args = ' -u -i -d -s -D '
        obj.tmpl_agent_log(args, default_log=False, debug_log=True)

    def test_is_running(self):
        """tman run is running
        Check the activity table for is_running status before, after and When TMAN is running
        1. check status before (done automatically)
        2. check when TMAN is running
        3. check after TMAN completes
        4. verification
        """

        # 1. check status before (done automatically)
        args = ' -l 10 -x 10 -d -i -s -D '
        x = Agents(self.agent)

        # 2. check when TMAN is running
        # 3. check after TMAN completes
        #2 & 3 done by test_agent_run
        x.tmpl_is_running(args)
        status = x.get_status()
        if status[1] != 0:
            raise TestFailure('isRunning is not set to 0 after TMAN exit')

    def not_working_test_is_running(self):

        """
        Check the activity table for is_running status before, after and When TMAN is running

        Check the URLs are inserted or not

        0. Get some init value for checks
        1. check status before (done automatically)
        2. check when TMAN is running
        3. check after TMAN completes
        4. verification

        """

        logging.info("Check the tman_sanity before TMAN is running")
        query = 'select count(*) from U2.dbo.queue where priority > 9000'
        u2obj = TsMsSqlWrap('U2')
        count1 = u2obj.get_row_count(query)
        logging.info('Number of urls before tman: %s' % count1)

        # 1. check status before (done automatically)
        # run agent
        args = ' -l 10 -x 10 -d -i -s -D '
        x = Agents(self.agent)

        # 2. check when TMAN is running
        #3. check after TMAN completes
        #2 & 3 done by test_agent_run
        x.tmpl_is_running(args)

        count2 = u2obj.get_row_count(query)
        if count2 - count1 == 10:
            logging.info("After running the TMAN Processed URL are deleted form the queue table")
        else:
            raise ValidationError("TMAN execution couldn't delete form the queue table")

    def test_01(self):
        """TMAN:Test url insertion into build table."""
        url_ids = []
        u2_obj = TsMsSqlWrap('U2')
        d2_obj = TsMsSqlWrap('D2')
        url = "*://tman" + str(time.time()) + ".COM"
        urls = [url]
        obj = sfimport()
        obj.append_category(urls, 'ms')
        url_dict = obj.url_dict()

        for key in list(url_dict.keys()):
            logging.warning(key)
            url_ids.append(key)
            update_query = "update u2.dbo.queue set priority = 99999 where url_id=" + key
            u2_obj.execute_sql_commit(update_query)
        obj = Agents(self.agent)
        obj.run_agent(agent_args="-D", output_file='out.txt')

        for key in list(url_dict.keys()):
            logging.warning(key)
            url_ids.append(key)
            query = "select url_id from d2.dbo.build where url_id=" + key
            urls = d2_obj.get_select_data(query)
        if len(urls) == 0:
            raise TestFailure('URL not present on build table after TMAN run')
        logging.warning(urls)
        for key in list(url_dict.keys()):
            logging.warning(key)
            update_query = "update u2.dbo.queue set priority = 9999 where url_id=" + key
            u2_obj.execute_sql_commit(update_query)

    def test_02(self):
        """TMAN: Test inserting a URL with cgi parameters."""
        url_ids = []
        u2_obj = TsMsSqlWrap('U2')
        d2_obj = TsMsSqlWrap('D2')
        url = "*://tmancgi" + str(time.time()) + ".COM/?this=546"
        urls = [url]
        obj = sfimport()
        obj.append_category(urls, 'ms')
        url_dict = obj.url_dict()

        for key in list(url_dict.keys()):
            logging.warning(key)
            url_ids.append(key)
            update_query = "update u2.dbo.queue set priority = 99999 where url_id=" + key
            u2_obj.execute_sql_commit(update_query)
        obj = Agents(self.agent)
        obj.run_agent(agent_args="-D", output_file='out.txt')

        for key in list(url_dict.keys()):
            logging.warning(key)
            url_ids.append(key)
            query = "select url_id from d2.dbo.build where url_id=" + key
            urls = d2_obj.get_select_data(query)
        if len(urls) == 0:
            raise TestFailure('URL not present on build table after TMAN run')
        logging.warning(urls)
        for key in list(url_dict.keys()):
            logging.warning(key)
            update_query = "update u2.dbo.queue set priority = 9999 where url_id=" + key
            u2_obj.execute_sql_commit(update_query)

    @testdata_file(runtime.data_path + '/tsw/agents/tman/delete.txt')
    def test_03(self, data):
        """TMAN: Test deleting a URL"""
        url_ids = []
        u2_obj = TsMsSqlWrap('U2')
        d2_obj = TsMsSqlWrap('D2')
        url = data
        urls = [url]
        sf_obj = sfimport()
        sf_obj.append_category(urls, 'ms')
        url_dict = sf_obj.url_dict()

        for key in list(url_dict.keys()):
            logging.warning(key)
            update_query = "update u2.dbo.queue set priority = 99999 where url_id=" + key
            u2_obj.execute_sql_commit(update_query)
        sf_obj.delete_category(urls)
        del_sfimportResult = sf_obj.delete_category(urls)
        logging.debug("Total_Successful :  %s"%(del_sfimportResult["Total_Successful"]))
        # check in queue
        for key in list(url_dict.keys()):
            logging.warning(key)
            url_ids.append(key)
            query = "select url_id from u2.dbo.queue where url_id=" + key
            urls = u2_obj.get_select_data(query)
        logging.warning(urls)
        #sf_obj.args()
        # run tman
        ag_obj = Agents(self.agent)
        ag_obj.run_agent(agent_args="-D", output_file='newout.txt')

        # check in build.URL should not be present
        for key in list(url_dict.keys()):
            logging.warning(key)
            url_ids.append(key)
            query = "select url_id from d2.dbo.build where url_id=" + key
            urls = d2_obj.get_select_data(query)
            logging.warning(urls)
            if len(urls) != 0:
                raise TestFailure('URL present in build even after deleting')

    @testdata_file(runtime.data_path + '/tsw/agents/tman/insert.txt')
    def test_gen_entries(self, data):
        """TMAN: carry out domain transactions and update the build with generated entries
        The following function will insert the urls present in the insert.txt file and will also enter
        the ips present in the domainZ collection present under the url as the geerated entries for the domain url.
        """
        url_ids = []
        u2_obj = TsMsSqlWrap('U2')
        d2_obj = TsMsSqlWrap('D2')
        urls = data
        url_list = [urls]
        sf_obj = sfimport()
        sf_obj.append_category(url_list,'ms')
        url_dict = sf_obj.url_dict()

        for key in list(url_dict.keys()):
            logging.warning(key)
            url_ids.append(key)
            update_query = "update u2.dbo.queue set priority = 99999 where url_id=" + key
            u2_obj.execute_sql_commit(update_query)
        obj = Agents(self.agent)
        obj.run_agent(agent_args="-D", output_file='out.txt')

        for key in list(url_dict.keys()):
            logging.warning(key)
            url_ids.append(key)
            query = "select url_id from d2.dbo.build where url_id=" + key
            urls = d2_obj.get_select_data(query)
        if len(urls) == 0:
            raise TestFailure('URL not present on build table after TMAN run')
        logging.warning(urls)

    def test_del_ips(self):
        """TMAN: Test deleting an ip address"""
        url_ids = []
        u2_obj = TsMsSqlWrap('U2')
        d2_obj = TsMsSqlWrap('D2')
        url = str("73." +  str(random.randint(0,255))+ "." +  str(random.randint(0,255)) + "." +  str(random.randint(0,255)))
        print(url)
        urls = [url]
        sf_obj = sfimport()
        sf_obj.append_category(urls, 'ms')
        url_dict = sf_obj.url_dict()

        for key in list(url_dict.keys()):
            logging.warning(key)
            update_query = "update u2.dbo.queue set priority = 99999 where url_id=" + key
            u2_obj.execute_sql_commit(update_query)
        sf_obj.delete_category(urls)
        del_sfimportResult = sf_obj.delete_category(urls)
        logging.debug("Total_Successful :  %s"%(del_sfimportResult["Total_Successful"]))
        # check in queue
        for key in list(url_dict.keys()):
            logging.warning(key)
            url_ids.append(key)
            query = "select url_id from u2.dbo.queue where url_id=" + key
            urls = u2_obj.get_select_data(query)
        logging.warning(urls)
        # run tman
        ag_obj = Agents(self.agent)
        ag_obj.run_agent(agent_args="-D", output_file='newout.txt')

        # check in build.IP should not be present
        for key in list(url_dict.keys()):
            logging.warning(key)
            url_ids.append(key)
            query = "select url_id from d2.dbo.build where url_id=" + key
            urls = d2_obj.get_select_data(query)
            logging.warning(urls)
            if len(urls) != 0:
                raise TestFailure('IP still present in build even after deleting')

    def test_del_childurls(self):
        """TMAN: Test deleting child urls
        This function inserts  a parent and child url pair into the build table and deletes child url only.
        """
        url_ids = []
        url_ids2 = []
        u2_obj = TsMsSqlWrap('U2')
        d2_obj = TsMsSqlWrap('D2')
        currtym = str(time.time())
        urlparent = "*://tmanpc" + currtym + ".COM"
        urlchild =  "*://tmanpc" + currtym + ".COM/childtest"
        urls = [urlparent,urlchild]
        urls2 = [urlchild]
        sf_obj = sfimport()
        sf_obj2 = sfimport()
        sf_obj.append_category(urls, 'ms')
        url_dict = sf_obj.url_dict()

        for key in list(url_dict.keys()):
            logging.warning(key)
            update_query = "update u2.dbo.queue set priority = 99999 where url_id=" + key
            u2_obj.execute_sql_commit(update_query)

        sf_obj2.delete_category(urls2)
        url_dict2 = sf_obj2.url_dict()
        del_sfimportResult = sf_obj2.delete_category(urls2)
        logging.debug("Total_Successful :  %s"%(del_sfimportResult["Total_Successful"]))
        # check in queue
        for key in list(url_dict2.keys()):
            logging.warning(key)
            url_ids2.append(key)
            query = "select url_id from u2.dbo.queue where url_id=" + key
            urls = u2_obj.get_select_data(query)
        logging.warning(urls)
        # run tman
        ag_obj = Agents(self.agent)
        ag_obj.run_agent(agent_args="-D", output_file='newout.txt')

        # check in build.Child url should not be present
        for key in list(url_dict2.keys()):
            logging.warning(key)
            url_ids2.append(key)
            query = "select url_id from d2.dbo.build where url_id=" + key
            urls2 = d2_obj.get_select_data(query)
            logging.warning(urls2)
            if len(urls2) != 0:
                raise TestFailure('Child url still present in build even after deleting')
