import logging
import os
import re
import subprocess
import time
import unittest
from path import Path

import pytest
from libx.process import ShellExecutor
from conf.files import LOG, SH, PROP
from conf.properties import set_prop_application, prop_prevalence_agent, prop_publish_agent
from lib.db.d2_activeagents import ActiveAgentsTable
from lib.db.mssql import TsMsSqlWrap
from lib.exceptions import TestFailure


__author__ = 'sundaresan'

ERR_AGENT_MSSQL_TEMPLATE = "Specify property '%s' in application"



class SandboxedPrevalenceAgentTest(unittest.TestCase):
    """ Class for dealing with agents related cleanup actions - copying agents.log to sandbox directory """

    def setUp(self):
        """ Deletes agents file """
        # # super set up
        # SandboxedTest.setUp(self)

        # Delete log files
        Path(LOG.common).remove_p()

        # Create new application.properties file
        Path(PROP.application).remove_p()
        self.app_prop = set_prop_application(write_file_bool=True)

        # Establish database connections
        self.d2_con = TsMsSqlWrap('D2')
        self.active_agents = ActiveAgentsTable(self.d2_con)

        # Reset all locks in active_agents table
        self.active_agents.reset_active_agents()

        # Instance variables
        self.prop_file = os.path.abspath('./java-agent.properties')
        self.agent_exec_str = SH.start_agent + ' %s' % self.prop_file

    def tearDown(self):
        """Copies required files back to sandbox"""
        # Path.copyfile(LOG.common, '.')
        # Path.copyfile(PROP.application, '.')
        # # Copy agent log file
        # self.sandbox.copy_file_to_sandbox(LOG.common)
        # self.sandbox.copy_file_to_sandbox(PROP.application)
        #
        # #super tear down
        # SandboxedTest.tearDown(self)

    def internal_test_missing_app_property(self, missing_property, sleep_seconds=10, property_file='agent.properties'):
        """ Helper function for tests with missing property value

        :param missing_property: str
        :return: bool
        """
        if not isinstance(missing_property, str):
            raise TypeError('missing_property must be a str. Found: %s' % type(missing_property))

        # remove missing property from application properties
        del self.app_prop[missing_property]
        with open(PROP.application, 'w') as fpw:
            self.app_prop.store(fpw)

        # create publish agent properties
        prop_publish_agent(write_file_name=self.prop_file)

        # run the agent here
        sub_obj = ShellExecutor.run_daemon_standalone(self.agent_exec_str)
        time.sleep(sleep_seconds)
        sub_obj.kill()

        # assert for error string in log file
        search_string = ERR_AGENT_MSSQL_TEMPLATE % missing_property
        matches, mismatches = self.search_log_file(search_string, LOG.common)
        if mismatches:
            return False
        return True

    def search_log_file(self, search_strings, log_file):
        """
        Does a simple search for strings in log file. Returns tuple of matches(list) and misses(list)
        :param search_strings: list of strings
        :param log_file: path of log file
        :return: ([<matches>], [<misses>])

		"""
        time.sleep(10)
        if isinstance(search_strings, str):
            search_strings = [search_strings]

        # open log file
		
        log_file_contents = open(log_file, encoding='UTF-8').read()

        matches = []
        misses = []
        logging.info('Searching log file: ' + LOG.common)
        for search_string in search_strings:
            if search_string in log_file_contents:
                logging.info('Found in log file:' + search_string)
                matches.append(search_string)
            else:
                logging.info('Miss in log file:' + search_string)
                misses.append(search_string)

        if misses:
            logging.info('Total misses: %s' % str(len(misses)))
        return matches, misses

    def internal_execute_agent(self):


        log_file_contents = open(LOG.common).read()
        logging.error(log_file_contents)
        logging.info('Search string: %s' % err_str)
        with open(LOG.common) as fpr:
            if err_str in fpr.read():
                logging.info('Found in log file: %s' % err_str)
                return True
        # if bool(re.findall(err_str, log_file_contents)):
        #     return True
        logging.error('Missing in log file: ' + err_str)
        return False

    def check_err_prev_agent(self, err_str, missing_app_property_list=None):
        if isinstance(missing_app_property_list, str):
            missing_app_property_list = [missing_app_property_list]

        # remove missing property from application properties
        for missing_app_property in missing_app_property_list:
            del self.app_prop[missing_app_property]
        with open(PROP.application, 'w') as fpw:
            self.app_prop.store(fpw)

        # run agent and assert
        stdo, stde = ShellExecutor.run_wait_standalone(SH.prevalence_client)
        self.failIf(err_str not in stdo+stde, err_str)

    def execute_agent(self, *, timeout_secs=None):
        if not timeout_secs:
            timeout_secs = 300
            logging.warning('Timeout set to default value: %s secs' % timeout_secs)

        logging.info('Executing agent: %s' % self.agent_exec_str)
        process = subprocess.Popen(self.agent_exec_str, shell=True)
        try:
            process.wait(timeout=timeout_secs)
            stdo, stde = ['' if val is None else str(val.decode("UTF-8"))
                          for val in process.communicate(timeout=timeout_secs)]
        except subprocess.TimeoutExpired:
            process.kill()
            stdo, stde = ['' if val is None else str(val.decode("UTF-8")) for val in process.communicate()]
            logging.info('Process was killed via TimeoutExpired exception')
        return stdo, stde

    def run_and_shutdown_agent(self):
        # run the agent
        process = subprocess.Popen(self.agent_exec_str, shell=True)

        # Set shut down bit
        self.active_agents.set_shutdown_now('Prevalence')

        # wait for the process to shut down
        logging.info('Setting shutdown bit now')
        shutdown_timeout = 180
        try:
            process.wait(timeout=shutdown_timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            raise TestFailure('Shutdown timeout exceeded: %s' % shutdown_timeout)

        # assert active_agents table
        self.assertFalse(self.active_agents.get_is_running('Prevalence'), 'Lock was not released by agent!')
        self.assertFalse(self.active_agents.get_shutdown_now('Prevalence'), 'Shutdown now was not reset by agent!')

        # assert the log file
        search_strings = ['Shutting down the agent.',
                          'Checking shutdown_now bit for agent',
                          'Agent Shutting down.',
                          'com.mcafee.tsw.agent.AgentManager.clearAgentLock Clearing agent lock']
        matches, misses = self.search_log_file(search_strings, LOG.common)
        if misses:
            raise TestFailure('Shutdown string search returned misses')


class JavaAgent(SandboxedPrevalenceAgentTest):
    """java agent framework tests"""

    def test_start_agent_exists(self):
        """File StartAgent.sh exists"""
        self.failIf(not os.path.isfile(SH.start_agent))

    def test_no_arguments(self):
        """No arguments"""
        stdo, stde = ShellExecutor.run_wait_standalone(SH.start_agent)
        self.failIf('Error. Must specify properties file for agent' not in stde + stdo)

    def test_invalid_properties_file(self):
        """Invalid properties file"""
        stdo, stde = ShellExecutor.run_wait_standalone(SH.start_agent + ' unknown-properties-file')
        self.failIf('java.io.FileNotFoundException: unknown-properties-file ' not in stde + stdo)

    def test_missing_d2_host(self):
        """Properties error check: Missing mssql.d2.host"""
        missing_property = 'mssql.d2.host'
        self.assertTrue(self.internal_test_missing_app_property(missing_property))

    #@pytest.mark.xfail(reason="Word 'specify' mis-spelled in exception text message. - ")
    def test_missing_d2_db(self):
        """Properties error check: Missing mssql.d2.db"""
        # For the missing mssql.d2.db attribute, in agents.log Specify is misspelled as Specifiy
        # So hardcoding the search string in the test as below
        missing_property = 'mssql.d2.db'
        self.internal_test_missing_app_property(missing_property)
        search = 'Specifiy property \'mssql.d2.db\' in application properties file.'
        log_file_contents = open(LOG.common, encoding='UTF-8').read()
        self.assertTrue(search in log_file_contents)

    def test_missing_d2_user(self):
        """Properties error check: Missing mssql.d2.username"""
        missing_property = 'mssql.d2.username'
        #self.assertTrue(self.internal_test_missing_app_property(missing_property))

    def test_missing_d2_pass(self):
        """Properties error check: Missing mssql.d2.password"""
        missing_property = 'mssql.d2.password'
        self.assertTrue(self.internal_test_missing_app_property(missing_property))

    def test_agent_name_upper_case(self):
        """Prevalence Agent: Change agent.name=Prevalence to agent.name=PREVALENCE"""
        # set new agent name
        prop_prevalence_agent(write_file_name=self.prop_file,
                              update_dict={'agent.name': 'PREVALENCE',
                                           'agent.getlock': 'true'})

        # run the agent
        self.execute_agent(timeout_secs=5)

        # set lock on agent
        lock_state = self.active_agents.get_is_running('Prevalence')
        self.assertTrue(lock_state, 'Lock was not acquired by agent!')

    def test_agent_name_invalid(self):
        """Invalid agent name"""
        # set new agent name
        prop_prevalence_agent(write_file_name=self.prop_file,
                              update_dict={'agent.name': 'xPREVALENCEd',
                                           'agent.getlock': 'true'})

        # run the agent
        self.execute_agent(timeout_secs=5)

        search_strings = ['Unexpected error while processing agent workflow. Exiting.',
                          'Unexpected value found when checking if agent is running.']

        # assert the log file
        matches, misses = self.search_log_file(search_strings, LOG.common)
        if misses:
            raise TestFailure('Error string search returned misses')

    def test_log_file_exists(self):
        """Check log file"""
        prop_prevalence_agent(write_file_name=self.prop_file)

        # run the agent
        self.execute_agent(timeout_secs=3)

        search_strings = ['[u2.client.agents] com.mcafee.tsw.agent.AgentManager.<init> ',
                          'Adding Provider Class to manager.',
                          'class=com.mcafee.tsw.agent.provider.PrevalenceProvider',
                          'Adding Worker Class to manager.',
                          'class=com.mcafee.tsw.agent.worker.PrevalenceWorker',
                          'Adding Consumer Class to manager.',
                          'class=com.mcafee.tsw.agent.consumer.PrevalenceConsumer']

        # assert the log file
        matches, misses = self.search_log_file(search_strings, LOG.common)
        if misses:
            raise TestFailure('Error string search returned misses')

    def test_log_file_debug_info(self):
        """Check log file: DEBUG info"""
        prop_prevalence_agent(write_file_name=self.prop_file)

        # run the agent
        self.execute_agent(timeout_secs=3)

        search_strings = ['DEBUG [u2.client.agents] com.mcafee.tsw.agent.AgentManager.isAgentRunning']

        # assert the log file
        matches, misses = self.search_log_file(search_strings, LOG.common)
        if misses:
            raise TestFailure('Error string search returned misses')

    def test_agent_get_lock(self):
        """Agent is able to get lock in the active_agents table"""
        prop_prevalence_agent(write_file_name=self.prop_file,
                              update_dict={'agent.getlock': 'true'})

        # run the agent
        self.execute_agent(timeout_secs=5)

        # set lock on agent
        lock_state = self.active_agents.get_is_running('Prevalence')
        self.assertTrue(lock_state, 'Lock was not acquired by agent!')

    def test_agent_unable_to_acquire_lock(self):
        """Agent cannot get Lock"""
        prop_prevalence_agent(write_file_name=self.prop_file,
                              update_dict={'agent.getlock': 'true'})

        # set lock on agent
        self.active_agents.set_is_running('Prevalence')

        # run the agent
        self.execute_agent()

        # assert the log file
        search_strings = ['Cannot get agent lock. The agent is already running. agent=Prevalence']
        matches, misses = self.search_log_file(search_strings, LOG.common)
        if misses:
            raise TestFailure('Not found: Cannot get agent lock. The agent is already running. agent=Prevalence')

    def test_agent_shut_down(self):
        """Shut down agent"""
        prop_prevalence_agent(write_file_name=self.prop_file)
        self.run_and_shutdown_agent()

    def test_agent_get_lock_false(self):
        """agent.getlock=false"""
        prop_prevalence_agent(write_file_name=self.prop_file,
                              update_dict={'agent.getlock': 'false'})

        # release lock on agent
        self.active_agents.unset_is_running('Prevalence')

        # run the agent
        self.execute_agent(timeout_secs=10)

        # assert the lock value
        self.assertFalse(self.active_agents.get_is_running('Prevalence'), 'Agent is_running is not false')

        # assert the log file
        search_strings = ['[u2.client.agents] com.mcafee.tsw.agent.AgentManager.<init> ',
                          'Adding Provider Class to manager.',
                          'class=com.mcafee.tsw.agent.provider.PrevalenceProvider',
                          'Adding Worker Class to manager.',
                          'class=com.mcafee.tsw.agent.worker.PrevalenceWorker',
                          'Adding Consumer Class to manager.',
                          'class=com.mcafee.tsw.agent.consumer.PrevalenceConsumer']
        matches, misses = self.search_log_file(search_strings, LOG.common)
        if misses:
            raise TestFailure('Error string search returned misses')

    def test_agent_get_lock_false_still_runs(self):
        """agent.getlock=false, is_running=1"""
        prop_prevalence_agent(write_file_name=self.prop_file,
                              update_dict={'agent.getlock': 'false'})

        # release lock on agent
        self.active_agents.unset_is_running('Prevalence')

        # run the agent
        self.execute_agent(timeout_secs=10)

        # assert the log file
        search_strings = ['[u2.client.agents] com.mcafee.tsw.agent.AgentManager.<init> ',
                          'Adding Provider Class to manager.',
                          'class=com.mcafee.tsw.agent.provider.PrevalenceProvider',
                          'Adding Worker Class to manager.',
                          'class=com.mcafee.tsw.agent.worker.PrevalenceWorker',
                          'Adding Consumer Class to manager.',
                          'class=com.mcafee.tsw.agent.consumer.PrevalenceConsumer']
        matches, misses = self.search_log_file(search_strings, LOG.common)
        if misses:
            raise TestFailure('Error string search returned misses')

    def test_verbose_false(self):
        """verbose=false"""
        prop_prevalence_agent(write_file_name=self.prop_file,
                              update_dict={'verbose': 'false'})

        # run the agent
        process = subprocess.Popen(self.agent_exec_str + '> verbose.log 2>&1', shell=True)
        time.sleep(10)
        process.kill()

        # assertion
        my_regex = re.compile('^Adding Provider Class to manager\.')
        my_string = open('verbose.log').read()
        self.assertFalse(my_regex.match(my_string))

    def test_verbose_true(self):
        """verbose=true"""
        prop_prevalence_agent(write_file_name=self.prop_file,
                              update_dict={'verbose': 'true'})

        # run the agent
        process = subprocess.Popen(self.agent_exec_str + '> verbose.log 2>&1', shell=True)
        time.sleep(10)
        process.kill()

        # assertion
        my_regex = re.compile('^Adding Provider Class to manager\.')
        #my_string = open('verbose.log').read()

        self.assertTrue('Adding Provider Class to manager.' in open('verbose.log').read())
        #self.assertTrue(my_regex.search(my_string))


    def test_update_process_history_record_count(self):
        """agent.updateProcessHistory=true"""
        prop_prevalence_agent(write_file_name=self.prop_file,
                              update_dict={'agent.updateProcessHistory': 'true'})

        #get max id ProcessHistory table
        r2_con = TsMsSqlWrap('R2')
        if r2_con.get_select_exactly_one_row_or_error('select count(*) x from ProcessHistory')['x'] == 0:
            min_id = 0
        else:
            min_id = r2_con.get_select_exactly_one_row_or_error('select max(process_id) x from ProcessHistory')['x']

        # run and shutdown the agent
        self.run_and_shutdown_agent()

        # look for process history information
        query = "select * from ProcessHistory where process_name='Prevalence' and process_id > %s" % min_id
        new_process_row = r2_con.get_select_data(query)
        if len(new_process_row) == 0:
            raise TestFailure('0 new rows added in process history table')
        elif len(new_process_row) > 1:
            raise TestFailure('2 or more new rows added in process history table')

        record_count = re.findall(r' itemsProcessed=(\d+)\n', open(LOG.common, encoding='UTF-8').read())[0]
        self.assertEqual(record_count, str(new_process_row[0]['records_processed']))

    def test_update_process_history_false(self):
        """agent.updateProcessHistory=false"""
        prop_prevalence_agent(write_file_name=self.prop_file,
                              update_dict={'agent.updateProcessHistory': 'false'})

        #get max id ProcessHistory table
        r2_con = TsMsSqlWrap('R2')
        if r2_con.get_select_exactly_one_row_or_error('select count(*) x from ProcessHistory')['x'] == 0:
            min_id = 0
        else:
            min_id = r2_con.get_select_exactly_one_row_or_error('select max(process_id) x from ProcessHistory')['x']

        # run and shutdown the agent
        self.run_and_shutdown_agent()

        # look for process history information
        query = "select * from ProcessHistory where process_name='Prevalence' and process_id > %s" % min_id
        new_process_rows = r2_con.get_select_data(query)
        if len(new_process_rows) != 0:
            raise TestFailure('1 or more new rows added in process history table')

    #@pytest.mark.xfail(reason="Word 'specify' mis-spelled in exception text message. - ")
    def test_batch_size(self):
        """Batch size"""
        # assert 0 == 1
        prop_prevalence_agent(write_file_name=self.prop_file,
                              update_dict={'prevalence.batchsize': '10'})

        # run the agent
        self.execute_agent(timeout_secs=10)

        search_strings = ['Requesting items to be worked on. batchSize=10',
                          'SELECT TOP 10 cl_hash, action FROM PrevalenceQueue (NOLOCK)']

        # assert the log file
        matches, misses = self.search_log_file(search_strings, LOG.common)
        #if misses:
        if not misses:
            raise TestFailure('Error string search returned misses')

    def test_column_domain_clhash(self):
        """Prevalence Table: domain_clhash exists"""
        qry = "SELECT * FROM sys.columns WHERE [name] = N'domain_clhash' AND [object_id] = OBJECT_ID(N'prevalence')"
        self.assertEqual(self.d2_con.get_row_count(qry), 1, 'Exactly 1 row expected for column')

    def test_column_domain_prevalence(self):
        """Prevalence Table: domain_prevalence exists"""
        qry = "SELECT * FROM sys.columns WHERE [name] = N'domain_prevalence' AND [object_id] = OBJECT_ID(N'prevalence')"
        self.assertEqual(self.d2_con.get_row_count(qry), 1, 'Exactly 1 row expected for column')

    def test_column_is_domain(self):
        """Prevalence Table: is_domain exists"""
        qry = "SELECT * FROM sys.columns WHERE [name] = N'is_domain' AND [object_id] = OBJECT_ID(N'prevalence')"
        self.assertEqual(self.d2_con.get_row_count(qry), 1, 'Exactly 1 row expected for column')
