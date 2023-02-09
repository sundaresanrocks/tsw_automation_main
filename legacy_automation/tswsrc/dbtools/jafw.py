"""
Java Agent Framework Tests
**************************
"""
from conf.properties import set_prop_application, prop_prevalence_agent

__author__ = 'manoj'

import re
import os
import pymssql
import logging

from framework.test import SandboxedTest
from lib.exceptions import TestFailure
from libx.process import ShellExecutor


# from tsw.config.env.nightly import Base as envcon
from lib.db.mssql import TsMsSqlWrap
from conf.properties import prop_publish_agent
from conf.files import PROP, SH, LOG


LOCAL_AGENT_PROP_FILE = 'agent.properties'
SH_JAVA_AGENT = SH.start_agent + ' %s' % LOCAL_AGENT_PROP_FILE


class SandboxedAgentsTest(SandboxedTest):

    def internal_execute_agent(self, agent_prop, err_str, log_file=None):

        if os.path.isfile(LOG.agents):
            os.remove(LOG.agents)

        set_prop_application(write_file_bool=True)

        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)

        stdo, stde = ShellExecutor.run_wait_standalone(SH_JAVA_AGENT)
        if log_file == 'agentslog':
            log_file_contents = open(LOG.agents).read()
            file = LOG.agents
        elif log_file == None:
            log_file_contents = open(LOG.agents).read()
            file = LOG.agents
        elif log_file == 'commonlog':
            log_file_contents = open(LOG.common).read()
            file = LOG.common
        logging.error(log_file_contents)
        logging.info('Search string: %s' % err_str)
        #with open(LOG.agents) as fpr:
        with open(file) as fpr:
            if err_str in fpr.read():
                logging.info('Found in log file: %s' % err_str)
                return True
        # if bool(re.findall(err_str, log_file_contents)):
        #     return True
        logging.error('Missing in log file: ' + err_str)
        return False

    def check_err_prev_client(self, err_str, missing_app_property=None):
        prop = set_prop_application()
        if isinstance(missing_app_property, str):
            missing_app_property = [missing_app_property]
        if missing_app_property:
            for key in missing_app_property:
                del prop[key]
        prop.write_to_file(PROP.application)
        stdo, stde = ShellExecutor.run_wait_standalone(SH.prevalence_client)
        # logging.warning(stde)
        # logging.warning(stdo)
        self.failIf(err_str not in stdo+stde, err_str)


class JavaAgentFW(SandboxedAgentsTest):
    """
    java agent framework tests
    """

    def test_01(self):
        """File StartAgent.sh exists"""
        self.failIf(not os.path.isfile(SH.start_agent))

    def test_02(self):
        """No arguments"""
        stdo, stde = ShellExecutor.run_wait_standalone(SH.start_agent)
        self.failIf('Error. Must specify properties file for agent' not in stde + stdo)

    def test_03(self):
        """Invalid properties file"""
        stdo, stde = ShellExecutor.run_wait_standalone(SH.start_agent + ' unknown-properties-file')
        self.failIf('java.io.FileNotFoundException: unknown-properties-file ' not in stde + stdo)

    def test_04(self):
        """Properties error check: Missing No appserver"""

        app_prop = set_prop_application()
        with open(PROP.application, 'w') as fpw:
            app_prop.store(fpw)

        if os.path.isfile(LOG.agents):
            os.remove(LOG.agents)

        agent_prop = prop_prevalence_agent()
        del agent_prop['agent.appserver']
        logging.info(LOCAL_AGENT_PROP_FILE)
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)

        stdo, stde = ShellExecutor.run_wait_standalone(SH_JAVA_AGENT)

        logging.error(stdo)
        logging.error(stde)

    def test_05(self):
        """Properties error check: Missing mssql.d2.host"""
        missing_property = 'mssql.d2.host'
        self.assertTrue(self.inernal_test_missing_app_property(missing_property))

    def test_06(self):
        """Properties error check: Missing mssql.d2.db"""
        missing_property = 'mssql.d2.db'
        self.assertTrue(self.inernal_test_missing_app_property(missing_property))

    def test_07(self):
        """Properties error check: Missing mssql.d2.username"""
        missing_property = 'mssql.d2.username'
        self.assertTrue(self.inernal_test_missing_app_property(missing_property))

    def test_08(self):
        """Properties error check: Missing mssql.d2.password"""
        missing_property = 'mssql.d2.password'
        self.assertTrue(self.inernal_test_missing_app_property(missing_property))

    def test_09(self):
        """Get agent lock not specified. Specify property 'agent.getlock' in the properties file"""
        err_str = "Get agent lock not specified. Specify property 'agent.getlock' in the properties file"
        prop = prop_publish_agent()
        del prop['agent.getlock']

        self.assertTrue(self.internal_execute_agent(prop, err_str))

    #
    # class ShutdownAgent(SandboxedAgentsTest):
    #     pass


class Prev1(SandboxedAgentsTest):
    def test_01(self):
        """Properties error check: Missing mssql.d2.host"""
        missing_property = 'mssql.d2.host'
        self.check_err_prev_client(
            "No MSSQL host specified. Specify property 'mssql.d2.host' in properties file",
            missing_app_property=missing_property)

    def test_02(self):
        """Properties error check: Missing mssql.d2.db"""
        missing_property = 'mssql.d2.db'
        self.check_err_prev_client(
            "No MSSQL db specified. Specify property 'mssql.d2.db' in properties file",
            missing_app_property=missing_property)

    def test_03(self):
        """Properties error check: Missing mssql.d2.username"""
        missing_property = 'mssql.d2.username'
        self.check_err_prev_client(
            "No username specified.  Specify property 'mssql.d2.username' in properties file",
            missing_app_property=missing_property)

    def test_04(self):
        """Properties error check: Missing mssql.d2.password"""
        missing_property = 'mssql.d2.password'
        self.check_err_prev_client(
            "No password specified. Specify property 'mssql.d2.password' in properties file",
            missing_app_property=missing_property)

    def test_05(self):
        """Properties error check: Missing mssql.u2.host"""
        missing_property = 'mssql.u2.host'
        self.check_err_prev_client(
            "No MSSQL host specified. Specify property 'mssql.u2.host' in properties file",
            missing_app_property=missing_property)

    def test_06(self):
        """Properties error check: Missing mssql.u2.db"""
        missing_property = 'mssql.u2.db'
        self.check_err_prev_client(
            "No MSSQL db specified. Specify property 'mssql.u2.db' in properties file",
            missing_app_property=missing_property)

    def test_07(self):
        """Properties error check: Missing mssql.u2.username"""
        missing_property = 'mssql.u2.username'
        self.check_err_prev_client(
            "No username specified.  Specify property 'mssql.u2.username' in properties file",
            missing_app_property=missing_property)

    def test_08(self):
        """Properties error check: Missing mssql.u2.password"""
        missing_property = 'mssql.u2.password'
        self.check_err_prev_client(
            "No password specified. Specify property 'mssql.u2.password' in properties file",
            missing_app_property=missing_property)

    def test_09(self):
        """Properties error check: Missing mssql.r2.host"""
        missing_property = 'mssql.r2.host'
        self.check_err_prev_client(
            "No MSSQL host specified. Specify property '%s' in properties file." % missing_property,
            missing_app_property=missing_property)

    def test_10(self):
        """Properties error check: Missing mssql.r2.db"""
        missing_property = 'mssql.r2.db'
        self.check_err_prev_client(
            "No MSSQL db specified. Specify property 'mssql.r2.db' in properties file.",
            missing_app_property=missing_property)

    def test_11(self):
        """Properties error check: Missing mssql.r2.username"""
        missing_property = 'mssql.r2.username'
        self.check_err_prev_client(
            "No username specified.  Specify property 'mssql.r2.username' in properties file.",
            missing_app_property=missing_property)

    def test_12(self):
        """Properties error check: Missing mssql.r2.password"""
        missing_property = 'mssql.r2.password'
        self.check_err_prev_client(
            "No password specified. Specify property 'mssql.r2.password' in properties file",
            missing_app_property=missing_property)

    def test_00_no_sanity(self):
        """No sanity file specified in properties file"""
        err_str = 'No sanity file specified in properties file'
        self.check_err_prev_client(err_str, 'sanityFile')

    def test_14(self):
        """No mongodb.topsite.host specified in properties file"""
        err_str = 'No MongoDB host is specified'
        self.check_err_prev_client(err_str, 'mongodb.topsite.host')

    def test_00_no_mongo_database(self):
        """No mongodb.topsite.database specified in properties file"""
        err_str = 'No database property is specified.'
        self.check_err_prev_client(err_str, 'mongodb.topsite.database')

    def test_00_no_mongo_collection(self):
        """No mongodb.topsite.collection specified in properties file"""
        err_str = 'java.lang.NullPointerException'
        self.check_err_prev_client(err_str, 'mongodb.topsite.collection')


class Prev2(SandboxedAgentsTest):
    def internal_check_errors(self, err_str):
        logging.info('Search string: %s' % err_str)
        with open(LOG.agents) as fpr:
            if err_str in fpr.read():
                logging.info('Found in log file: %s' % err_str)
                return True
        logging.error('Missing in log file: ' + err_str)
        return False

    def internal_execute_prev_client(self, cmd_line):

        if os.path.isfile(LOG.agents):
            os.remove(LOG.agents)

        set_prop_application(write_file_bool=True)

        stdo, stde = ShellExecutor.run_wait_standalone(SH.prevalence_client + ' %s' % cmd_line)

        log_file_contents = open(LOG.agents).read()
        logging.error(log_file_contents)
        return stdo + stde

    def test_01(self):
        """Prev Client: The shell script exists"""
        self.assertFalse(os.path.isfile(SH.prevalence_client),
                    "Prevalence client shell script %s was not found" % SH.prevalence_client)

    def test_02(self):
        """Prev Client: No argument"""
        self.internal_execute_prev_client(cmd_line="")

    def test_03(self):
        """Prev Client: Queue exists"""
        d2_con = TsMsSqlWrap('TELEMETRY')
        sql = 'select top 1 * from PrevalenceQueue with (nolock)'
        try:
            cur = d2_con.get_row_count(sql)

        except pymssql.ProgrammingError as err:
            if not 'Invalid object name' in str(err):
                raise
            else:
                raise TestFailure('Table not found in db')

    def test_04(self):
        """Prev Client: arguemnt 1"""
        stdoe = self.internal_execute_prev_client(cmd_line="1")
        pat = 'Prevalence Record'
        self.assertEqual(1, len(re.findall(pat, stdoe)))

    # def test_05(self):
    #     """Prev Client: Check prioiry order"""
    #
    # def test_06(self):
    #     """Prev Client: Check queued_on order"""
    #
    def test_07(self):
        """Prev Client: top sites data - true"""

    #
    # def test_08(self):
    #     """Prev Client: top sites data - false"""
    #
    # def test_09(self):
    #     """Prev Client: sanity list data - true"""
    #
    # def test_10(self):
    #     """Prev Client: sanity list data - false"""
    #
    # def test_11(self):
    #     """Prev Client: prevalence count is right"""
    #
    # def test_12(self):
    #     """Prev Client: Picks data in a priority basis"""



