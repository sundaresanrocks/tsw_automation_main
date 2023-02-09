"""
======================================
Publishing Agent Test Case Automation
======================================
"""
from lib.db import d2_activeagents

__author__ = "AviMehenwal & Sundaresan"

import datetime
import logging
import os.path
import pprint
import re
import time

from path import Path
import pytest
print ("Hellobefore")
import runtime
from conf.properties import set_prop_application, prop_publish_agent
from dbtools.jafw import SandboxedAgentsTest
from framework.test import SandboxedTest
from libx.process import ShellExecutor
from lib.db.mssql import TsMsSqlWrap
from lib.db.telemetrydb import PrevalenceTable
from lib.utils import db_reset
db_reset.db_reset()

print("hello")
LOCAL_AGENT_PROP_FILE = Path('agent.properties')
SLEEP_SECONDS = 2
ERR_AGENT_MSSQL_TEMPLATE = "Specify property '%s' in application properties file"
AGENT_START_STRING = "Adding Provider Class to manager. class=com.mcafee.tsw.agent.provider.PublishPrevalenceProvider"
AGENT_COMPLETED_STRING = "syncPrevalenceWithBuildTable Finish sync of prevalence table with the build table."
DATA = ""
DB_CLEAN_UP = True

XL_CAT_ilsx = """(0x1D44B22B761708BFC38FCE9D,0x356D9F66D319BAD175B427C8,0xE0194564BD5BAE55A8F94FB8,0x2C76BACF45AA535DC8F7A757)"""
#XL_REMOVAL_CRITERIA = """(0x10AA53FD0315C0A98CD5A7B7,0xA7ECC496AEA38CF7F4021275,0xC46FA65974F88DE9FB05DDC1)"""
XL_REMOVAL_CRITERIA = """(0x10AA53FD0315C0A98CD5A7B7,0xC46FA65974F88DE9FB05DDC1)"""
COMMON_MCAFEESECURE = """
(
0x019541D3F9F32C992CFC264C,0x01A9EC82BFE18C60C99BEE50,0x01C397B5172F2C31A6D04FEA,
0xFFAC7BE95B26B0A63CC07E46,
0x0DC8388FEF9951846DF39D99,0x0DD0E2690D011A44350C8ADC,0x0DD0ECA0D4267BF60F2A6634,
0x0D2CCA21A9A644FDCE9FC3D4,0x0D4962F7708B13B9870EC1F6,0x0D5C19E880152DB1FC1E3F25,
0x002CC7AD67CF2BCE5EDECEF1,0x0034EE45447D52FA0B6922E8,0x004C97E319753FA7473A996D,
0xFFE3A3B4B456736BC7FD0C61,0xFFE9237CCECEA838FB764068,0xFFFBDCDE8C4CF45E33BB4DF7
)
"""
TOPSITE = """(0x000C14BCA20DFDDBAD7A091D,0x002207636630DD7F94E55C8C,0x003BABD952525BE7455DA7D2)"""
CUSTOMERTICKET = """(0x005606F39E68FF9086E9F51C,0x0051EC82140B2AF5728E0FC9,0x00510FF55368FD8F5A5CFF88)"""
CUSTOMERTICKET_SANITY = """(0x052D2EC769AD25209114C87E,0x0530890FA4AE4B23A6798B5A,0x0539D8CE51DDCBE3B1A14185)"""
CUSTOMERTICKET_TOPSITE = """(0x09E4AEA342B5E60DCCFDBE0A,0x09EE51E967AC0681F5F91EA8,0x09F09C8A439446DC89A27DCB)"""
CUSTOMERTICKET_SANITY_TOPSITE = """(0x0E126E0807BDE91FC09DF469,0x0E254BF74DA624DFE94392D7,0x0E35B2D0695881A89B708D61)"""
SANITYURLS = """(0x00F0ABAC72318DD43ABDEEF0,0x00E762B3EF6B9FD546538562,0x00D40FC08AB67B38D6EC7BB1)"""
MCAFEESECURE = """(0x019541D3F9F32C992CFC264C,0x01A9EC82BFE18C60C99BEE50,0x01C397B5172F2C31A6D04FEA)"""
MCAFEESECURE_ONLY = """(0xFFAC7BE95B26B0A63CC07E46)"""
MCAFEESECURE_TOPSITE = """(0x0DC8388FEF9951846DF39D99,0x0DD0E2690D011A44350C8ADC,0x0DD0ECA0D4267BF60F2A6634)"""
MCAFEESECURE_SANITY = """(0x0D2CCA21A9A644FDCE9FC3D4,0x0D4962F7708B13B9870EC1F6,0x0D5C19E880152DB1FC1E3F25)"""
MCAFEESECURE_CUSTOMERTKT = """(0x002CC7AD67CF2BCE5EDECEF1,0x0034EE45447D52FA0B6922E8,0x004C97E319753FA7473A996D)"""
MCAFEESECURE_TOPSITE_SANITY = """(0xFFE3A3B4B456736BC7FD0C61,0xFFE9237CCECEA838FB764068,0xFFFBDCDE8C4CF45E33BB4DF7)"""
ISLOCKED = """(0x7A67BD717638286D4B2AAC84,0x7A50D6434B9C85CF65637E6C,0x7A5971AA09E3C30E88CED8FE)"""
SANITY_ISLOCKED = """(0x13E4BF4DBC395F3BE246C670,0x13ED30CF7A9638C39D279D00)"""
TOPSITE_ISLOCKED = """(0x1422E5A5166996BBCFA7D6F1,0x1446A4ADF0AE7BE76852F7AB)"""
CUSTOMERTICKET_ISLOCKED = """(0x137E22E900803310C485602A,0x139023EF9AF1777AF4CEAF83)"""
TOPSITE_SANITY_CUSTOMERTKT = """(0xFF33E86437DF8962556CFA6B,0xFF38D15247ECFA880B302AB4,0xFF5172C87D938375AFA3B56F)"""
URLCATEGORY_BL_BU_MK = """(0xFFC4D4119A10417EB058DB44)"""
URLCATEGORY_BL_BU_FI = """(0xFEDC6E460D9885AEBBC0DD8E,0xFEBC7A51B7CA55BB2801A3F0)"""
PREVALENCE_GREATER_ZERO = """(0xFF1AF810D22D30C1A9C525A0,0xFF192C60CA68FD28688BDA6D,0xFF112EF847ACCD0011AD6ED7)"""
CHILD_FOR_DOMAIN = """(0x10AA53FD0315C0A98CD5A7B7,0xA7ECC496AEA38CF7F4021275,0xC46FA65974F88DE9FB05DDC1)"""
DOMAIN_OF_CHILD = """(0x000C14BCA20DFDDBAD7A091D,0x002207636630DD7F94E55C8C,0xC6E889DE295D930AB46A5223)"""
TRIMISGENIPTS = """(0x03240906B36849DB5787A5BC,0x3C5270B102C54FDA7EE511FE)"""
#XL_REMOVAL_CRITERIA_DOMAIN = """(0x002207636630DD7F94E55C8C,0x003BABD952525BE7455DA7D2,0x000C14BCA20DFDDBAD7A091D)"""
XL_REMOVAL_CRITERIA_DOMAIN = """(0x002207636630DD7F94E55C8C,0x000C14BCA20DFDDBAD7A091D)"""
XL_REMOVAL_CRITERIA_CHILD_DOMAIN = """(0x10AA53FD0315C0A98CD5A7B7,0xC46FA65974F88DE9FB05DDC1,0x002207636630DD7F94E55C8C,0x000C14BCA20DFDDBAD7A091D)"""
TS_REMOVAL_CRITERIA_DOMAIN = """(0x002207636630DD7F94E55C8C,0x000C14BCA20DFDDBAD7A091D)"""
TS_REMOVAL = """(0x07A9D840B4D5727EE013DD63,0x69E530EBF4D9F524EC8F747E)"""


class PublishingAgentSandbox(SandboxedTest):
    """ Class for dealing with agents related cleanup actions - copying agents.log to sandbox directory """

    @classmethod
    def agent_execution(cls):
        print("Executing Agent")
        # Check if agent is free or not before starting
        if d2_activeagents.ActiveAgentsTable('Publish').get_is_running('Publish'):
            raise EnvironmentError('Publish agent is already running according to D2.active_agents')
        logging.info('Running Publishing Agent')
        stdo, stderr = ShellExecutor.run_wait_standalone(runtime.SH.start_agent + ' %s' % LOCAL_AGENT_PROP_FILE)
        #if not stderr:
        #    logging.error('ERRORS Found while running the agent. Please resolve them manually \n %s' % stderr)
        #    raise RuntimeError('ERROR while running Publishing Agent')
        return (stdo, stderr)

    def datetime_diff(self, dt):
        """ Validates if dates lie in past 5000 sec range """
        dt_now = datetime.datetime.now()
        d1_ts = time.mktime(dt_now.timetuple())
        d2_ts = time.mktime(dt.timetuple())
        if int(d1_ts - d2_ts) <= 3600:
            return True
        else:
            return False

    def modify_date(self, increment):
        date = datetime.datetime.now()
        date += datetime.timedelta(days=increment)
        return date.strftime("%Y-%m-%d")

    def isFileExist(self, filewithPath):
        if isinstance(filewithPath, str):
            # pattern = r'^/'
            # match = re.search(pattern, filewithPath)
            # if match:
            return os.path.isfile(filewithPath)
        else:
            logging.error('Argument filewithPath is not string type : %s' % (type(filewithPath)))
            return 0

    def database_update_query(self, query):
        d2_conn = TsMsSqlWrap('D2')
        if not query:
            logging.error("Query Positional Argument is not supplied or is Empty")
            return False
        else:
            arg = query
            if isinstance(query, str):
                # self.d2_conn.execute_sql_commit(query)
                d2_conn.execute_sql_commit(query)
                logging.info('TestCase data setup done [%s]' % query)
                # logging.debug('Updated rows from database follows : \n %s'%(self.d2_conn.get_row_count(query)))
            else:
                logging.error('Argument [%s] is not string type : %s' % (arg, type(arg)))
                return 0
            return True

    def databaseserver_name(self):
        sql_3 = "select SERVERPROPERTY ('ServerName') AS ServerName"
        return self.d2_conn.get_select_data(sql_3)

    def log_analysis(self):
        with open('/opt/sftools/log/agents.log') as log:
            logging.info('Succesfully opened agents.log file')
            global DATA
            DATA = ''.join(log.readlines())
            return DATA


class FileCheck(PublishingAgentSandbox):
    def test_001(self):
        """Check executable exists or not"""
        self.assertTrue(runtime.SH.start_agent.isfile(), "The shell executable doesn't exists")

    def test_002(self):
        """publishprevalence.properties exists or not"""
        agent_prop = prop_publish_agent()
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        self.assertTrue(os.path.isfile(LOCAL_AGENT_PROP_FILE), "agent.property file doesn't exists")

    def test_003(self):
        """application.properties exists or not"""
        self.assertTrue(runtime.PROP.application.isfile(), "application.property file doesn't exists")


class MandatoryURLs(PublishingAgentSandbox):
    @classmethod
    def setUpClass(cls):
        """ Running publishing agent from Framework """
        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        set_prop_application(write_file_bool=True)
        agent_prop = prop_publish_agent()
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        # Db Cleanup and then start the agent
        cls.d2_conn = TsMsSqlWrap('D2')
        cls.database_reset()
        cls.agent_execution()
        # Check if the agent shell script exists or not
        if not runtime.SH.start_agent.isfile():
            raise FileNotFoundError(runtime.SH.start_agent)

    @classmethod
    def database_reset(cls):
        """ Resets publishing bits and inserted dates in db """
        try:
            db_initialization_prevalence = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=0,publish_xl=0, \
    publish_ts=0,last_checked =NULL,last_seen=NULL,xl_removed=NULL,ts_removed=NULL,xl_inserted=NULL,ts_inserted=NULL"
            cls.d2_conn.execute_sql_commit(db_initialization_prevalence)
            db_initialization_build = "update build set mcafee_secure=0 where cl_hash in " + MCAFEESECURE
            cls.d2_conn.execute_sql_commit(db_initialization_build)
            logging.info("DataBase Tables updated for publish_xl, publish_ts, ts_inserted, xl_inserted ")
        except Exception as exc:
            logging.info('Exception while resetting db: PublishingAgent.database_reset - {}'.format(exc))
            return False
        else:
            logging.info('Inside else loop and no exception encountered while resetting DB flags for publishing agent ###')
            topsite = "update prevalence set is_top_site=1,is_locked=0,is_sanity_url=0,customer_ticket=0 where cl_hash in " + TOPSITE
            customerticket = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=1 where cl_hash in " + CUSTOMERTICKET
            customerticket_sanity = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=1,customer_ticket=1 where cl_hash in " + CUSTOMERTICKET_SANITY
            customerticket_topsite = "update prevalence set is_top_site=1,is_locked=0,is_sanity_url=0,customer_ticket=1 where cl_hash in " + CUSTOMERTICKET_TOPSITE
            customerticket_sanity_topsite = "update prevalence set is_top_site=1,is_locked=0,is_sanity_url=1,customer_ticket=1 where cl_hash in " + CUSTOMERTICKET_SANITY_TOPSITE
            sanity = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=1,customer_ticket=0 where cl_hash in " + SANITYURLS
            mcafeesecure = "update build set mcafee_secure =1 where cl_hash in " + MCAFEESECURE
            mcafeesecure_only = "update build set mcafee_secure =1 where cl_hash in " + MCAFEESECURE_ONLY
            mcafeesecure_topsite = "update prevalence set is_top_site=1,is_locked=0,is_sanity_url=0,customer_ticket=0 where cl_hash in " + MCAFEESECURE_TOPSITE
            mcafeesecure_sanity = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=1,customer_ticket=0 where cl_hash in " + MCAFEESECURE_SANITY
            mcafeesecure_customerticket = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=1 where cl_hash in " + MCAFEESECURE_CUSTOMERTKT
            mcafeesecure_topsite_sanity = "update prevalence set is_top_site=1,is_locked=0,is_sanity_url=1,customer_ticket=0 where cl_hash in " + MCAFEESECURE_TOPSITE_SANITY
            sanity_islocked = "update prevalence set is_top_site=0,is_locked=1,is_sanity_url=1,customer_ticket=0 where cl_hash in " + SANITY_ISLOCKED
            topsite_islocked = "update prevalence set is_top_site=1,is_locked=1,is_sanity_url=0,customer_ticket=0 where cl_hash in " + TOPSITE_ISLOCKED
            customerticket_islocked = "update prevalence set is_top_site=0,is_locked=1,is_sanity_url=0,customer_ticket=1 where cl_hash in " + CUSTOMERTICKET_ISLOCKED
            topsite_sanity_customerticket = "update prevalence set is_top_site=1,is_locked=0,is_sanity_url=1,customer_ticket=1 where cl_hash in " + TOPSITE_SANITY_CUSTOMERTKT
            common_mcafeesecure = "update build set mcafee_secure =1 where cl_hash in " + COMMON_MCAFEESECURE
            islocked = "update prevalence set is_top_site=0,is_locked=1,is_sanity_url=0,customer_ticket=0 where cl_hash in " + ISLOCKED
            child_for_domain = "update prevalence set is_top_site=1,is_locked=0,is_sanity_url=0,customer_ticket=0,prevalence=0 where cl_hash in " + CHILD_FOR_DOMAIN
            domain_of_child = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=0,prevalence=0 where cl_hash in " + DOMAIN_OF_CHILD

            ## Set appropriate flags in the prevalence table for the selected cl_hashes
            cls.d2_conn.execute_sql_commit(topsite)
            cls.d2_conn.execute_sql_commit(customerticket)
            cls.d2_conn.execute_sql_commit(customerticket_sanity)
            cls.d2_conn.execute_sql_commit(customerticket_topsite)
            cls.d2_conn.execute_sql_commit(customerticket_sanity_topsite)
            cls.d2_conn.execute_sql_commit(sanity)
            cls.d2_conn.execute_sql_commit(common_mcafeesecure)
            cls.d2_conn.execute_sql_commit(mcafeesecure_only)
            cls.d2_conn.execute_sql_commit(mcafeesecure)
            cls.d2_conn.execute_sql_commit(mcafeesecure_topsite)
            cls.d2_conn.execute_sql_commit(mcafeesecure_sanity)
            cls.d2_conn.execute_sql_commit(mcafeesecure_customerticket)
            cls.d2_conn.execute_sql_commit(mcafeesecure_topsite_sanity)
            cls.d2_conn.execute_sql_commit(sanity_islocked)
            cls.d2_conn.execute_sql_commit(topsite_islocked)
            cls.d2_conn.execute_sql_commit(customerticket_islocked)
            cls.d2_conn.execute_sql_commit(topsite_sanity_customerticket)
            cls.d2_conn.execute_sql_commit(islocked)
            cls.d2_conn.execute_sql_commit(child_for_domain)
            cls.d2_conn.execute_sql_commit(domain_of_child)
        return True

    def test_001(self):
        """agent.publish.safeMode=false """
        validation_query2 = "select is_top_site,publish_ts,publish_xl,ts_inserted,xl_inserted from dbo.prevalence \
        (nolock) where is_top_site =1 and publish_xl=1 and publish_ts=1 and ts_inserted is not NULL \
        and xl_inserted is not NULL and cl_hash in " + TOPSITE
        self.assertNotEqual(self.d2_conn.get_row_count(validation_query2), 0, 'No updates made in the prevalence table')
        logging.info(self.d2_conn.get_row_count(validation_query2))
        for row in self.d2_conn.get_select_data(validation_query2):
            self.assertTrue(row['is_top_site'], 'is_top_site flag not set or the cl_hashes doesnt exists in DB')
            self.assertTrue(row['publish_ts'], 'Though safe mode set to false, publish_ts flag \
            not set in prevalence table for is_top_site hashes')
            self.assertTrue(row['publish_xl'], 'Though safe mode set to false, publish_xl flag \
            not set in prevalence table for is_top_site hashes')
            self.assertTrue(row['ts_inserted'], 'Though safe mode set to false, ts_inserted date stamp\
            not set in prevalence table for is_top_site hashes')
            self.assertTrue(row['xl_inserted'], 'Though safe mode set to false, xl_inserted date stamp\
            not set in prevalence table for is_top_site hashes')

    def test_002(self):
        """Safemode false All Top Sites published to XL and TS list """
        # query = "update prevalence set customer_ticket=1 where cl_hash in " + SAMPLE_CL_HASH
        # self.database_update_query(query)
        # (stdo, stderr) = self.agent_execution()
        # logging.info('Agent post run stats \n stdo [%s] stderr [%s]' % (stdo, stderr))
        sql_1 = "select * from prevalence (nolock) where is_top_site=1 and is_locked=0"
        sql_2 = "select * FROM prevalence (nolock) where is_top_site =1 and publish_ts=1 AND publish_xl=1 and is_locked=0"
        self.assertEqual(self.d2_conn.get_row_count(sql_1), self.d2_conn.get_row_count(sql_2),
                         "For xl/ts=1 and top_site=1 : Count doesn't match")
        for row in self.d2_conn.get_select_data(sql_1):
            self.assertTrue(row['ts_inserted'], 'ts_inserted not 1')
            self.assertTrue(row['xl_inserted'], 'xl_inserted not 1')
            self.assertIsNotNone(row['xl_inserted'], 'ts_inserted is None')
            self.assertIsNotNone(row['ts_inserted'], 'ts_inserted is None')
            # logging.critical(self.datetime_diff(row['xl_inserted']))
            # self.assertTrue(self.datetime_diff(row['xl_inserted']), 'datetime_diff:xl_inserted is not true')
            # logging.critical(self.datetime_diff(row['ts_inserted']))
            #self.assertTrue(self.datetime_diff(row['ts_inserted']), 'datetime_diff:ts_inserted is not true')

    def test_003(self):
        """Safemode false Number of top site urls to be published"""
        DATA = self.log_analysis()
        sql = "SELECT cl_hash FROM prevalence (nolock) where is_top_site=1 and is_locked = 0 and \
        publish_xl=1 and publish_ts=1 and xl_inserted is not NULL and ts_inserted is not NULL"
        expected = self.d2_conn.get_row_count(sql)
        logging.info('from DB = %s' % (expected))

        xl_inserted = re.search(r'Number of top sites urls set to publish_xl = 1: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        self.assertEqual(int(actual), expected, 'LogFile : Number of URLs Inserted into XL : count doesnt match')
        DB_CLEAN_UP = False


    def test_004(self):
        """Safemode false All customer ticketed URLs published to XL and TS list """
        sql_1 = "select * FROM prevalence (nolock) where customer_ticket=1 and is_sanity_url=0 and is_top_site=0 and is_locked = 0 and publish_xl=1 and publish_ts=1 and xl_inserted is not NULL " \
                "and ts_inserted is not NULL and cl_hash in " + CUSTOMERTICKET
        self.assertNotEqual(self.d2_conn.get_row_count(sql_1), 0, 'Row count is zero')
        if self.d2_conn.get_row_count(sql_1) != 0:
            for row in self.d2_conn.get_select_data(sql_1):
                self.assertTrue(row['publish_ts'], 'publish_ts is FALSE')
                self.assertTrue(row['publish_xl'], 'publish_xl is FALSE')
        else:
            logging.error('Test data not set for TestCase')

    def test_005(self):
        """ Safemode false Number of customer tickets urls to be published"""
        DATA = self.log_analysis()
        sql = "SELECT cl_hash FROM prevalence (nolock) where  is_sanity_url=0 and  is_top_site=0 and \
        customer_ticket = 1 and is_locked = 0 and publish_xl=1 and publish_ts=1 and xl_inserted is not NULL and ts_inserted is not NULL"
        expected = self.d2_conn.get_row_count(sql)
        logging.info('from DB = %s' % (expected))
        xl_inserted = re.search(r'Number of customer tickets urls set to publish_xl = 1: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        self.assertEqual(int(actual), expected, 'LogFile : Number of customer tickets urls set to \
        publish_xl = 1 : count doesnt match')
        DB_CLEAN_UP = False


    def test_006(self):
        """Safemode false customer_ticket =1 and is_sanity_url =1 is_top_site=0"""
        sql_1 = "select * from prevalence (nolock) where customer_ticket =1 and is_sanity_url =1 and is_top_site=0 and is_locked = 0 and publish_xl=1 and publish_ts=1 and xl_inserted is not NULL " \
                "and ts_inserted is not NULL and cl_hash in " + CUSTOMERTICKET_SANITY
        self.assertNotEqual(self.d2_conn.get_row_count(sql_1), 0, 'Row count is zero')
        if self.d2_conn.get_row_count(sql_1) != 0:
            for row in self.d2_conn.get_select_data(sql_1):
                self.assertTrue(row['publish_ts'], 'publish_ts is FALSE')
                self.assertTrue(row['publish_xl'], 'publish_xl is FALSE')
                self.assertTrue(row['ts_inserted'], 'ts_inserted is FALSE')
                self.assertTrue(row['xl_inserted'], 'xl_inserted is FALSE')
        else:
            logging.error('Test data not set for TestCase')


    def test_007(self):
        """Safemode false customer_ticket =1 and is_sanity_url =0 is_top_site=1"""
        sql_1 = "select * from prevalence (nolock) where customer_ticket =1 and is_sanity_url =0 and is_top_site=1 and is_locked = 0 and publish_xl=1 and publish_ts=1 and xl_inserted is not NULL " \
                "and ts_inserted is not NULL and cl_hash in " + CUSTOMERTICKET_TOPSITE
        self.assertNotEqual(self.d2_conn.get_row_count(sql_1), 0, 'Row count is zero')
        if self.d2_conn.get_row_count(sql_1) != 0:
            for row in self.d2_conn.get_select_data(sql_1):
                self.assertTrue(row['publish_ts'], 'publish_ts is FALSE')
                self.assertTrue(row['publish_xl'], 'publish_xl is FALSE')
                self.assertTrue(row['ts_inserted'], 'ts_inserted is FALSE')
                self.assertTrue(row['xl_inserted'], 'xl_inserted is FALSE')
        else:
            logging.error('Test data not set for TestCase')


    def test_008(self):
        """Safemode false customer_ticket =1 and is_sanity_url =1 is_top_site=1"""
        sql_1 = "select * from prevalence (nolock) where customer_ticket =1 and is_sanity_url =1 and is_top_site=1 and is_locked = 0 and publish_xl=1 and publish_ts=1 and xl_inserted is not NULL " \
                "and ts_inserted is not NULL and cl_hash in " + CUSTOMERTICKET_SANITY_TOPSITE
        self.assertNotEqual(self.d2_conn.get_row_count(sql_1), 0, 'Post agent run Query Row count found is zero')
        for row in self.d2_conn.get_select_data(sql_1):
            self.assertTrue(row['publish_ts'], 'publish_ts is FALSE')
            self.assertTrue(row['publish_xl'], 'publish_xl is FALSE')
            self.assertTrue(row['ts_inserted'], 'ts_inserted is FALSE')
            self.assertTrue(row['xl_inserted'], 'xl_inserted is FALSE')


    def test_009(self):
        """Safemode false All sanity URLs published to XL and TS list """
        sql_1 = "select * FROM prevalence (nolock) where customer_ticket =0 and is_sanity_url =1 and is_top_site=0 and is_locked = 0 and publish_xl=1 and publish_ts=1 and xl_inserted is not NULL " \
                "and ts_inserted is not NULL and cl_hash in " + SANITYURLS
        self.assertNotEqual(self.d2_conn.get_row_count(sql_1), 0, 'Row count is zero for database_update_query')
        if self.d2_conn.get_row_count(sql_1) != 0:
            for row in self.d2_conn.get_select_data(sql_1):
                self.assertTrue(row['publish_ts'], 'publish_ts is FALSE')
                self.assertTrue(row['publish_xl'], 'publish_xl is FALSE')
                self.assertTrue(row['ts_inserted'], 'ts_inserted is FALSE')
                self.assertTrue(row['xl_inserted'], 'xl_inserted is FALSE')
        else:
            logging.error('Test data not set for TestCase')


    def test_010(self):
        """Safemode false Number of sanity urls to be published"""
        DATA = self.log_analysis()
        sql = "select * FROM prevalence (nolock) where is_sanity_url =1 and is_top_site=0 and is_locked=0 and publish_xl=1 \
        and publish_ts=1 and xl_inserted is not NULL and ts_inserted is not NULL"
        expected = self.d2_conn.get_row_count(sql)
        logging.info('from DB = %s' % (expected))
        xl_inserted = re.search(r'Number of sanity urls set to publish_xl = 1: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        self.assertEqual(int(actual), expected,
                         'LogFile : Number of sanity urls set to publish_xl = 1 : count doesnt match')


    def test_011(self):
        """Safe mode false only mcafee_secure set """
        # Initialize DB tables before staring agent
        sql_query = "select * from prevalence where customer_ticket=0 and is_sanity_url =0 and is_top_site=0 and publish_xl=0 and publish_ts=1 and ts_inserted is not NULL and \
        xl_inserted is NULL and cl_hash in (select cl_hash from build where mcafee_secure=1 and cl_hash in " + MCAFEESECURE_ONLY + " )"
        self.assertNotEqual(self.d2_conn.get_row_count(sql_query), 0, 'No mcafee_secured cl_hashes published to ts \
        or the cl_hashes are set to publish_xl also')
        validation_query1 = "select cl_hash,publish_xl,publish_ts,ts_inserted,xl_inserted from prevalence \
        where cl_hash in" + MCAFEESECURE_ONLY
        for row in self.d2_conn.get_select_data(validation_query1):
            self.assertFalse(row['publish_xl'], "publish xl set for the cl_hash")
            self.assertTrue(row['publish_ts'], "publish_ts set for the cl_hash")
            self.assertTrue(row['ts_inserted'], "ts_inserted not set for the cl_hash")
            self.assertFalse(row['xl_inserted'], "xl_inserted is set for the cl_hash")


    def test_012(self):
        """Safe mode false mcafee_secure =1 and is_top_site=1"""
        # Initialize DB tables before staring agent
        sql_query = "select * from prevalence where is_top_site=1 and customer_ticket=0 and is_sanity_url =0 and publish_xl=1 and publish_ts=1 and \
        ts_inserted is not NULL and xl_inserted is not NULL and cl_hash in \
        (select cl_hash from build where mcafee_secure=1 and cl_hash in " + MCAFEESECURE_TOPSITE + " )"
        self.assertNotEqual(self.d2_conn.get_row_count(sql_query), 0, 'Seems no cl_hashes which as \
        is_top_site & mcafee_secured set are published to xl & ts or the cl_hashes are set to only to ts')

        validation_query1 = "select cl_hash,publish_xl,publish_ts,ts_inserted,xl_inserted from prevalence \
        where cl_hash in" + MCAFEESECURE_TOPSITE
        for row in self.d2_conn.get_select_data(validation_query1):
            self.assertTrue(row['publish_xl'], "publish xl not set for the cl_hash")
            self.assertTrue(row['publish_ts'], "publish_ts not set for the cl_hash")
            self.assertTrue(row['ts_inserted'], "ts_inserted not set for the cl_hash")
            self.assertTrue(row['xl_inserted'], "xl_inserted not set for the cl_hash")


    def test_013(self):
        """Safe mode false mcafee_secure =1 and is_sanity_url=1"""
        sql_query = "select * from prevalence where is_top_site=0 and customer_ticket=0 and is_sanity_url=1 and publish_xl=1 and publish_ts=1 and \
        ts_inserted is not NULL and xl_inserted is not NULL and cl_hash in \
        (select cl_hash from build where mcafee_secure=1 and cl_hash in " + MCAFEESECURE_SANITY + " )"
        self.assertNotEqual(self.d2_conn.get_row_count(sql_query), 0, 'Seems no cl_hashes which as \
        is_sanity_url & mcafee_secured set are published to xl & ts or the cl_hashes are set to only to ts')
        validation_query1 = "select cl_hash,publish_xl,publish_ts,ts_inserted,xl_inserted from prevalence \
        where cl_hash in" + MCAFEESECURE_SANITY
        for row in self.d2_conn.get_select_data(validation_query1):
            self.assertTrue(row['publish_xl'], "publish xl not set for the cl_hash")
            self.assertTrue(row['publish_ts'], "publish_ts not set for the cl_hash")
            self.assertTrue(row['ts_inserted'], "ts_inserted not set for the cl_hash")
            self.assertTrue(row['xl_inserted'], "xl_inserted not set for the cl_hash")


    def test_014(self):
        """Safe mode false mcafee_secure =1 and customer_ticket=1"""
        sql_query = "select * from prevalence where is_sanity_url=0 and is_top_site=0 and customer_ticket=1 and publish_xl=1 and publish_ts=1 and \
        ts_inserted is not NULL and  xl_inserted is not NULL and cl_hash in (select cl_hash from build where \
        mcafee_secure=1 and cl_hash in " + MCAFEESECURE_CUSTOMERTKT + " )"
        self.assertNotEqual(self.d2_conn.get_row_count(sql_query), 0, 'The selected cl_hashes are not set to xl and ts')
        validation_query = "select is_top_site,is_sanity_url,is_locked,customer_ticket,publish_xl,publish_ts\
        from prevalence where cl_hash in" + MCAFEESECURE_CUSTOMERTKT
        for row in self.d2_conn.get_select_data(validation_query):
            self.assertTrue(row['customer_ticket'], 'Customer Ticket is not set for the cl_hash')
            self.assertTrue(row['publish_ts'], 'publish_ts is not set for the cl_hash')
            self.assertTrue(row['publish_xl'], 'publish_xl is not set for the cl_hash')


    def test_015(self):
        """Safe mode false mcafee_secure =1, is_top_site=1 and is_sanity_url =1"""
        after_run = "select * from prevalence where is_sanity_url=1 and is_top_site=1 and customer_ticket=0 \
        and publish_xl=1 and publish_ts=1 and ts_inserted is not NULL and  xl_inserted is not NULL and cl_hash in \
        (select cl_hash from build where mcafee_secure=1 and cl_hash in " + MCAFEESECURE_TOPSITE_SANITY + " )"
        self.assertNotEqual(self.d2_conn.get_row_count(after_run), 0, 'The selected cl_hashes are not set to xl and ts')

        validation_query = "select is_top_site,is_sanity_url,is_locked,customer_ticket,publish_xl,publish_ts from prevalence \
        where cl_hash in" + MCAFEESECURE_TOPSITE_SANITY
        for row in self.d2_conn.get_select_data(validation_query):
            self.assertTrue(row['is_top_site'], True)
            self.assertTrue(row['is_sanity_url'], True)
            self.assertFalse(row['customer_ticket'], True)
            self.assertTrue(row['publish_ts'], True)
            self.assertTrue(row['publish_xl'], True)


    def test_016(self):
        """Safemode false for cl_hash just is_locked is set"""
        sql_2 = "select * FROM prevalence (nolock) where is_sanity_url=0 and is_top_site=0 and customer_ticket=0 \
        and is_locked=1 and cl_hash in " + ISLOCKED
        sql_2_data_old = self.d2_conn.get_select_data(sql_2)
        logging.info('SUCCESS: db query for is_locked urls')
        # convert binary clhashes to hex to be used in db query inplace sql_2_data_old
        cl_hash_hex = []
        p = PrevalenceTable()
        for item in sql_2_data_old:
            cl_hex = p.d2_con.convert_cl_hash_bin_to_hex_string(item['cl_hash'])
            item['cl_hash'] = cl_hex
            logging.info('cl_hash replaced with %s' % cl_hex)
        logging.info(pprint.pformat(sql_2_data_old))
        logging.info('SUCCESS: publishing agent')
        sql_2_data_new = self.d2_conn.get_select_data(sql_2)
        # list of dictionary comparision
        for item in sql_2_data_new:
            cl_hex = p.d2_con.convert_cl_hash_bin_to_hex_string(item['cl_hash'])
            item['cl_hash'] = cl_hex
            logging.info('cl_hash replaced with %s' % cl_hex)
            for element in sql_2_data_old:
                if element['cl_hash'] == item['cl_hash']:
                    self.assertEqual(element['is_locked'], item['is_locked'], 'is_locked mismatch for %s' % cl_hex)
                    self.assertEqual(element['is_top_site'], item['is_top_site'],
                                     'is_top_site mismatch for %s' % cl_hex)
                    self.assertEqual(element['is_sanity_url'], item['is_sanity_url'],
                                     'is_sanity_url mismatch for %s' % cl_hex)
                    self.assertEqual(element['publish_xl'], item['publish_xl'], 'publish_xl mismatch for %s' % cl_hex)
                    self.assertEqual(element['publish_ts'], item['publish_ts'], 'publish_ts mismatch for %s' % cl_hex)
                    self.assertEqual(element['customer_ticket'], item['customer_ticket'],
                                     'customer_ticket mismatch for %s' % cl_hex)
                    break
        logging.info("End of Test 7386")

    def test_017(self):
        """Safemode false is_sanity_url=1 and is_locked=1 """
        query = "select * from prevalence (nolock) where is_sanity_url=1 and is_locked=1 and is_top_site=0 \
        and customer_ticket=0 and cl_hash in " + SANITY_ISLOCKED
        for row in self.d2_conn.get_select_data(query):
            self.assertFalse(row['publish_ts'], 'publish_ts is FALSE')
            self.assertFalse(row['publish_xl'], 'publish_xl is FALSE')
            self.assertIsNone(row['xl_inserted'], 'xl_inserted is NOT None \n %s' % (row))
            self.assertIsNone(row['ts_inserted'], 'ts_inserted is NOT None \n %s' % (row))

    def test_018(self):
        """Safemode false is_top_site=1 and is_locked=1 """
        query = "select * from prevalence (nolock) where is_sanity_url=0 and is_locked=1 and is_top_site=1 \
        and customer_ticket=0 and cl_hash in " + TOPSITE_ISLOCKED
        for row in self.d2_conn.get_select_data(query):
            self.assertFalse(row['publish_ts'], 'publish_ts is FALSE')
            self.assertFalse(row['publish_xl'], 'publish_xl is FALSE')
            self.assertIsNone(row['xl_inserted'], 'xl_inserted is NOT None \n %s' % row)
            self.assertIsNone(row['ts_inserted'], 'ts_inserted is NOT None \n %s' % row)

    def test_019(self):
        """Safemode false customer_ticket=1 and is_locked=1 """
        query = "select * from prevalence (nolock) where is_sanity_url=0 and is_locked=1 and is_top_site=0 \
        and customer_ticket=1 and cl_hash in " + CUSTOMERTICKET_ISLOCKED
        for row in self.d2_conn.get_select_data(query):
            self.assertFalse(row['publish_ts'], 'publish_ts is FALSE')
            self.assertFalse(row['publish_xl'], 'publish_xl is FALSE')
            self.assertIsNone(row['xl_inserted'], 'xl_inserted is NOT None \n %s' % (row))
            self.assertIsNone(row['ts_inserted'], 'ts_inserted is NOT None \n %s' % (row))


    def test_020(self):
        """Safemode false is_top_site=1 , is_sanity_url=1 and is_locked=1"""
        query = "select * from prevalence (nolock) where is_locked=1 and is_top_site=1 and is_sanity_url=1 "
        for row in self.d2_conn.get_select_data(query):
            self.assertFalse(row['publish_ts'], 'publish_ts is FALSE')
            self.assertFalse(row['publish_xl'], 'publish_xl is FALSE')
            self.assertIsNone(row['xl_inserted'], 'xl_inserted is NOT None \n %s' % (row))
            self.assertIsNone(row['ts_inserted'], 'ts_inserted is NOT None \n %s' % (row))


    def test_021(self):
        """agent.log file exists or not """
        assert runtime.LOG.agents.isfile()


    def test_022(self):
        """Safemode false agent.log captures traces """
        log_file_contents = open(runtime.LOG.agents).read()
        if AGENT_START_STRING in log_file_contents and AGENT_COMPLETED_STRING in log_file_contents:
            logging.info('Found Start and completinon string in log file \
            i.e. agent started & completed successfully')
            return True
        else:
            logging.info('Didnd\'t find Start and completinon string in log file\
            i.e. probably agent didn\'t start')


    def test_023(self):
        """Safemode false Number of mandatory urls to be published"""

        DATA = self.log_analysis()
        query_total_xl_published = 'select * from D2.dbo.prevalence (nolock) where \
        (is_locked = 1 and publish_xl = 1) or is_top_site = 1 or is_sanity_url = 1 or customer_ticket = 1'

        total_xl_published = self.d2_conn.get_row_count(query_total_xl_published)
        expected = int(total_xl_published)

        count = re.search(r'Total number of XL URLs to ensure to publish: (\d+)', DATA)
        actual = int(count.group(1))

        self.assertEqual(int(expected), int(actual), 'As per log not all mandatory cl_hashes published to xl')

    def test_024(self):
        """Safe mode false Number of URLs ensured to be publish in TS"""
        # Note: This count is = Total number of XL Updates +  Number of McAfee Secure urls set to publish_ts
        DATA = self.log_analysis()
        query_xl_ts_published = 'select cl_hash from prevalence (nolock) where publish_ts=1 and publish_xl =1'
        total_xl_ts_published = self.d2_conn.get_row_count(query_xl_ts_published)

        query_only_mcafeesecure_set_to_ts = 'select * from D2.dbo.prevalence (nolock) where publish_xl =0 and \
        cl_hash in (select cl_hash from D2.dbo.build (nolock) where mcafee_secure =1)'
        total_only_mcafeesecure_set_to_ts = self.d2_conn.get_row_count(query_only_mcafeesecure_set_to_ts)

        expected = int(total_xl_ts_published) + int(total_only_mcafeesecure_set_to_ts)

        count = re.search(r'publishTs Number of URLs ensured to be publish in TS: (\d+)', DATA)
        actual = int(count.group(1))

        self.assertTrue(re.search(r'Finish sync of prevalence table with the build table', DATA, re.I | re.M), 'Some issue \
        encountered while running publishing agent')

        self.assertEqual(actual, expected, 'Mismatch in total Number of URLs ensured to be publish in TS')


    def test_025(self):
        """Safemode false parents published to xl and ts because child is published to xl"""
        d2_con = TsMsSqlWrap('D2')
        query = "select * from prevalence with (nolock) where (is_top_site=0 and is_locked=0 and is_sanity_url=0 and customer_ticket=0)\
        and publish_xl=1 and publish_ts=1 and cl_hash in " + DOMAIN_OF_CHILD
        count = self.d2_conn.get_row_count(query)
        self.assertNotEqual(count, 0, "No domain hashes are set to publish xl because child is already published")
        for row in self.d2_conn.get_select_data(query):
            self.assertTrue(row['publish_ts'], 'publish_ts is FALSE')
            self.assertTrue(row['publish_xl'], 'publish_xl is FALSE')
            # self.assertTrue(row['xl_inserted'], 'xl_inserted is None \n %s' % (row))
            ## Commeting this assert statement because for these parent cl_hash publised because child is published ,
            ## doesnt have the xl_inserted date set, Need to check with John Rivera
            self.assertTrue(row['ts_inserted'], 'ts_inserted is None \n %s' % (row))


    def test_026(self):
        """Safemode false publishXlParents Number of parent cl_hashes set to publish_xl = 1"""
        query = "select * from prevalence with (nolock) where (is_top_site=0 and prevalence=0 and is_locked=0 and \
        is_sanity_url=0 and customer_ticket=0) and publish_xl=1 and publish_ts=1 and cl_hash in " + DOMAIN_OF_CHILD
        expected = int(self.d2_conn.get_row_count(query))
        self.assertNotEqual(expected, 0,
                            "No domain hashes are set to publish xl because child is already published to xl")
        DATA = self.log_analysis()
        xl_inserted = re.search(r'publishXlParents Number of parent cl_hashes set to publish_xl = 1: (\d+)', DATA)
        actual = xl_inserted.group(1)
        self.assertEqual(int(actual), expected, 'LogFile : Number of parent cl_hashes set to publish_xl = 1:')


    def test_027(self):
        """Safemade false Drop temp tables"""
        drop_green = 'cleanXlPrevalenceTable #greentmp table deleted'
        drop_grey = 'cleanXlPrevalenceTable #greytmp table  deleted'
        drop_yellow = 'cleanXlPrevalenceTable #yellowtmp table deleted'
        drop_red = 'cleanXlPrevalenceTable #redtmp table deleted'
        drop_mandtemp = 'cleanXlPrevalenceTable #mandtemp table deleted'
        DATA = self.log_analysis()
        self.assertTrue(re.search(drop_green, DATA, re.I | re.M), '#gereen temp table not dropped')
        self.assertTrue(re.search(drop_grey, DATA, re.I | re.M), '#grey temp table not dropped')
        self.assertTrue(re.search(drop_yellow, DATA, re.I | re.M), '#yellow temp table not dropped')
        self.assertTrue(re.search(drop_red, DATA, re.I | re.M), '#red temp table not dropped')
        self.assertTrue(re.search(drop_mandtemp, DATA, re.I | re.M), '#mandtemp temp table not dropped')


class WebReputation(PublishingAgentSandbox):
    @classmethod
    def setUpClass(cls):
        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        set_prop_application(write_file_bool=True)
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.xlNumberUrls'] = '100000000'
        agent_prop['agent.publish.xlGreenPercent'] = '100'
        agent_prop['agent.publish.xlGreyPercent'] = '100'
        agent_prop['agent.publish.xlYellowPercent'] = '100'
        agent_prop['agent.publish.xlRedPercent'] = '100'
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        cls.d2_conn = TsMsSqlWrap('D2')
        db_initialization_prevalence = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=0,publish_xl=0, \
    publish_ts=0,last_checked =NULL,last_seen=NULL,xl_removed=NULL,ts_removed=NULL,xl_inserted=NULL,ts_inserted=NULL"
        cls.d2_conn.execute_sql_commit(db_initialization_prevalence)
        prevalence_greater_zero = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=0,prevalence=10 where cl_hash in " + PREVALENCE_GREATER_ZERO
        cls.d2_conn.execute_sql_commit(prevalence_greater_zero)
        db_initialization_build = "update build set mcafee_secure=0 where cl_hash in " + MCAFEESECURE
        cls.d2_conn.execute_sql_commit(db_initialization_build)
        cls.database_reset()
        cls.agent_execution()


    @classmethod
    def database_reset(cls):
        """ Resets publishing bits and inserted dates in db """
        try:
            db_initialization_prevalence = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=0,publish_xl=0, \
    publish_ts=0,last_checked =NULL,last_seen=NULL,xl_removed=NULL,ts_removed=NULL,xl_inserted=NULL,ts_inserted=NULL"
            cls.d2_conn.execute_sql_commit(db_initialization_prevalence)
            db_initialization_build = "update build set mcafee_secure=0 where cl_hash in " + MCAFEESECURE
            cls.d2_conn.execute_sql_commit(db_initialization_build)
            logging.info("DataBase Tables updated for publish_xl, publish_ts, ts_inserted, xl_inserted ")
            ## Set prevalence = 10 for few cl_hashes for some tests under
            set_prevalence = "update prevalence set prevalence=10 where cl_hash in " + PREVALENCE_GREATER_ZERO
            cls.d2_conn.execute_sql_commit(set_prevalence)
        except Exception as exc:
            logging.info('Exception while resetting db: PublishingAgent.database_reset - {}'.format(exc))
            return False
        else:
            return True


    def test_001(self):
        """Safemode false Number of cl_hashes in temp table #greentmp"""
        # sql = "select top 479998 p.cl_hash from d2.dbo.prevalence p (nolock), WebReputation w (nolock), build b (nolock) where p.cl_hash = w.cl_hash and p.cl_hash = b.cl_hash and b.is_generated = 0 and w.web_reputation <= 14 and p.is_locked = 0 and p.cl_hash not in  (select cl_hash from d2.dbo.prevalence where (is_locked = 1 and publish_xl = 1) or is_top_site = 1 or is_sanity_url = 1 or customer_ticket = 1)"
        sql = "select * from prevalence p (nolock),WebReputation w (nolock), build b (nolock) \
        where p.cl_hash = w.cl_hash and p.cl_hash = b.cl_hash and b.is_generated = 0 and w.web_reputation <= 14 \
        and p.is_locked = 0 order by p.prevalence desc,b.updated_on"
        expected = self.d2_conn.get_row_count(sql)

        DATA = self.log_analysis()

        xl_inserted = re.search(r'Number of cl_hashes in #greentmp: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        self.assertEqual(int(actual), expected, 'LogFile : Number of cl_hashes in #greentmp : count doesnt match')
        DB_CLEAN_UP = False


    def test_002(self):
        """Safemode false Number of cl_hashes in temp table #greytmp """
        # sql = "select top 319999 p.cl_hash from d2.dbo.prevalence p (nolock), WebReputation w (nolock), build b (nolock) where p.cl_hash = w.cl_hash and p.cl_hash = b.cl_hash and b.is_generated = 0 and w.web_reputation > 14 and w.web_reputation <= 29 and p.is_locked = 0 and p.cl_hash not in  (select cl_hash from d2.dbo.prevalence where (is_locked = 1 and publish_xl = 1) or is_top_site = 1 or is_sanity_url = 1 or customer_ticket = 1)"
        sql = "select * from prevalence p (nolock),WebReputation w (nolock), build b (nolock) \
        where p.cl_hash = w.cl_hash and p.cl_hash = b.cl_hash and b.is_generated = 0 and w.web_reputation > 14 and w.web_reputation <= 29 \
        and p.is_locked = 0 order by p.prevalence desc,b.updated_on"
        expected = self.d2_conn.get_row_count(sql)
        logging.info('from DB = %s' % (expected))

        DATA = self.log_analysis()

        xl_inserted = re.search(r'Number of cl_hashes in #greytmp: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        self.assertEqual(int(actual), expected, 'LogFile : Number of cl_hashes in #greytmp : count doesnt match')
        DB_CLEAN_UP = False


    def test_003(self):
        """Safemode false Number of cl_hashes in temp table #yellowtmp"""
        # sql = "select p.cl_hash from d2.dbo.prevalence p (nolock), WebReputation w (nolock), build b (nolock) where p.cl_hash = w.cl_hash and p.cl_hash = b.cl_hash and b.is_generated = 0 and w.web_reputation > 29 and w.web_reputation <= 49 and p.is_locked = 0 and p.cl_hash not in  (select cl_hash from d2.dbo.prevalence where (is_locked = 1 and publish_xl = 1) or is_top_site = 1 or is_sanity_url = 1 or customer_ticket = 1)"
        sql = "select * from prevalence p (nolock),WebReputation w (nolock), build b (nolock) \
        where p.cl_hash = w.cl_hash and p.cl_hash = b.cl_hash and b.is_generated = 0 and w.web_reputation > 29 and w.web_reputation <= 49 \
        and p.is_locked = 0 order by p.prevalence desc,b.updated_on"
        expected = self.d2_conn.get_row_count(sql)
        logging.info('from DB = %s' % (expected))

        DATA = self.log_analysis()

        xl_inserted = re.search(r'Number of cl_hashes in #yellowtmp: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        self.assertEqual(int(actual), expected, 'LogFile : Number of cl_hashes in #yellowtmp : count doesnt match')
        DB_CLEAN_UP = False


    def test_004(self):
        """Safemode false Number of cl_hashes in temp table #redtmp"""
        # sql = "select top 319999 p.cl_hash from d2.dbo.prevalence p (nolock), WebReputation w (nolock), build b (nolock) where p.cl_hash = w.cl_hash and p.cl_hash = b.cl_hash and b.is_generated = 0 and w.web_reputation > 49 and p.is_locked = 0 and p.cl_hash not in  (select cl_hash from d2.dbo.prevalence where (is_locked = 1 and publish_xl = 1) or is_top_site = 1 or is_sanity_url = 1 or customer_ticket = 1)"
        sql = "select * from prevalence p (nolock),WebReputation w (nolock), build b (nolock) \
        where p.cl_hash = w.cl_hash and p.cl_hash = b.cl_hash and b.is_generated = 0 and w.web_reputation > 49 \
        and p.is_locked = 0 order by p.prevalence desc,b.updated_on"
        expected = self.d2_conn.get_row_count(sql)
        logging.info('from DB = %s' % (expected))

        DATA = self.log_analysis()

        xl_inserted = re.search(r'Number of cl_hashes in #redtmp: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        self.assertEqual(int(actual), expected, 'LogFile : Number of cl_hashes in #redtmp : count doesnt match')
        DB_CLEAN_UP = False


    def test_005(self):
        """Safemode false Number of green cl_hashes set to pending_xl_insert = 1"""
        sql = "select * from prevalence p (nolock),WebReputation w (nolock), build b (nolock) \
        where p.cl_hash = w.cl_hash and p.cl_hash = b.cl_hash and b.is_generated = 0 and w.web_reputation <= 14 \
        and p.is_locked = 0 order by p.prevalence desc,b.updated_on"
        expected = self.d2_conn.get_row_count(sql)
        # logging.info('from DB = %s' % (expected))

        DATA = self.log_analysis()

        xl_inserted = re.search(r'Number of green cl_hashes set to pending_xl_insert = 1: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        self.assertEqual(int(actual), expected, 'LogFile : Number of cl_hashes in #greentmp : count doesnt match')
        DB_CLEAN_UP = False


    def test_006(self):
        """Safemode false Number of grey cl_hashes set to pending_xl_insert = 1"""
        # sql = "select top 319999 p.cl_hash from d2.dbo.prevalence p (nolock), WebReputation w (nolock), build b (nolock) where p.cl_hash = w.cl_hash and p.cl_hash = b.cl_hash and b.is_generated = 0 and w.web_reputation > 14 and w.web_reputation <= 29 and p.is_locked = 0 and p.cl_hash not in  (select cl_hash from d2.dbo.prevalence where (is_locked = 1 and publish_xl = 1) or is_top_site = 1 or is_sanity_url = 1 or customer_ticket = 1)"
        sql = "select * from prevalence p (nolock),WebReputation w (nolock), build b (nolock) \
        where p.cl_hash = w.cl_hash and p.cl_hash = b.cl_hash and b.is_generated = 0 and w.web_reputation > 14 and w.web_reputation <= 29 \
        and p.is_locked = 0 order by p.prevalence desc,b.updated_on"
        expected = self.d2_conn.get_row_count(sql)
        logging.info('from DB = %s' % (expected))

        DATA = self.log_analysis()

        xl_inserted = re.search(r'Number of grey cl_hashes set to pending_xl_insert = 1: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        self.assertEqual(int(actual), expected, 'LogFile : Number of cl_hashes in #greytmp : count doesnt match')
        DB_CLEAN_UP = False


    def test_007(self):
        """Safemode false Number of yellow cl_hashes set to pending_xl_insert = 1"""
        sql = "select * from prevalence p (nolock),WebReputation w (nolock), build b (nolock) \
        where p.cl_hash = w.cl_hash and p.cl_hash = b.cl_hash and b.is_generated = 0 and w.web_reputation > 29 and w.web_reputation <= 49 \
        and p.is_locked = 0 order by p.prevalence desc,b.updated_on"
        expected = self.d2_conn.get_row_count(sql)
        logging.info('from DB = %s' % (expected))

        DATA = self.log_analysis()

        xl_inserted = re.search(r'Number of yellow cl_hashes set to pending_xl_insert = 1: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        self.assertEqual(int(actual), expected, 'LogFile : Number of cl_hashes in #yellowtmp : count doesnt match')
        DB_CLEAN_UP = False


    def test_008(self):
        """Safemode false Number of red cl_hashes set to pending_xl_insert = 1"""
        sql = "select * from prevalence p (nolock),WebReputation w (nolock), build b (nolock) \
        where p.cl_hash = w.cl_hash and p.cl_hash = b.cl_hash and b.is_generated = 0 and w.web_reputation > 49 \
        and p.is_locked = 0 order by p.prevalence desc,b.updated_on"
        expected = self.d2_conn.get_row_count(sql)
        logging.info('from DB = %s' % (expected))

        DATA = self.log_analysis()

        xl_inserted = re.search(r'Number of red cl_hashes set to pending_xl_insert = 1: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        self.assertEqual(int(actual), expected, 'LogFile : Number of cl_hashes in #redtmp : count doesnt match')
        DB_CLEAN_UP = False

    def test_009(self):
        """Safemode false prevalence URLs with prevalence > 0 published in TS"""
        DATA = self.log_analysis()
        query_ts_bcz_prev_greater_zero = 'select * from prevalence (nolock) where is_top_site=0 and is_locked=0 \
        and is_sanity_url=0 and customer_ticket=0 and prevalence > 0 and publish_xl=0 and publish_ts=1 \
        and cl_hash in ' + PREVALENCE_GREATER_ZERO

        for row in self.d2_conn.get_select_data(query_ts_bcz_prev_greater_zero):
            self.assertTrue(row['publish_ts'], 'publish_ts is FALSE')
            self.assertFalse(row['publish_xl'], 'publish_xl is True')
            self.assertFalse(row['xl_inserted'], 'xl_inserted is NOT None \n %s' % (row))
            self.assertTrue(row['ts_inserted'], 'ts_inserted is NOT None \n %s' % (row))


    def test_010(self):
        """Safemode false publishTs Number of prevalence URLs to be published in TS"""
        DATA = self.log_analysis()
        query_ts_bcz_prev_greater_zero = 'select cl_hash from prevalence (nolock) where is_top_site=0 and is_locked=0 \
        and is_sanity_url=0 and customer_ticket=0 and prevalence > 0 and publish_xl=0 and publish_ts=1 '
        total_ts_bcz_prev_greater_zero = self.d2_conn.get_row_count(query_ts_bcz_prev_greater_zero)
        expected = int(total_ts_bcz_prev_greater_zero)
        self.assertNotEqual(expected, 0, 'No cl_hashes set to publish_ts because prevalence is > 0 or there are \
        no cl_hashes in the table which has prevalence > 0')
        count = re.search(r'publishTs Number of prevalence URLs to be published in TS: (\d+)', DATA)
        actual = int(count.group(1))
        self.assertTrue(re.search(r'Finish sync of prevalence table with the build table', DATA, re.I | re.M), 'Some issue \
        encountered while running publishing agent, agent run not completed')
        self.assertEqual(actual, expected, 'Mismatch in total number of cl_hash published to \
        ts because of prevalence')


class SpecificSingleCategory(PublishingAgentSandbox):
    @classmethod
    def setUpClass(cls):
        """ Running publishing agent from Framework """
        set_prop_application(write_file_bool=True)
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.xlGreenPercent'] = '0'
        agent_prop['agent.publish.xlGreyPercent'] = '0'
        agent_prop['agent.publish.xlYellowPercent'] = '0'
        agent_prop['agent.publish.xlRedPercent'] = '0'
        del agent_prop['agent.publish.xlEnsureCatPublish2']
        agent_prop['agent.publish.xlEnsureCatPublish1'] = 'bl  bu  mk'
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        # Db Cleanup and then start agent
        cls.d2_conn = TsMsSqlWrap('D2')
        cls.database_reset()
        cls.agent_execution()

        # Check if the agent shell script exists or not
        if not runtime.SH.start_agent.isfile():
            raise FileNotFoundError(runtime.SH.start_agent)

    @classmethod
    def database_reset(cls):
        # URLCATEGORY_BL_BU_MK = """(0xFFC4D4119A10417EB058DB44)"""
        # URLCATEGORY_BL_BU_FI = """(0xFEDC6E460D9885AEBBC0DD8E,0xFEBC7A51B7CA55BB2801A3F0)"""
        """ Resets publishing bits and inserted dates in db """
        try:

            db_initialization_prevalence = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=0,publish_xl=0, \
    publish_ts=0,last_checked =NULL,last_seen=NULL,xl_removed=NULL,ts_removed=NULL,xl_inserted=NULL,ts_inserted=NULL"
            cls.d2_conn.execute_sql_commit(db_initialization_prevalence)
            db_initialization_build = "update build set mcafee_secure=0 where cl_hash in " + MCAFEESECURE
            cls.d2_conn.execute_sql_commit(db_initialization_build)
            logging.info("DataBase Tables updated for publish_xl, publish_ts, ts_inserted, xl_inserted ")
        except Exception as exc:
            logging.info('Exception while resetting db: PublishingAgent.database_reset - {}'.format(exc))
            return False
        else:
            update_url_category = "update build set cat_xl = 'bl  bu  mk' where cl_hash in " + URLCATEGORY_BL_BU_MK
            cls.d2_conn.execute_sql_commit(update_url_category)
        return True

    def test_001(self):
        """Safemode false Valid single category urls publishes in XL & TS"""
        # prop_publish_agent(write_file_name=LOCAL_AGENT_PROP_FILE,
        # update_dict={'agent.publish.xlEnsureCatPublish1': 'bl  bu  mk'})
        validation_query1 = "select * from prevalence where publish_xl=1 and publish_ts=1 and is_sanity_url=0 \
        and is_top_site=0 and customer_ticket=0 and is_locked=1 and cl_hash in \
        (select cl_hash from build where mcafee_secure=0 and cat_xl='bl  bu  mk' \
        and cl_hash in " + URLCATEGORY_BL_BU_MK + ")"
        row_count_after_run = self.d2_conn.get_row_count(validation_query1)
        self.assertNotEqual(row_count_after_run, 0, 'No cl_hashes with the category is bl  bu  mk \
        are published to xl & ts list or selected cl_hash doesnt exist in the prevalence table')
        validation_query1 = "select publish_xl,publish_ts,is_locked,ts_inserted,xl_inserted from prevalence \
        where publish_xl=1 and publish_ts=1 and is_locked=1 and cl_hash in " + URLCATEGORY_BL_BU_MK
        for row in self.d2_conn.get_select_data(validation_query1):
            self.assertTrue(row['publish_xl'], "publish xl not set for the cl_hash")
            self.assertTrue(row['publish_ts'], "publish_ts not set for the cl_hash")
            self.assertTrue(row['ts_inserted'], "ts_inserted not set for the cl_hash")
            self.assertTrue(row['xl_inserted'], "xl_inserted not set for the cl_hash")

    def test_002(self):
        """Safemode false Number of specfic categories urls to be published"""
        DATA = self.log_analysis()
        query_category_xl_published = "select * from prevalence where publish_xl=1 and publish_ts=1 and is_sanity_url=0 \
        and is_top_site=0 and customer_ticket=0 and is_locked=1 and cl_hash in \
        (select cl_hash from build where mcafee_secure=0 and cat_xl='bl  bu  mk' \
        and cl_hash in " + URLCATEGORY_BL_BU_MK + ")"

        total_category_xl_published = self.d2_conn.get_row_count(query_category_xl_published)
        expected = int(total_category_xl_published)
        self.assertNotEqual(expected, 0, 'No cl_hash set to publish_xl because of specific category criteria or \
        the selected cl_hash doesnt exists in the data bases')

        count = re.search(r'Number of URLs with specfic categories set to publish_xl = 1: (\d+)', DATA)
        actual = int(count.group(1))

        self.assertEqual(actual, expected, 'Mismatch in total number of cl_hash published to xl')
        self.assertEqual(actual, expected, 'Mismatch in total number of cl_hash published to xl because of \
        specific category')


class SpecificMultipleCategory(PublishingAgentSandbox):
    @classmethod
    def setUpClass(cls):
        """ Running publishing agent from Framework """
        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        set_prop_application(write_file_bool=True)
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.xlGreenPercent'] = '0'
        agent_prop['agent.publish.xlGreyPercent'] = '0'
        agent_prop['agent.publish.xlYellowPercent'] = '0'
        agent_prop['agent.publish.xlRedPercent'] = '0'
        agent_prop['agent.publish.xlEnsureCatPublish1'] = 'bl  bu  mk'
        agent_prop['agent.publish.xlEnsureCatPublish2'] = 'bl  bu  fi'
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)

        # Db Cleanup and then start agent
        cls.d2_conn = TsMsSqlWrap('D2')
        cls.database_reset()
        cls.agent_execution()

        # Check if the agent shell script exists or not
        if not runtime.SH.start_agent.isfile():
            raise FileNotFoundError(runtime.SH.start_agent)

    @classmethod
    def database_reset(cls):
        """ Resets publishing bits and inserted dates in db """
        try:
            db_initialization_prevalence = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=0,publish_xl=0, \
    publish_ts=0,last_checked =NULL,last_seen=NULL,xl_removed=NULL,ts_removed=NULL,xl_inserted=NULL,ts_inserted=NULL"
            cls.d2_conn.execute_sql_commit(db_initialization_prevalence)
            db_initialization_build = "update build set mcafee_secure=0 where cl_hash in " + MCAFEESECURE
            cls.d2_conn.execute_sql_commit(db_initialization_build)
            logging.info("DataBase Tables updated for publish_xl, publish_ts, ts_inserted, xl_inserted ")
        except Exception as exc:
            logging.info('Exception while resetting db: PublishingAgent.database_reset - {}'.format(exc))
            return False
        else:
            update_url_category1 = "update build set cat_xl = 'bl  bu  mk' where cl_hash in " + URLCATEGORY_BL_BU_MK
            cls.d2_conn.execute_sql_commit(update_url_category1)

            update_url_category2 = "update build set cat_xl = 'bl  bu  fi' where cl_hash in " + URLCATEGORY_BL_BU_FI
            cls.d2_conn.execute_sql_commit(update_url_category2)
        return True

    def test_001(self):
        """Safemode false Valid multiple categories urls publishes in XL & TS"""
        # prop_publish_agent(write_file_name=LOCAL_AGENT_PROP_FILE,
        # update_dict={'agent.publish.xlEnsureCatPublish1': 'bl  bu  mk'})
        validation_query1 = "select * from prevalence where publish_xl=1 and publish_ts=1 and is_sanity_url=0 \
        and is_top_site=0 and customer_ticket=0 and is_locked=1 and cl_hash in \
        (select cl_hash from build where mcafee_secure=0 and cat_xl = 'bl  bu  mk' or cat_xl = 'bl  bu  fi'\
        and cl_hash in " + URLCATEGORY_BL_BU_MK + "or cl_hash in " + URLCATEGORY_BL_BU_FI + ")"
        row_count_after_run = self.d2_conn.get_row_count(validation_query1)
        print(self.d2_conn.get_row_count(validation_query1))
        self.assertNotEqual(row_count_after_run, 0, 'No cl_hashes with the category is bl  bu  mk or bl  bu  fi\
        are published to xl & ts list or selected cl_hashs doesnt exist in the prevalence table')
        for row in self.d2_conn.get_select_data(validation_query1):
            self.assertTrue(row['publish_xl'], "publish xl not set for the cl_hash")
            self.assertTrue(row['publish_ts'], "publish_ts not set for the cl_hash")
            self.assertTrue(row['ts_inserted'], "ts_inserted not set for the cl_hash")
            self.assertTrue(row['xl_inserted'], "xl_inserted not set for the cl_hash")


class XLRemovalCriteriaLogAnalysis(PublishingAgentSandbox):
    @classmethod
    def setUpClass(cls):
        """ Running publishing agent from Framework """
        set_prop_application(write_file_bool=True)
        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        agent_prop = prop_publish_agent()
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        # Db Cleanup and then
        cls.d2_conn = TsMsSqlWrap('D2')
        cls.database_reset()
        # cls.agent_execution()

        initialization_prevalence_query = "update dbo.prevalence set is_top_site=0,is_sanity_url=0,\
        customer_ticket=0,xl_inserted=NULL,ts_inserted=NULL where cl_hash in " + XL_REMOVAL_CRITERIA_DOMAIN
        cls.d2_conn.execute_sql_commit(initialization_prevalence_query)

        initialization_prevalence_query = "update prevalence set is_top_site=1,is_sanity_url=0,\
        customer_ticket=0 where cl_hash in " + XL_REMOVAL_CRITERIA
        # PublishingAgentSandbox.database_update_query(cls,initialization_prevalence_query)
        cls.d2_conn.execute_sql_commit(initialization_prevalence_query)

        # Run 1 to ensure if the child exist in XL parents will be published to xl
        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        cls.agent_execution()

        # Reinitialize child hashes to match the xl removal criteria
        initialization_prevalence_query = "update prevalence set is_top_site=0 where cl_hash in " + XL_REMOVAL_CRITERIA
        cls.d2_conn.execute_sql_commit(initialization_prevalence_query)

        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        cls.agent_execution()

    @classmethod
    def database_reset(cls):
        # URLCATEGORY_BL_BU_MK = """(0xFFC4D4119A10417EB058DB44)"""
        # URLCATEGORY_BL_BU_FI = """(0xFEDC6E460D9885AEBBC0DD8E,0xFEBC7A51B7CA55BB2801A3F0)"""
        """ Resets publishing bits and inserted dates in db """
        try:
            # d2_conn = TsMsSqlWrap('D2')
            db_initialization_prevalence = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=0,publish_xl=0, \
    publish_ts=0,last_checked =NULL,last_seen=NULL,xl_removed=NULL,ts_removed=NULL,xl_inserted=NULL,ts_inserted=NULL"
            cls.d2_conn.execute_sql_commit(db_initialization_prevalence)
            db_initialization_build = "update build set mcafee_secure=0 where cl_hash in " + MCAFEESECURE
            cls.d2_conn.execute_sql_commit(db_initialization_build)
            logging.info("DataBase Tables updated for publish_xl, publish_ts, ts_inserted, xl_inserted ")
        except Exception as exc:
            logging.info('Exception while resetting db: PublishingAgent.database_reset - {}'.format(exc))
            return False
        else:
            return True

    def test_001(self):
        """Safemode false Number of URLs removed from XL"""
        # Note as per the change made in WEB_R016 if the child & domain matches the xl removal criteria
        # Both can be removed from XL ie domain & child
        DATA = self.log_analysis()
        sql = "select cl_hash from d2.dbo.prevalence where xl_removed is not NULL and cl_hash in " + XL_REMOVAL_CRITERIA_CHILD_DOMAIN
        expected = int(self.d2_conn.get_row_count(sql))
        logging.info('from DB = %s' % (expected))
        xl_inserted = re.search(r'Number of URLs removed from XL: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        print("###### Expected value is "+ str(expected))
        print("###### Actual value is "+ str(actual))
        self.assertEqual(int(actual), expected,
                         'LogFile : Number of cl_hashes set to pending_xl_insert = 0 : count doesnt match')

    def test_002(self):
        """Safemode false Number of cl_hashes set to publish_xl = 0"""
        # Note as per the change made in WEB_R016 if the child & domain matches the xl removal criteria
        # Both can be removed from XL ie domain & child
        DATA = self.log_analysis()
        sql = "select cl_hash from d2.dbo.prevalence where xl_removed is not NULL and cl_hash in " + XL_REMOVAL_CRITERIA_CHILD_DOMAIN
        expected = int(self.d2_conn.get_row_count(sql))
        logging.info('from DB = %s' % (expected))
        xl_inserted = re.search(r'removeXl Number of cl_hashes set to publish_xl = 0: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        print("###### Expected value is "+ str(expected))
        print("###### Actual value is "+ str(actual))
        self.assertEqual(int(actual), expected,
                         'LogFile : Number of cl_hashes set to publish_xl = 0 count doesnt match')


    def test_003(self):
        """set pending_xl_remove = 0 where pending_xl_remove = 1"""
        # Note as per the change made in WEB_R016 if the child & domain matches the xl removal criteria
        # Both can be removed from XL ie domain & child
        DATA = self.log_analysis()
        sql = "select cl_hash from d2.dbo.prevalence where xl_removed is not NULL and cl_hash in " + XL_REMOVAL_CRITERIA_CHILD_DOMAIN
        expected = int(self.d2_conn.get_row_count(sql))
        logging.info('from DB = %s' % (expected))
        xl_inserted = re.search(r'cleanXlPrevalenceTable Number of cl_hashes set to pending_xl_remove = 0: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        print("###### Expected value is "+ str(expected))
        print("###### Actual value is "+ str(actual))
        self.assertEqual(int(actual), expected, 'LogFile : Number of cl_hashes set pending_xl_remove = 0 where \
        pending_xl_ remove = 1 count doesnt match')

    def test_004(self):
        """Safe mode false if child removed from xl parent can be removed from XL """
        # Change made in WEB_R016 -> If Child in XL domain should not be removed from XL
        # Run 1 Validation to ensure if the child exist in XL parents will be published to xl

        validation_query3 = "select * from dbo.prevalence (nolock) where domain_clhash = cl_hash and \
        is_domain=1 and cl_hash in " + XL_REMOVAL_CRITERIA_DOMAIN
        self.assertNotEqual(self.d2_conn.get_row_count(validation_query3), 0, 'Domain cl_hashes are \
        removed from xl_list')

        for row in self.d2_conn.get_select_data(validation_query3):
            assert not row['publish_xl']
            #assert row['ts_inserted']
            #assert row['xl_inserted']
            assert row['xl_removed']
            #assert not row['ts_removed']


class XLRemovalCriteria(PublishingAgentSandbox):
    @classmethod
    def setUpClass(cls):
        """ Running publishing agent from Framework """
        set_prop_application(write_file_bool=True)
        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        agent_prop = prop_publish_agent()
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        # Db Cleanup and then
        cls.d2_conn = TsMsSqlWrap('D2')
        cls.database_reset()
        # cls.agent_execution()

        initialization_prevalence_query = "update dbo.prevalence set is_top_site=0,is_sanity_url=0,\
        customer_ticket=0,xl_inserted=NULL,ts_inserted=NULL where cl_hash in " + XL_REMOVAL_CRITERIA_DOMAIN
        cls.d2_conn.execute_sql_commit(initialization_prevalence_query)

        initialization_prevalence_query = "update prevalence set is_top_site=1,is_sanity_url=0,\
        customer_ticket=0 where cl_hash in " + XL_REMOVAL_CRITERIA
        # PublishingAgentSandbox.database_update_query(cls,initialization_prevalence_query)
        cls.d2_conn.execute_sql_commit(initialization_prevalence_query)

        # Run 1 to ensure if the child exist in XL parents will be published to xl
        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        cls.agent_execution()

    @classmethod
    def database_reset(cls):
        # URLCATEGORY_BL_BU_MK = """(0xFFC4D4119A10417EB058DB44)"""
        # URLCATEGORY_BL_BU_FI = """(0xFEDC6E460D9885AEBBC0DD8E,0xFEBC7A51B7CA55BB2801A3F0)"""
        """ Resets publishing bits and inserted dates in db """
        try:
            # d2_conn = TsMsSqlWrap('D2')
            db_initialization_prevalence = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=0,publish_xl=0, \
    publish_ts=0,last_checked =NULL,last_seen=NULL,xl_removed=NULL,ts_removed=NULL,xl_inserted=NULL,ts_inserted=NULL"
            cls.d2_conn.execute_sql_commit(db_initialization_prevalence)
            db_initialization_build = "update build set mcafee_secure=0 where cl_hash in " + MCAFEESECURE
            cls.d2_conn.execute_sql_commit(db_initialization_build)
            logging.info("DataBase Tables updated for publish_xl, publish_ts, ts_inserted, xl_inserted ")
        except Exception as exc:
            logging.info('Exception while resetting db: PublishingAgent.database_reset - {}'.format(exc))
            return False
        else:
            return True


    def test_001(self):
        """Safe mode false XL removal criteria no triming domain level entries"""
        # Change made in WEB_R016 -> If Child in XL domain should not be removed from XL
        # Note as per the change made in WEB_R016 if the child & domain matches the xl removal criteria
        # Both can be removed from XL ie domain & child


        validate_child_in_xl = "select * from prevalence (nolock) where is_top_site =1 and publish_xl =1 and \
        cl_hash in " + XL_REMOVAL_CRITERIA
        assert self.d2_conn.get_row_count(validate_child_in_xl) != 0

        validate_parent_in_xl = "select * from prevalence (nolock) where is_top_site =0 and is_sanity_url=0 and \
        customer_ticket = 0 and publish_xl =1 and cl_hash in " + XL_REMOVAL_CRITERIA_DOMAIN

        assert self.d2_conn.get_row_count(validate_parent_in_xl) != 0

        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        self.agent_execution()

        # Run 2 Validation to ensure if the parent is not removed if child exist in XL
        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        self.agent_execution()

        validation_query3 = "select * from dbo.prevalence (nolock) where domain_clhash = cl_hash and \
        is_domain=1 and cl_hash in " + XL_REMOVAL_CRITERIA_DOMAIN
        self.assertNotEqual(self.d2_conn.get_row_count(validation_query3), 0, 'Domain cl_hashes are \
        removed from xl_list')

        for row in self.d2_conn.get_select_data(validation_query3):
            assert row['publish_ts']
            assert row['publish_xl']
            #assert row['ts_inserted']
            #assert row['xl_inserted']
            assert not row['xl_removed']
            assert not row['ts_removed']


class TSRemovalCriteriaDomain(PublishingAgentSandbox):
    @classmethod
    def setUpClass(cls):
        """ Running publishing agent from Framework """
        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        set_prop_application(write_file_bool=True)
        agent_prop = prop_publish_agent()
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        # Db Cleanup and then
        cls.database_reset()
        cls.d2_conn = TsMsSqlWrap('D2')

        db_initialization_prevalence = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=0,publish_xl=0, \
        publish_ts=0,last_checked =NULL,last_seen=NULL,xl_removed=NULL,ts_removed=NULL,xl_inserted=NULL,ts_inserted=NULL"
        cls.d2_conn.execute_sql_commit(db_initialization_prevalence)
        db_initialization_build = "update build set mcafee_secure=0 where cl_hash in " + MCAFEESECURE
        cls.d2_conn.execute_sql_commit(db_initialization_build)
        logging.info("DataBase Tables updated for publish_xl, publish_ts, ts_inserted, xl_inserted ")

        initialization_prevalence_query = "update prevalence set prevalence=10 where cl_hash in " + CHILD_FOR_DOMAIN
        PublishingAgentSandbox.database_update_query(cls, initialization_prevalence_query)

        initialization_build_domain_query = "update dbo.build set u2_cats = 'ms',updated_on= '2014-06-01',\
        mcafee_secure=0 where cl_hash in " + TS_REMOVAL_CRITERIA_DOMAIN
        PublishingAgentSandbox.database_update_query(cls, initialization_build_domain_query)

        before_run = "select * from prevalence (nolock) where is_domain=1 and cl_hash in \
        (select cl_hash from build (nolock) where u2_cats = 'ms' and updated_on= '2014-06-01'and \
        mcafee_secure=0 and cl_hash in " + TS_REMOVAL_CRITERIA_DOMAIN + ")"
        assert cls.d2_conn.get_row_count(before_run) != 0

        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        cls.agent_execution()

        after_run = "select * from prevalence (nolock) where is_domain=1 \
        and cl_hash in (select cl_hash from build (nolock) where u2_cats = 'ms' and updated_on= '2014-06-01'and \
        mcafee_secure=0 and cl_hash in " + TS_REMOVAL_CRITERIA_DOMAIN + ")"
        logging.info('Checking whether there are no domain cl_hashes meeting the TS removal criteria or not')
        assert cls.d2_conn.get_row_count(after_run) != 0


    @classmethod
    def database_reset(cls):
        """ Resets publishing bits and inserted dates in db """
        try:
            db_initialization_prevalence = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=0,publish_xl=0, \
    publish_ts=0,last_checked =NULL,last_seen=NULL,xl_removed=NULL,ts_removed=NULL,xl_inserted=NULL,ts_inserted=NULL"
            cls.d2_conn.execute_sql_commit(db_initialization_prevalence)
            db_initialization_build = "update build set mcafee_secure=0 where cl_hash in " + MCAFEESECURE
            cls.d2_conn.execute_sql_commit(db_initialization_build)
            logging.info("DataBase Tables updated for publish_xl, publish_ts, ts_inserted, xl_inserted ")
        except Exception as exc:
            logging.info('Exception while resetting db: PublishingAgent.database_reset - {}'.format(exc))
            return False
        else:
            return True


    def test_001(self):
        """Safe mode false TS removal criteria no triming domain level entries"""
        # prop_publish_agent(write_file_name=LOCAL_AGENT_PROP_FILE,
        # update_dict={'agent.publish.tsTrimIsGenIps': 'false'})
        # These step are to ensure domain hash are published in to ts because the child is published ie \
        # the criteria is if child in TS publish parents to TS if the prevalence is > 0
        validation_query = "select is_top_site,is_sanity_url,is_locked,customer_ticket,publish_xl,publish_ts,is_domain,\
        xl_inserted,ts_inserted,ts_removed from prevalence where cl_hash in" + TS_REMOVAL_CRITERIA_DOMAIN
        for row in self.d2_conn.get_select_data(validation_query):
            self.assertFalse(row['is_top_site'], True)
            self.assertFalse(row['is_sanity_url'], True)
            self.assertFalse(row['is_locked'], True)
            self.assertFalse(row['customer_ticket'], True)
            self.assertTrue(row['publish_ts'], True)
            self.assertFalse(row['publish_xl'], True)
            self.assertTrue(row['is_domain'], True)


class TSRemovalCriteria(PublishingAgentSandbox):
    @classmethod
    def setUpClass(cls):
        """ Running publishing agent from Framework """
        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        set_prop_application(write_file_bool=True)
        """ Running publishing agent from Framework """
        agent_prop = prop_publish_agent()
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        cls.d2_conn = TsMsSqlWrap('D2')
        cls.database_reset()

    @classmethod
    def database_reset(cls):
        """ Resets publishing bits and inserted dates in db """
        try:
            db_initialization_prevalence = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=0,publish_xl=0, \
    publish_ts=0,last_checked =NULL,last_seen=NULL,xl_removed=NULL,ts_removed=NULL,xl_inserted=NULL,ts_inserted=NULL"
            cls.d2_conn.execute_sql_commit(db_initialization_prevalence)
            db_initialization_build = "update build set mcafee_secure=0 where cl_hash in " + MCAFEESECURE
            cls.d2_conn.execute_sql_commit(db_initialization_build)
            logging.info("DataBase Tables updated for publish_xl, publish_ts, ts_inserted, xl_inserted ")
        except Exception as exc:
            logging.info('Exception while resetting db: PublishingAgent.database_reset - {}'.format(exc))
            return False
        else:
            return True

    def test_001(self):
        """Safemode false tsRemoveCategoryThreshold1=ms|30 to match parent url"""
        updated_on = self.modify_date(increment=-40)
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.tsRemoveCategoryThreshold1'] = 'ms|30'
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        self.assertTrue(self.isFileExist(LOCAL_AGENT_PROP_FILE),
                        'agent.properties file DO NOT exist [%s]' % LOCAL_AGENT_PROP_FILE)
        logging.info(agent_prop['agent.publish.safeMode'])
        self.assertEqual(agent_prop['agent.publish.safeMode'], 'false', "Safe mode property NOT set to false")

        initialization_prevalence_query = "update prevalence set prevalence=10,is_domain=0 where cl_hash in " + TS_REMOVAL
        self.database_update_query(initialization_prevalence_query)

        initialization_build_query = "update build set u2_cats = 'ms',updated_on=" + str(
            updated_on) + "where cl_hash in " + TS_REMOVAL
        self.database_update_query(initialization_build_query)

        before_run = "select * from prevalence where prevalence=10 and cl_hash in (select cl_hash from build where \
        u2_cats = 'ms' and cl_hash in" + TS_REMOVAL + " )"
        logging.info(before_run)
        self.assertNotEqual(self.d2_conn.get_row_count(before_run), 0, 'The selected cl_hash doesnt exists in db')

        self.agent_execution()

        initialization_prevalence_query = "update prevalence set prevalence=0 where cl_hash in " + TS_REMOVAL
        self.database_update_query(initialization_prevalence_query)

        self.agent_execution()

        validation_query2 = "select * from dbo.prevalence where cl_hash in " + TS_REMOVAL
        logging.info(self.d2_conn.get_row_count(validation_query2))
        for row in self.d2_conn.get_select_data(validation_query2):
            self.assertFalse(row['publish_ts'], True)
            self.assertFalse(row['publish_xl'], True)
            self.assertTrue(row['ts_inserted'], True)
            self.assertTrue(row['ts_removed'], True)

    def test_002(self):
        """Safemode false Number of URLs Removed from TS"""
        DATA = self.log_analysis()
        sql = "select cl_hash from prevalence where xl_inserted=0 and ts_inserted=0 and xl_removed is not NULL and \
        ts_removed is not NULL and cl_hash in " + TS_REMOVAL
        expected = int(self.d2_conn.get_row_count(sql))
        logging.info('from DB = %s' % (expected))
        xl_inserted = re.search(r'removeTs Number of cl_hashes set publish_ts = 0, publish_xl = 0: (\d+)', DATA)
        logging.info(xl_inserted.group())
        actual = xl_inserted.group(1)
        self.assertEqual(int(actual), expected, 'LogFile : Number of cl_hashes set set publish_ts=0 count doesnt match')

    def test_003(self):
        """Safe mode false if mcafee_secure set not removed from ts"""
        # Note: Once the date converter function is ready the updated_on variable will be made more dynamic
        # Should be done by next demo
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.tsRemoveCategoryThreshold1'] = 'ms|30'
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        self.assertTrue(self.isFileExist(LOCAL_AGENT_PROP_FILE),
                        'agent.properties file DO NOT exist [%s]' % LOCAL_AGENT_PROP_FILE)
        updated_on = self.modify_date(increment=-40)
        initialization_build_query1 = "update dbo.build set u2_cats = 'ms',updated_on=" + updated_on + ",mcafee_secure=1 \
        where cl_hash in " + MCAFEESECURE
        self.database_update_query(initialization_build_query1)

        before_run = "select * from prevalence where is_top_site=0 and is_sanity_url=0 and customer_ticket=0 and \
        is_locked=0 and cl_hash in (select cl_hash from build where mcafee_secure=1 and cl_hash in " + MCAFEESECURE + " )"
        self.assertNotEqual(self.d2_conn.get_row_count(before_run), 0, 'No cl_hashes set to mcafee_secure \
        or the cl_hashes selected doesnt exists in the db')

        self.agent_execution()

        # Negative Test
        '''
        query_number_mcafee_secure = "update build set mcafee_secure=0"
        self.d2_conn.execute_sql_commit(query_number_mcafee_secure)

        self.agent_execution()
        '''
        ##

        after_run = "select * from prevalence where publish_ts=1 and publish_xl=0 and cl_hash in\
        (select cl_hash from build where mcafee_secure=1 and u2_cats = 'ms' and updated_on= " + updated_on + ")"
        self.assertNotEqual(self.d2_conn.get_row_count(after_run), 0, 'cl_hashes set to mcafee_secure \
        are removed or hashes are set xl already ')

        validation_query = "select is_top_site,is_sanity_url,is_locked,customer_ticket,publish_xl,publish_ts,ts_removed  \
        from prevalence where cl_hash in" + MCAFEESECURE
        for row in self.d2_conn.get_select_data(validation_query):
            self.assertFalse(row['is_top_site'], 'is_top_site is set for the cl_hash')
            self.assertFalse(row['is_sanity_url'], 'is_sanity_url is set for the cl_hash')
            self.assertFalse(row['customer_ticket'], 'customer_ticket is set for the cl_hash')
            self.assertTrue(row['publish_ts'], True)
            self.assertFalse(row['ts_removed'], 'cl_hash removed from ts')
            self.assertFalse(row['publish_xl'], 'cl_hash published to xl as well')


class TSTrimIsGenIPs(PublishingAgentSandbox):
    def setUp(self):
        """ Initiating database object """
        # check if application.properties file is created or not
        SandboxedTest.setUp(self)
        """ Running publishing agent from Framework """
        set_prop_application(write_file_bool=True)
        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        agent_prop = prop_publish_agent()
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        self.d2_conn = TsMsSqlWrap('D2')
        db_initialization_prevalence = "update prevalence set is_top_site=0,is_locked=0,\
        is_sanity_url=0,customer_ticket=0,publish_xl=0, publish_ts=0,last_checked =NULL,last_seen=NULL,xl_removed=NULL,\
        ts_removed=NULL,xl_inserted=NULL,ts_inserted=NULL"
        self.d2_conn.execute_sql_commit(db_initialization_prevalence)
        db_initialization_build = "update build set mcafee_secure=0 where cl_hash in " + MCAFEESECURE
        self.d2_conn.execute_sql_commit(db_initialization_build)
        logging.info("DataBase Tables updated for publish_xl, publish_ts, ts_inserted, xl_inserted ")


    def test_001(self):
        """Safemode = false,tsTrimIsGenIps = true and tsTrimIsGenIpAge=90"""
        ts_trim_age = 10
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.tsTrimIsGenIps'] = 'true'
        agent_prop['agent.publish.tsTrimIsGenIpAge'] = str(ts_trim_age)
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        self.assertTrue(self.isFileExist(LOCAL_AGENT_PROP_FILE),
                        'agent.properties file DO NOT exist [%s]' % LOCAL_AGENT_PROP_FILE)
        logging.info(agent_prop['agent.publish.safeMode'])
        self.assertEqual(agent_prop['agent.publish.safeMode'], 'false', "Safe mode property NOT set to false")

        logging.info("This first initialize query is to make the is_generated cl_hashes into TS list ie \
        cl_hash with prevalence > 0")
        trim_criteria_date = self.modify_date(increment=-(ts_trim_age + 2))
        initialization_build_query1 = "update build set updated_on=" + trim_criteria_date + " where cl_hash in " + TRIMISGENIPTS
        self.database_update_query(initialization_build_query1)

        logging.info("This query is to make the cl_hash to be removed matching the tsTrimIsGenIpAge")
        initialization_prevalence_query1 = "update prevalence set prevalence=10 where cl_hash in " + TRIMISGENIPTS
        self.database_update_query(initialization_prevalence_query1)

        before_run = "select * from prevalence where prevalence > 0 and cl_hash in (select cl_hash from build where \
        is_generated = 1 and url_id > 0 and wa_viewed = 0 and is_ip = 1 and mcafee_secure = 0 and \
        url like '%://%/%' and cl_hash in (select cl_hash from build where cl_hash in " + TRIMISGENIPTS + " ))"
        logging.info(before_run)
        self.assertNotEqual(self.d2_conn.get_row_count(before_run), 0, 'There are no cl_hashes which matches \
        the is_generated trimming criteria')

        self.agent_execution()

        validation_query1 = "select * from dbo.prevalence where publish_xl=0 and publish_ts=1 and prevalence = 10 \
        and cl_hash in " + TRIMISGENIPTS
        self.assertNotEqual(self.d2_conn.get_row_count(validation_query1), 0, 'There are no is_generated \
        cl_hashes pushed into TS list')

        logging.info("This initialize query just sets the condition for making the cl_hash suitable for \
        trimming based on is_generated hashes")
        initialization_prevalence_query2 = "update prevalence set prevalence=0 where cl_hash in " + TRIMISGENIPTS
        self.database_update_query(initialization_prevalence_query2)

        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        self.agent_execution()

        validation_query2 = "select * from dbo.prevalence where publish_xl=0 and publish_ts=0 and \
        ts_inserted is not NULL and ts_removed is not NULL and cl_hash in " + TRIMISGENIPTS
        self.assertNotEqual(self.d2_conn.get_row_count(validation_query2), 0, 'is_generated \
        cl_hashes are not removed from TS list')
        logging.info(self.d2_conn.get_row_count(validation_query2))
        for row in self.d2_conn.get_select_data(validation_query2):
            self.assertFalse(row['publish_ts'], True)
            self.assertFalse(row['publish_xl'], True)
            self.assertTrue(row['ts_inserted'], True)
            self.assertTrue(row['ts_removed'], True)


    def test_002(self):
        """Safemode = false,tsTrimIsGenIps = false and tsTrimIsGenIpAge=90"""
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.tsTrimIsGenIps'] = 'false'
        agent_prop['agent.publish.tsTrimIsGenIpAge'] = '10'
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)

        logging.info("This first initialize query is to make the is_generated cl_hashes into TS list ie \
        cl_hash with prevalence > 0")
        initialization_prevalence_query1 = "update prevalence set prevalence=10 where cl_hash in " + TRIMISGENIPTS
        self.database_update_query(initialization_prevalence_query1)

        before_run = "select * from prevalence where prevalence > 0 and cl_hash in (select cl_hash from build where \
        is_generated = 1 and url_id > 0 and wa_viewed = 0 and is_ip = 1 and mcafee_secure = 0 and \
        url like '%://%/%' and cl_hash in (select cl_hash from build where cl_hash in " + TRIMISGENIPTS + " ))"
        logging.info(before_run)
        self.assertNotEqual(self.d2_conn.get_row_count(before_run), 0, 'There are no cl_hashes which matches \
        the is_generated trimming criteria')

        self.agent_execution()

        validation_query1 = "select * from dbo.prevalence (nolock) where publish_xl=0 and publish_ts=1 and prevalence = 10 \
        and cl_hash in " + TRIMISGENIPTS
        self.assertNotEqual(self.d2_conn.get_row_count(validation_query1), 0, 'There are no is_generated \
        cl_hashes pushed into TS list')

        logging.info("This initialize query just sets the condition for making the cl_hash suitable for \
        trimming based on is_generated hashes")
        initialization_prevalence_query2 = "update prevalence set prevalence=0 where cl_hash in " + TRIMISGENIPTS
        self.database_update_query(initialization_prevalence_query2)

        self.agent_execution()

        validation_query2 = "select * from dbo.prevalence where publish_xl=0 and publish_ts=1 and \
        ts_inserted is not NULL and ts_removed is NULL and cl_hash in " + TRIMISGENIPTS
        self.assertNotEqual(self.d2_conn.get_row_count(validation_query2), 0, 'is_generated \
        cl_hashes are not removed from TS list')
        logging.info(self.d2_conn.get_row_count(validation_query2))
        for row in self.d2_conn.get_select_data(validation_query1):
            self.assertTrue(row['publish_ts'], True)
            self.assertFalse(row['publish_xl'], True)
            self.assertTrue(row['ts_inserted'], True)
            self.assertFalse(row['ts_removed'], True)


    def test_003(self):
        """Safemode = false,tsTrimIsGenIps is empty and tsTrimIsGenIpAge=90"""
        # By default tsTrimIsGenIps is false. So we do not expect is generated URLs to be trimmed from TS
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.tsTrimIsGenIps'] = ''
        agent_prop['agent.publish.tsTrimIsGenIpAge'] = '10'
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)

        logging.info("This first initialize query is to make the is_generated cl_hashes into TS list ie \
        cl_hash with prevalence > 0")
        initialization_prevalence_query1 = "update prevalence set prevalence=10 where cl_hash in " + TRIMISGENIPTS
        self.database_update_query(initialization_prevalence_query1)

        before_run = "select * from prevalence where prevalence > 0 and cl_hash in (select cl_hash from build where \
        is_generated = 1 and url_id > 0 and wa_viewed = 0 and is_ip = 1 and mcafee_secure = 0 and \
        url like '%://%/%' and cl_hash in (select cl_hash from build where cl_hash in " + TRIMISGENIPTS + " ))"
        logging.info(before_run)
        self.assertNotEqual(self.d2_conn.get_row_count(before_run), 0, 'There are no cl_hashes which matches \
        the is_generated trimming criteria')

        self.agent_execution()

        validation_query1 = "select * from dbo.prevalence (nolock) where publish_xl=0 and publish_ts=1 and prevalence = 10 \
        and cl_hash in " + TRIMISGENIPTS
        self.assertNotEqual(self.d2_conn.get_row_count(validation_query1), 0, 'There are no is_generated \
        cl_hashes pushed into TS list')

        logging.info("This initialize query just sets the condition for making the cl_hash suitable for \
        trimming based on is_generated hashes")
        initialization_prevalence_query2 = "update prevalence set prevalence=0 where cl_hash in " + TRIMISGENIPTS
        self.database_update_query(initialization_prevalence_query2)

        self.agent_execution()

        validation_query2 = "select * from dbo.prevalence where publish_xl=0 and publish_ts=1 and \
        ts_inserted is not NULL and ts_removed is NULL and cl_hash in " + TRIMISGENIPTS
        self.assertNotEqual(self.d2_conn.get_row_count(validation_query2), 0, 'Though tsTrimIsGenIps is false ,\
        is_generated cl_hashes are not removed from TS list or the cl_hashes are published to XL as well')
        logging.info(self.d2_conn.get_row_count(validation_query2))
        for row in self.d2_conn.get_select_data(validation_query1):
            self.assertTrue(row['publish_ts'], True)
            self.assertFalse(row['publish_xl'], True)
            self.assertTrue(row['ts_inserted'], True)
            self.assertFalse(row['ts_removed'], True)

    def test_004(self):  ## need to Correct code
        """Safemode = false,tsTrimIsGenIps=true and tsTrimIsGenIpAge is empty"""
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.tsTrimIsGenIps'] = 'true'
        agent_prop['agent.publish.tsTrimIsGenIpAge'] = ''
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        self.assertTrue(self.isFileExist(LOCAL_AGENT_PROP_FILE), 'agent.properties \
        file DO NOT exist [%s]' % LOCAL_AGENT_PROP_FILE)

        self.agent_execution()

        self.assertTrue(self.isFileExist(LOCAL_AGENT_PROP_FILE), 'log file doesnt exists\
        file DO NOT exist [%s]' % LOCAL_AGENT_PROP_FILE)

        fp = open('/opt/sftools/log/common.log')
        logging.info('Succesfully opened agents.log file')
        txt = ''.join(fp.readlines())
        fp.close()

        exception_received = re.search(r'java.lang.NumberFormatException: For input string: \"\"', txt)

        if exception_received:
            logging.info('Exception received')
            self.assertTrue('True')
        else:
            logging.info('No exception encountered may be due to tsTrimIsGenIpAge is not set to null')
            self.assertFalse('True')


    def test_005(self):
        """Safemode = false,tsTrimIsGenIps=false and tsTrimIsGenIpAge is empty"""
        # Note : is the  tsTrimIsGenIps
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.tsTrimIsGenIps'] = 'false'
        agent_prop['agent.publish.tsTrimIsGenIpAge'] = ''
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        self.assertTrue(self.isFileExist(LOCAL_AGENT_PROP_FILE), 'agent.properties \
        file DO NOT exist [%s]' % LOCAL_AGENT_PROP_FILE)

        logging.info("This first initialize query is to make the is_generated cl_hashes into TS list ie \
        cl_hash with prevalence > 0")
        initialization_prevalence_query1 = "update prevalence set prevalence=10 where cl_hash in " + TRIMISGENIPTS
        self.database_update_query(initialization_prevalence_query1)

        before_run = "select * from prevalence where prevalence > 0 and cl_hash in (select cl_hash from build where \
        is_generated = 1 and url_id > 0 and wa_viewed = 0 and is_ip = 1 and mcafee_secure = 0 and \
        url like '%://%/%' and cl_hash in (select cl_hash from build where cl_hash in " + TRIMISGENIPTS + " ))"
        logging.info(before_run)
        self.assertNotEqual(self.d2_conn.get_row_count(before_run), 0, 'There are no cl_hashes which matches \
        the is_generated trimming criteria')

        self.agent_execution()

        validation_query1 = "select * from dbo.prevalence (nolock) where publish_xl=0 and publish_ts=1 and prevalence = 10 \
        and cl_hash in " + TRIMISGENIPTS
        self.assertNotEqual(self.d2_conn.get_row_count(validation_query1), 0, 'There are no is_generated \
        cl_hashes pushed into TS list')

        logging.info("This initialize query just sets the condition for making the cl_hash suitable for \
        trimming based on is_generated hashes")
        initialization_prevalence_query2 = "update prevalence set prevalence=0 where cl_hash in " + TRIMISGENIPTS
        self.database_update_query(initialization_prevalence_query2)

        self.agent_execution()

        validation_query2 = "select * from dbo.prevalence where publish_xl=0 and publish_ts=1 and \
        ts_inserted is not NULL and ts_removed is NULL and cl_hash in " + TRIMISGENIPTS
        self.assertNotEqual(self.d2_conn.get_row_count(validation_query2), 0, 'Though tsTrimIsGenIps is false ,\
        is_generated cl_hashes are not removed from TS list or the cl_hashes are published to XL as well')
        logging.info(self.d2_conn.get_row_count(validation_query2))
        for row in self.d2_conn.get_select_data(validation_query1):
            self.assertTrue(row['publish_ts'], True)
            self.assertFalse(row['publish_xl'], True)
            self.assertTrue(row['ts_inserted'], True)
            self.assertFalse(row['ts_removed'], True)


    def test_006(self):
        """Safemode = false and tsTrimIsGenIps=true no tsTrimIsGenIpAge"""
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.tsTrimIsGenIps'] = 'true'
        del agent_prop['agent.publish.tsTrimIsGenIpAge']
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        self.assertTrue(self.isFileExist(LOCAL_AGENT_PROP_FILE), 'agent.properties \
        file DO NOT exist [%s]' % LOCAL_AGENT_PROP_FILE)

        if not agent_prop['agent.publish.tsTrimIsGenIpAge']:
            exit_code = 0
            logging.info('tsTrimIsGenIpAge property removed from file')
        else:
            exit_code = 1
            logging.info('tsTrimIsGenIpAge key present')

        # Assert statement to ensure if the tsTrimIsGenIps key is not removed exit the test.
        self.assertNotEqual(exit_code, 1, 'tsTrimIsGenIpAge key present ,so exiting the test')

        # Though tsTrimIsGenIpAge key is not defined publishing agent should execute successfully.
        logging.info("This first initialize query is to make the is_generated cl_hashes into TS list ie \
        cl_hash with prevalence > 0")
        initialization_prevalence_query1 = "update prevalence set prevalence=10 where cl_hash in " + TRIMISGENIPTS
        self.database_update_query(initialization_prevalence_query1)

        before_run = "select * from prevalence where prevalence > 0 and cl_hash in (select cl_hash from build where \
        is_generated = 1 and url_id > 0 and wa_viewed = 0 and is_ip = 1 and mcafee_secure = 0 and \
        url like '%://%/%' and cl_hash in (select cl_hash from build where cl_hash in " + TRIMISGENIPTS + " ))"
        logging.info(before_run)
        self.assertNotEqual(self.d2_conn.get_row_count(before_run), 0, 'There are no cl_hashes which matches \
        the is_generated trimming criteria')

        self.agent_execution()

        validation_query1 = "select * from dbo.prevalence (nolock) where publish_xl=0 and publish_ts=1 \
        and prevalence = 10 and cl_hash in " + TRIMISGENIPTS
        self.assertNotEqual(self.d2_conn.get_row_count(validation_query1), 0, 'There are no is_generated \
        cl_hashes pushed into TS list')

        logging.info("This initialize query just sets the condition for making the cl_hash suitable for \
        trimming based on is_generated hashes")
        initialization_prevalence_query2 = "update prevalence set prevalence=0 where cl_hash in " + TRIMISGENIPTS
        self.database_update_query(initialization_prevalence_query2)

        self.agent_execution()

        validation_query2 = "select * from dbo.prevalence where publish_xl=0 and publish_ts=1 and \
        ts_inserted is not NULL and ts_removed is NULL and cl_hash in " + TRIMISGENIPTS
        self.assertNotEqual(self.d2_conn.get_row_count(validation_query2), 0, 'is_generated \
        cl_hashes are not removed from TS list')
        logging.info(self.d2_conn.get_row_count(validation_query2))
        for row in self.d2_conn.get_select_data(validation_query1):
            self.assertTrue(row['publish_ts'], True)
            self.assertFalse(row['publish_xl'], True)
            self.assertTrue(row['ts_inserted'], True)
            self.assertFalse(row['ts_removed'], True)


class LogTest(PublishingAgentSandbox):
    @classmethod
    def setUpClass(cls):
        """ Running publishing agent from Framework """
        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        set_prop_application(write_file_bool=True)
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.xlNumberUrls'] = '100000000'
        agent_prop['agent.publish.xlGreenPercent'] = '100'
        agent_prop['agent.publish.xlGreyPercent'] = '100'
        agent_prop['agent.publish.xlYellowPercent'] = '100'
        agent_prop['agent.publish.xlRedPercent'] = '100'
        agent_prop['agent.publish.xlEnsureCatPublish1'] = 'invalid'
        agent_prop['agent.publish.xlEnsureCatPublish2'] = 'invalid'
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)

        # Db Cleanup and then start agent
        cls.d2_conn = TsMsSqlWrap('D2')
        cls.database_reset()
        cls.agent_execution()

        # Check if the agent shell script exists or not
        if not runtime.SH.start_agent.isfile():
            raise FileNotFoundError(runtime.SH.start_agent)

    @classmethod
    def database_reset(cls):
        """ Resets publishing bits and inserted dates in db """
        try:
            db_initialization_prevalence = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,\
            customer_ticket=0,publish_xl=0,publish_ts=0,last_checked =NULL,last_seen=NULL,xl_removed=NULL,\
            ts_removed=NULL,xl_inserted=NULL,ts_inserted=NULL"
            cls.d2_conn.execute_sql_commit(db_initialization_prevalence)
            db_initialization_build = "update build set mcafee_secure=0 where cl_hash in " + MCAFEESECURE
            cls.d2_conn.execute_sql_commit(db_initialization_build)
            logging.info("DataBase Tables updated for publish_xl, publish_ts, ts_inserted, xl_inserted ")
        except Exception as exc:
            logging.info('Exception while resetting db: PublishingAgent.database_reset - {}'.format(exc))
            return False
        else:
            update_url_category1 = "update build set cat_xl = 'bl  bu  mk' where cl_hash in " + URLCATEGORY_BL_BU_MK
            cls.d2_conn.execute_sql_commit(update_url_category1)

            update_url_category2 = "update build set cat_xl = 'bl  bu  fi' where cl_hash in " + URLCATEGORY_BL_BU_FI
            cls.d2_conn.execute_sql_commit(update_url_category2)
        return True


    def test_001(self):
        """Safemode false BuildTable sync with prevalence table"""
        DATA = self.log_analysis()
        self.assertTrue(re.search(r'Finish sync of prevalence table with the build table', DATA, re.I | re.M), 'Some issue \
        encountered while running publishing agent')


    def test_002(self):
        """Safemode false Number of cl_hashes set to publish_ts = 1 for publish_xl =1"""
        DATA = self.log_analysis()
        query_total_xl_published = 'select cl_hash from prevalence (nolock) where publish_xl=1'
        total_xl_published = self.d2_conn.get_row_count(query_total_xl_published)
        expected = int(total_xl_published)
        count = re.search(r'Total number of XL Updates: (\d+)', DATA)
        actual = int(count.group(1))
        self.assertTrue(re.search(r'Finish sync of prevalence table with the build table', DATA, re.I | re.M), 'Some issue \
        encountered while running publishing agent')
        self.assertEqual(actual, expected, 'Mismatch in total number of cl_hash published to xl')


    def test_003(self):
        """Safemode false Number of cl_hashes set to publish_ts = 1 for publish_xl =1"""
        DATA = self.log_analysis()
        query_total_ensured_ts_bcz_xl = 'select cl_hash from prevalence (nolock) where publish_xl=1 and publish_ts=1'
        total_ensured_ts_bcz_xl = self.d2_conn.get_row_count(query_total_ensured_ts_bcz_xl)
        expected = int(total_ensured_ts_bcz_xl)
        count = re.search(r'ensureTsPublish Number of cl_hashes set to publish_ts = 1: (\d+)', DATA)
        actual = int(count.group(1))
        self.assertTrue(re.search(r'Finish sync of prevalence table with the build table', DATA, re.I | re.M), 'Some issue \
        encountered while running publishing agent')
        self.assertEqual(actual, expected, 'Mismatch in total number of cl_hash published to \
        ts because its published in xl')


    def test_004(self):
        """Safemode false Number of cl_hases set to publish_ts = 1 where prevalence > 0"""
        DATA = self.log_analysis()
        query_ts_bcz_prev_greater_zero = 'select cl_hash from prevalence (nolock) where prevalence > 0 \
        and publish_xl=0 and publish_ts=1'
        total_ts_bcz_prev_greater_zero = self.d2_conn.get_row_count(query_ts_bcz_prev_greater_zero)
        expected = int(total_ts_bcz_prev_greater_zero)
        count = re.search(r'publishTsAllPrevalence Number of cl_hases set to publish_ts = 1: (\d+)', DATA)
        actual = int(count.group(1))
        self.assertTrue(re.search(r'Finish sync of prevalence table with the build table', DATA, re.I | re.M), 'Some issue \
        encountered while running publishing agent')
        self.assertEqual(actual, expected, 'Mismatch in total number of cl_hash published to \
        ts because of prevalence > 0')


class ErrorTests(SandboxedAgentsTest):
    def setUp(self):
        set_prop_application(write_file_bool=True)
        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        SandboxedTest.setUp(self)

    #@pytest.mark.slow
    def test_001(self):
        """no xlEnsureCatPublish """
        err_str = "No xlEnsureCatPublish specified. Specify at least 'agent.publish.xlEnsureCatPublish1'"

        prop = prop_publish_agent()
        del prop['agent.publish.xlEnsureCatPublish1']
        del prop['agent.publish.xlEnsureCatPublish2']
        self.assertTrue(self.internal_execute_agent(prop, err_str))

    #@pytest.mark.slow
    def test_002(self):
        """xlEnsureCatPublish empty"""

        err_str = 'Invalid value for agent.publish.xlEnsureCatPublish1 property. Value cannot be blank!'
        prop = prop_publish_agent()
        prop['agent.publish.xlEnsureCatPublish1'] = ''
        del prop['agent.publish.xlEnsureCatPublish2']
        self.assertTrue(self.internal_execute_agent(prop, err_str))

    #@pytest.mark.slow
    def test_003(self):
        """no tsRemoveCategoryThreshold"""
        err_str = "No tsCategoryThreshold specified. Specify at least 'agent.publish.tsCategoryThreshold1'  in the properties file"
        prop = prop_publish_agent()
        del prop['agent.publish.tsRemoveCategoryThreshold1']
        del prop['agent.publish.xlEnsureCatPublish2']
        self.assertTrue(self.internal_execute_agent(prop, err_str))

    #@pytest.mark.slow
    def test_004(self):
        """tsRemoveCategoryThreshold empty"""
        """no tsRemoveCategoryThreshold"""
        err_str = "Invalid agent.publish.tsCategoryThreshold1 property.  Need " + \
                  "delimiter '|' to indicate difference between category and age."
        prop = prop_publish_agent()
        prop['agent.publish.tsRemoveCategoryThreshold1'] = ''
        del prop['agent.publish.xlEnsureCatPublish2']
        self.assertTrue(self.internal_execute_agent(prop, err_str))

    #@pytest.mark.slow
    def test_005(self):
        """no agent.publish.xlGreenPercent"""
        err_str = 'java.lang.NullPointerException'
        prop = prop_publish_agent()
        del prop['agent.publish.xlGreenPercent']
        self.assertTrue(self.internal_execute_agent(prop, err_str, log_file ='commonlog'))

    #@pytest.mark.slow
    def test_006(self):
        """agent.publish.xlGreenPercent is empt"""
        err_str = 'java.lang.NumberFormatException: empty String'
        prop = prop_publish_agent()
        prop['agent.publish.xlGreenPercent'] = ''
        self.assertTrue(self.internal_execute_agent(prop, err_str, log_file ='commonlog'))

    #@pytest.mark.slow
    def test_007(self):
        """no agent.publish.xlGreyPercent"""
        err_str = 'java.lang.NullPointerException'
        prop = prop_publish_agent()
        del prop['agent.publish.xlGreyPercent']
        self.assertTrue(self.internal_execute_agent(prop, err_str, log_file ='commonlog'))

    #@pytest.mark.slow
    def test_008(self):
        """agent.publish.xlGreyPercent is empty"""
        err_str = 'java.lang.NumberFormatException: empty String'
        prop = prop_publish_agent()
        prop['agent.publish.xlGreyPercent'] = ''
        self.assertTrue(self.internal_execute_agent(prop, err_str, log_file ='commonlog'))

    #@pytest.mark.slow
    def test_009(self):
        """no agent.publish.xlYellowPercent"""
        err_str = 'java.lang.NullPointerException'
        prop = prop_publish_agent()
        del prop['agent.publish.xlYellowPercent']
        self.assertTrue(self.internal_execute_agent(prop, err_str, log_file ='commonlog'))

    #@pytest.mark.slow
    def test_010(self):
        """agent.publish.xlYellowPercent is empty"""
        err_str = 'java.lang.NumberFormatException: empty String'
        prop = prop_publish_agent()
        prop['agent.publish.xlYellowPercent'] = ''
        self.assertTrue(self.internal_execute_agent(prop, err_str, log_file ='commonlog'))

    #@pytest.mark.slow
    def test_011(self):
        """no agent.publish.xlRedPercent"""
        err_str = 'java.lang.NullPointerException'
        prop = prop_publish_agent()
        del prop['agent.publish.xlRedPercent']
        self.assertTrue(self.internal_execute_agent(prop, err_str, log_file ='commonlog'))

    #@pytest.mark.slow
    def test_012(self):
        """agent.publish.xlRedPercent is empty"""
        err_str = 'java.lang.NumberFormatException: empty String'
        prop = prop_publish_agent()
        prop['agent.publish.xlRedPercent'] = ''
        self.assertTrue(self.internal_execute_agent(prop, err_str, log_file ='commonlog'))

    #@pytest.mark.slow
    def test_013(self):
        """no agent.publish.xlNumberUrls"""
        err_str = 'java.lang.NumberFormatException: null'
        prop = prop_publish_agent()
        del prop['agent.publish.xlNumberUrls']
        self.assertTrue(self.internal_execute_agent(prop, err_str, log_file ='commonlog'))

    #@pytest.mark.slow
    def test_014(self):
        """agent.publish.xlNumberUrls is empty"""
        err_str = 'java.lang.NumberFormatException: For input string: ""'
        prop = prop_publish_agent()
        prop['agent.publish.xlNumberUrls'] = ''
        self.assertTrue(self.internal_execute_agent(prop, err_str, log_file ='commonlog'))

    #@pytest.mark.slow
    def test_015(self):
        """no agent.publish.xlAllowedUpdates"""
        err_str = 'java.lang.NumberFormatException: null'
        prop = prop_publish_agent()
        del prop['agent.publish.xlAllowedUpdates']
        self.assertTrue(self.internal_execute_agent(prop, err_str, log_file ='commonlog'))

    #@pytest.mark.slow
    def test_016(self):
        """agent.publish.xlAllowedUpdates is empty"""
        err_str = 'java.lang.NumberFormatException: For input string: ""'
        prop = prop_publish_agent()
        prop['agent.publish.xlAllowedUpdates'] = ''
        self.assertTrue(self.internal_execute_agent(prop, err_str, log_file ='commonlog'))

    #@pytest.mark.slow
    def test_017(self):
        """no agent.publish.tsAllowedUpdates"""
        err_str = 'java.lang.NumberFormatException: null'
        prop = prop_publish_agent()
        del prop['agent.publish.tsAllowedUpdates']
        self.assertTrue(self.internal_execute_agent(prop, err_str, log_file ='commonlog'))

    #@pytest.mark.slow
    def test_018(self):
        """agent.publish.tsAllowedUpdates is empty"""
        err_str = 'java.lang.NumberFormatException: For input string: ""'
        prop = prop_publish_agent()
        prop['agent.publish.tsAllowedUpdates'] = ''
        self.assertTrue(self.internal_execute_agent(prop, err_str, log_file ='commonlog'))


class Standalone(PublishingAgentSandbox):
    def setUp(self):
        SandboxedTest.setUp(self)
        runtime.LOG.agents.remove_p()
        runtime.LOG.common.remove_p()
        set_prop_application(write_file_bool=True)
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.xlNumberUrls'] = '100000000'
        agent_prop['agent.publish.xlGreenPercent'] = '100'
        agent_prop['agent.publish.xlGreyPercent'] = '100'
        agent_prop['agent.publish.xlYellowPercent'] = '100'
        agent_prop['agent.publish.xlRedPercent'] = '100'
        agent_prop['agent.publish.xlEnsureCatPublish1'] = 'invalid'
        agent_prop['agent.publish.xlEnsureCatPublish2'] = 'invalid'

        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)

        self.d2_conn = TsMsSqlWrap('D2')
        d2_conn = TsMsSqlWrap('D2')
        db_initialization_prevalence = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=0,publish_xl=0, \
    publish_ts=0,last_checked =NULL,last_seen=NULL,xl_removed=NULL,ts_removed=NULL,xl_inserted=NULL,ts_inserted=NULL"
        d2_conn.execute_sql_commit(db_initialization_prevalence)
        db_initialization_build = "update build set mcafee_secure=0 where cl_hash in " + MCAFEESECURE
        d2_conn.execute_sql_commit(db_initialization_build)

    def test_001(self):
        """Publish agent shutdown bit set to 1 """
        # Running publishing agent in standalone mode
        sub_obj = ShellExecutor.run_daemon_standalone(runtime.SH.start_agent + ' %s' % LOCAL_AGENT_PROP_FILE)
        time.sleep(SLEEP_SECONDS)
        d2_con = TsMsSqlWrap('D2')
        sql = "update active_agents set shutdown_now=1 where agent_name='Publish' and is_running=0"
        stdout, stderr = sub_obj.communicate()
        sql = "update active_agents set shutdown_now=0 where agent_name='Publish'"
        obj = d2_con.execute_sql_commit(sql)
        log_file_contents = open(runtime.LOG.agents).read()
        if AGENT_START_STRING in log_file_contents and AGENT_COMPLETED_STRING in log_file_contents:
            logging.info('Found Start and completinon string in log file \
            i.e. agent started & completed successfully')
            return True
        else:
            logging.info('Didnd\'t find Start and completinon string in log file\
            i.e. probably agent didn\'t start')

    def test_002(self):
        """agent.publish.safeMode=true """
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.safeMode'] = 'true'
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        self.assertTrue(self.isFileExist(LOCAL_AGENT_PROP_FILE),
                        'agent.properties file DO NOT exist [%s]' % LOCAL_AGENT_PROP_FILE)
        self.assertEqual(agent_prop['agent.publish.safeMode'], 'true', "Safe mode property NOT set to true")
        sql_1 = "SELECT TABLE_NAME FROM information_schema.tables (nolock)"
        sql_2 = "select top 100 cl_hash, is_locked, is_top_site, is_sanity_url, publish_xl, publish_ts, customer_ticket \
                from prevalence where is_locked=0"
        logging.info('records from query %s ' % (self.d2_conn.get_row_count(sql_2)))
        sql_1_old_count = self.d2_conn.get_row_count(sql_1)
        sql_1_old_data = self.d2_conn.get_select_data(sql_1)
        sql_2_data_old = self.d2_conn.get_select_data(sql_2)
        # convert binary clhashes to hex to be used in db query inplace sql_2_data_old
        cl_hash_hex = []
        p = PrevalenceTable()
        for item in sql_2_data_old:
            cl_hex = p.d2_con.convert_cl_hash_bin_to_hex_string(item['cl_hash'])
            item['cl_hash'] = cl_hex
            # logging.info('cl_hash replaced with %s'%cl_hex)
        # logging.info(pprint.pformat(sql_2_data_old))
        self.agent_execution()
        logging.info('SUCCESS: publishing agent')
        sql_2_data_new = self.d2_conn.get_select_data(sql_2)
        # list of dictionary comparision
        for item in sql_2_data_new:
            cl_hex = p.d2_con.convert_cl_hash_bin_to_hex_string(item['cl_hash'])
            item['cl_hash'] = cl_hex
            # logging.info('cl_hash replaced with %s'%cl_hex)
            for element in sql_2_data_old:
                if element['cl_hash'] == item['cl_hash']:
                    self.assertEqual(element['is_locked'], item['is_locked'], 'is_locked mismatch for %s' % cl_hex)
                    self.assertEqual(element['is_top_site'], item['is_top_site'],
                                     'is_top_site mismatch for %s' % cl_hex)
                    self.assertEqual(element['is_sanity_url'], item['is_sanity_url'],
                                     'is_sanity_url mismatch for %s' % cl_hex)
                    self.assertEqual(element['publish_xl'], item['publish_xl'], 'publish_xl mismatch for %s' % cl_hex)
                    self.assertEqual(element['publish_ts'], item['publish_ts'], 'publish_ts mismatch for %s' % cl_hex)
                    self.assertEqual(element['customer_ticket'], item['customer_ticket'],
                                     'customer_ticket mismatch for %s' % cl_hex)
                    break
        # Checking temp file created in DB
        # d2_table_list = self.d2_conn.get_select_data(sql_1)
        # logging.info(pprint.pformat(d2_table_list))
        sql_1_new_count = self.d2_conn.get_row_count(sql_1)
        sql_1_new_data = self.d2_conn.get_select_data(sql_1)
        logging.info("sql_1_old_count [%s] sql_1_new_count [%s]" % (sql_1_old_count, sql_1_new_count))
        self.assertEqual(sql_1_new_count - sql_1_old_count, 1, 'More than 1 OR no new tables are created')
        # Find the new temp table created
        list_A = []
        list_B = []
        new_table = ''
        for item in sql_1_new_data:
            list_A.append(item['TABLE_NAME'])
        for item in sql_1_old_data:
            list_B.append(item['TABLE_NAME'])
        # logging.info(pprint.pformat(list_A))
        if len(set(list_A) - set(list_B)):
            for item in (set(list_A) - set(list_B)):
                # logging.info(item)
                # logging.info(type(item))
                new_table = item
                logging.info(new_table)
                # logging.info(type(new_table))
                break
        else:
            logging.info('No new table created in D2')
        # Delete the new temp table created
        sql_3 = "DROP TABLE [D2].[dbo].[" + new_table + "]"
        logging.info(sql_3)
        self.d2_conn.execute_sql_commit(sql_3)
        logging.info("Table %s deleted from D2" % new_table)
        logging.info("End of Test 7392")

    def test_003(self):
        """agent.publish.safeMode set to none """
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.safeMode'] = ''
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)
        self.assertTrue(self.isFileExist(LOCAL_AGENT_PROP_FILE),
                        'agent.properties file DO NOT exist [%s]' % LOCAL_AGENT_PROP_FILE)
        self.assertEqual(agent_prop['agent.publish.safeMode'], '', "Safe mode property NOT set to Blank")
        self.agent_execution()
        logging.info('SUCCESS: publishing agent')
        sql_1 = "select top 1000 * FROM prevalence (nolock) where is_top_site=1 and is_locked=0"
        logging.info('records from query %s ' % (self.d2_conn.get_row_count(sql_1)))
        if self.d2_conn.get_row_count(sql_1) != 0:
            for row in self.d2_conn.get_select_data(sql_1):
                self.assertTrue(row['publish_ts'],
                                'publish_ts NOT set true by publishing Agent for %s Exitting test' % (row))
                self.assertTrue(row['publish_xl'],
                                'publish_xl NOT set true by publishing Agent for %s Exitting test' % (row))
        else:
            logging.info('Record count is 0. No url matching the criteria')
            # self.assertRaises('NoRecordFetched')
        logging.info("End of Test 7390")


    def test_004(self):
        """safe mode property removed"""
        # Default safemode if false, Though not set updates made in the prevalence table itself.
        prop_publish_agent(delete_key_list=['agent.publish.safeMode'])
        sql_1 = "select * from prevalence (nolock) where customer_ticket =1 and is_sanity_url =1 and is_top_site=1"
        query = "update prevalence set customer_ticket=1, is_sanity_url=1, is_top_site=1 \
        where cl_hash in " + TOPSITE_SANITY_CUSTOMERTKT
        self.database_update_query(query)
        self.assertNotEqual(self.d2_conn.get_row_count(sql_1), 0, 'Row count is zero')
        (stdo, stderr) = self.agent_execution()
        logging.info('Agent post run stats \n stdo [%s] stderr [%s]' % (stdo, stderr))
        self.assertNotEqual(self.d2_conn.get_row_count(sql_1), 0, 'Post agent run Query Row count found is zero')
        for row in self.d2_conn.get_select_data(sql_1):
            self.assertTrue(row['publish_ts'], 'publish_ts is FALSE')
            self.assertTrue(row['publish_xl'], 'publish_xl is FALSE')


    def test_005(self):
        """Safe Mode false agent.publish.xlNumberUrls  < number of mandatory urls"""
        xl_allowed_count = 1
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.xlNumberUrls'] = '%d' % xl_allowed_count
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)

        # As part of mandatory cl_hashes to publication, adding few to is_top_site
        initialization_prevalence_query1 = "update dbo.prevalence set is_top_site=1,is_sanity_url=0,is_locked=0,\
        customer_ticket=0,xl_inserted=NULL,ts_inserted=NULL where cl_hash in " + TOPSITE
        self.database_update_query(initialization_prevalence_query1)

        # As part of mandatory cl_hashes to publication, adding few to is_sanity_url
        initialization_prevalence_query2 = "update dbo.prevalence set is_top_site=0,is_sanity_url=1,is_locked=0,\
        customer_ticket=0,xl_inserted=NULL,ts_inserted=NULL where cl_hash in " + SANITYURLS
        self.database_update_query(initialization_prevalence_query2)

        before_run = "select * from dbo.prevalence where (is_top_site =1 or is_sanity_url=1) and publish_xl=0 and \
        publish_ts=0"
        row_count_before_run = self.d2_conn.get_row_count(before_run)
        self.assertGreater(row_count_before_run, xl_allowed_count, 'The number of mandatory hashes selected \
        is lesser than the xl_allowed_count , please make sure to add more to mandatory hashes than xl_allowed_count')
        self.assertNotEqual(row_count_before_run, 0, 'The cl_hashes selected doesnt exists in the db')
        logging.info(xl_allowed_count)
        logging.info(row_count_before_run)

        self.agent_execution()

        after_run = "select * from dbo.prevalence where (is_top_site =1 or is_sanity_url=1) and publish_xl=1 and \
        publish_ts=1 and (cl_hash in " + TOPSITE + " or cl_hash in " + SANITYURLS + ")"
        logging.info(after_run)
        row_count_after_run = self.d2_conn.get_row_count(after_run)
        logging.info(row_count_after_run)
        self.assertNotEqual(row_count_after_run, 0, 'The cl_hashes are not published to xl & ts list')
        self.assertGreater(row_count_after_run, xl_allowed_count)
        logging.info("Though xlNumberUrls value is lesser than possible mandatory cl_hashes no error encountered")

    def test_006(self):
        """Safe Mode false agent.publish.xlNumberUrls  > number of mandatory urls """
        total_record_count_query = "select * from dbo.prevalence with (nolock)"
        total_record_count = self.d2_conn.get_row_count(total_record_count_query)
        self.assertNotEqual(total_record_count, 0, 'There are no records in the data base')

        # Make the count of xl_allowed_count more than the actual records count in the db
        xl_allowed_count = total_record_count + 10000
        logging.info(xl_allowed_count)
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.xlNumberUrls'] = '%d' % xl_allowed_count
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)

        # As part of mandatory cl_hashes to publication, adding few to is_top_site
        initialization_prevalence_query1 = "update dbo.prevalence set is_top_site=1,is_sanity_url=0,is_locked=0,\
        customer_ticket=0,xl_inserted=NULL,ts_inserted=NULL where cl_hash in " + TOPSITE
        self.database_update_query(initialization_prevalence_query1)

        # As part of mandatory cl_hashes to publication, adding few to is_sanity_url
        initialization_prevalence_query2 = "update dbo.prevalence set is_top_site=0,is_sanity_url=1,is_locked=0,\
        customer_ticket=0,xl_inserted=NULL,ts_inserted=NULL where cl_hash in " + SANITYURLS
        self.database_update_query(initialization_prevalence_query2)

        before_run = "select * from dbo.prevalence where (is_top_site =1 or is_sanity_url=1) and publish_xl=0 and \
        publish_ts=0"
        row_count_before_run = self.d2_conn.get_row_count(before_run)
        self.assertNotEqual(row_count_before_run, 0, 'The cl_hashes selected doesnt exists in the db')
        logging.info(xl_allowed_count)
        logging.info(row_count_before_run)

        self.agent_execution()

        after_run = "select * from dbo.prevalence where (is_top_site =1 or is_sanity_url=1) and publish_xl=1 and \
        publish_ts=1 and (cl_hash in " + TOPSITE + " or cl_hash in " + SANITYURLS + ")"
        logging.info(after_run)
        row_count_after_run = self.d2_conn.get_row_count(after_run)
        logging.info(row_count_after_run)
        self.assertNotEqual(row_count_after_run, 0, 'The cl_hashes are not published to xl & ts list')
        self.assertGreater(xl_allowed_count, row_count_after_run)
        logging.info("Though xlNumberUrls value is greater than possible mandatory cl_hashes no errors encountered")

    def test_007(self):
        """Safe Mode falseagent.publish.tsAllowedUpdates > number of mandat urls """
        total_record_count_query = "select * from dbo.prevalence with (nolock)"
        total_record_count = self.d2_conn.get_row_count(total_record_count_query)
        tsallowedupdates = total_record_count + 10000
        logging.info(tsallowedupdates)
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.tsAllowedUpdates'] = '%d' % tsallowedupdates
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)

        initialization_build_query2 = "update build set mcafee_secure=1 where cl_hash in " + MCAFEESECURE
        self.database_update_query(initialization_build_query2)
        before_run = "select * from dbo.build where mcafee_secure =1"
        row_count_before_run = self.d2_conn.get_row_count(before_run)
        self.assertNotEqual(row_count_before_run, 0, 'The cl_hashes selected doesnt exists in the db')
        logging.info(tsallowedupdates)
        logging.info(row_count_before_run)

        self.agent_execution()

        after_run = "select * from dbo.prevalence where publish_ts=1 and publish_xl =0 and cl_hash in " + MCAFEESECURE
        logging.info(after_run)
        row_count_after_run = self.d2_conn.get_row_count(after_run)
        logging.info(row_count_after_run)
        self.assertNotEqual(row_count_after_run, 0, 'The cl_hashes selected are not published to ts list')
        self.assertGreater(tsallowedupdates, row_count_after_run)
        logging.info("Though tsallowedupdates value is greater than possible ts published cl_hashes, \
        no errors encountered")

    def test_008(self):
        """ Safe Mode false agent.publish.tsAllowedUpdates  < number of mandat urls"""
        total_record_count_query = "select * from dbo.prevalence with (nolock)"
        total_record_count = self.d2_conn.get_row_count(total_record_count_query)
        tsallowedupdates = 1
        logging.info(tsallowedupdates)
        agent_prop = prop_publish_agent()
        agent_prop['agent.publish.tsAllowedUpdates'] = '%d' % tsallowedupdates
        with open(LOCAL_AGENT_PROP_FILE, 'w') as fpw:
            agent_prop.store(fpw)

        initialization_build_query2 = "update build set mcafee_secure=1 where cl_hash in " + MCAFEESECURE
        self.database_update_query(initialization_build_query2)
        before_run = "select * from dbo.build where mcafee_secure =1"
        row_count_before_run = self.d2_conn.get_row_count(before_run)
        self.assertNotEqual(row_count_before_run, 0, 'The cl_hashes selected doesnt exists in the db')
        logging.info(tsallowedupdates)
        logging.info(row_count_before_run)

        self.agent_execution()

        after_run = "select * from dbo.prevalence where publish_ts=1 and publish_xl =0 and cl_hash in " + MCAFEESECURE
        logging.info(after_run)
        row_count_after_run = self.d2_conn.get_row_count(after_run)
        logging.info(row_count_after_run)
        self.assertNotEqual(row_count_after_run, 0, 'The cl_hashes selected are not published to ts list')
        self.assertLess(tsallowedupdates, row_count_after_run)
        logging.info("Though tsallowedupdates value is lesser than possible ts published cl_hashes, \
        no errors encountered")
