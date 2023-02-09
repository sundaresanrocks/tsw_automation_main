"""
======================================
Publishing Agent Test Case Automation
======================================
"""

__author__="Sundaresan"

import re
import os
import sys
import time
import logging
import os.path
import datetime

from pymongo import Connection

import runtime
from libx.process import ShellExecutor
from lib.db.mssql import TsMsSqlWrap
from framework.test import SandboxedTest
from libx.pyjavaproperties import Properties


runtime.DB.U2_host = 'tsmindb03.wsrlab'
runtime.DB.D2_host = 'tsmindb03.wsrlab'
runtime.DB.R2_host = 'tsmindb03.wsrlab'
runtime.DB.T_host = 'tsmindb03.wsrlab'
runtime.DB.T_name = 'telemetry'
runtime.DB.T_user = 'sa'
runtime.DB.T_pass = '1qazse4'
runtime.DB.T_telemetry_tables = 'active_tables'

APP_PROP = '/opt/sftools/conf/application.properties'
BIN_START_AGENT = '/opt/sftools/bin/QueueUrlsClHashOnPrevalenceQueue.sh'
LOG_FILE_AGENT = '/opt/sftools/log/agents.log'
LOCAL_AGENT_PROP_FILE = 'agent.properties'
SH_JAVA_AGENT = BIN_START_AGENT + ' %s' % LOCAL_AGENT_PROP_FILE
CUSTOMER_TICKET_SCRIPT = '/opt/sftools/bin/PrevalenceSetCustomerTicketClient.sh'
DB_CLEAN_UP = ''

## Hard coding these values for testing purpose.
TOP_SITE_URLS_COUNT = 23271
SANITY_URLS_COUNT = 4
VALID_SANITY_URL_PATH = '/opt/sftools/bin/sanityfile.txt'
INVALID_SANITY_URL_PATH = '/opt/sftools/bin/sanityfile_invalid.txt'
VALID_EMPTY_SANITY_URL_PATH = '/opt/sftools/bin/sanityfile_empty.txt'
VALID_SANITY_URL_NEWLINES_AT_STARTING_PATH = '/opt/sftools/bin/sanity_url_newlines_at_starting.txt'
VALID_SANITY_URL_NEWLINES_IN_BETWEEN_PATH = '/opt/sftools/bin/sanity_url_newlines_in_between.txt'
VALID_SANITY_URL_NEWLINES_AT_END_PATH = '/opt/sftools/bin/sanity_url_newlines_at_end.txt'

VALID_TOPSITE_COLLECTION = 'top_site'
VALID_EMPTY_TOPSITE_COLLECTION = 'topsite_empty'

def get_default_application_properties(write_bool=True):
    prop = Properties()

    prop['mssql.telemetry.host'] = runtime.DB.T_host
    prop['mssql.telemetry.db'] = runtime.DB.T_name
    prop['mssql.telemetry.username'] = runtime.DB.T_user
    prop['mssql.telemetry.password'] = runtime.DB.T_pass
    prop['mssql.telemetry.telemetryTables'] = runtime.DB.T_telemetry_tables

    prop['mssql.u2.host'] = runtime.DB.U2_host
    prop['mssql.u2.db'] = 'U2'
    prop['mssql.u2.username'] = runtime.DB.U2_user
    prop['mssql.u2.password'] = runtime.DB.U2_pass

    prop['mssql.d2.host'] = runtime.DB.D2_host
    prop['mssql.d2.db'] = 'D2'
    prop['mssql.d2.username'] = runtime.DB.D2_user
    prop['mssql.d2.password'] = runtime.DB.D2_pass

    prop['mssql.r2.host'] = runtime.DB.R2_host
    prop['mssql.r2.db'] = 'R2'
    prop['mssql.r2.username'] = runtime.DB.R2_user
    prop['mssql.r2.password'] = runtime.DB.R2_pass

    prop['mongodb.topsite.host'] = 'tsqamongodb01.wsrlab'
    prop['mongodb.topsite.port'] = '27017'
    #prop['mongodb.topsite.database'] = 'topsites'
    prop['mongodb.topsite.database'] = 'topsites_test_rb'
    prop['mongodb.topsite.collection'] = 'top_site'

    prop['sanityFile'] = '/opt/sftools/bin/sanityfile.txt'

    if write_bool:
        with open(APP_PROP, 'w') as fpw:
            prop.store(fpw)
    return prop
    

class QueueLoader(SandboxedTest):
    """ Class for dealing with agents related cleanup actions - copying agents.log to sandbox directory """

    def database_reset(self):
        """ Resets PrevalenceQueue bits and inserted dates in db """
        try:
            d2_conn = TsMsSqlWrap('TELEMETRY')
            sql = "truncate table PrevalenceQueue"
            d2_conn.execute_sql_commit(sql)
            logging.info("PrevalenceQueue table truncated")
        except :
            logging.info('Exception while resetting db : PrevalenceQueue.database_reset')
            return False
        return True

    def agent_execution(self):
        """ Executing Publishing Agent """
        # Check if agent is free or not
        query = "select is_running from D2.dbo.active_agents (nolock) where agent_name='Publish'"
        val = self.d2_conn.get_select_data(query)
        logging.info('Publishing Agent is_running value from active_agents = %s '%(val))
        if val[0]['is_running']:
            sys.exit('D2.active_agents.Publish.is_running bit is locked. Agent is currently active')
        else:
            logging.info('Running Publishing Agent')
            stdo, stderr = ShellExecutor.run_wait_standalone(SH_JAVA_AGENT)
            if not stderr:
                logging.error('ERRORS Found while running the agent. Please resolve them manually \n %s'%(stderr))
                sys.exit('ERROR while running Publishing Agent')
        return (stdo, stderr)

    def mongodb_connect(self):
        connection = Connection('tsqamongodb01.wsrlab', 27017) #Connect to mongodb
        print(connection.database_names())  #Return a list of db, equal to: > show dbs
        db = connection['topsites_test_rb']          #equal to: > use testdb1
        print(db.collection_names())        #Return a list of collections in 'testdb1'
        print("top_site" in db.collection_names())     #Check if collection "posts"
        collection = db['top_site']
        logging.info(collection.count())
        count = collection.count()
        return count

    def customer_ticket_execution(self,arg):
        """ Executing customer ticket """
        logging.info('Running customer ticket')
        CUSTOMER_TICKET_SCRIPT = '/opt/sftools/bin/PrevalenceSetCustomerTicketClient.sh'
        CUSTOMER_TICKET_SCRIPT = CUSTOMER_TICKET_SCRIPT +' '+ arg
        stdo, stderr = ShellExecutor.run_wait_standalone(CUSTOMER_TICKET_SCRIPT)
        return stdo, stderr

    def queue_loader_execution(self):
        """ Executing queue loader """
        logging.info('Running queue loader script')
        BIN_START_AGENT = '/opt/sftools/bin/QueueUrlsClHashOnPrevalenceQueue.sh'
        stdo, stderr = ShellExecutor.run_wait_standalone(BIN_START_AGENT)
        return stdo, stderr

    def datetime_diff(self, dt):
        """ Validates if dates lie in past 5000 sec range """
        dt_now = datetime.datetime.now()
        d1_ts = time.mktime(dt_now.timetuple())
        d2_ts = time.mktime(dt.timetuple())
        if int(d1_ts-d2_ts) <= 3600:
            return True
        else:
            return False

    def isFileExist(self, filewithPath):
        if isinstance(filewithPath, str):
            # pattern = r'^/'
            # match = re.search(pattern, filewithPath)       
            # if match:
            return os.path.isfile(filewithPath)
        else:
            logging.error('Argument filewithPath is not string type : %s'%(type(filewithPath)))
            return 0

    def database_update_query(self, query):
        if not query:
            logging.error("Query Positional Argument is not supplied or is Empty")
            return False
        else:
            arg = query
            if isinstance(query, str):        
                self.d2_conn.execute_sql_commit(query)
                logging.info('TestCase data setup done [%s]'%(query))
                # logging.debug('Updated rows from database follows : \n %s'%(self.d2_conn.get_row_count(query)))
            else:
                logging.error('Argument [%s] is not string type : %s'%(arg, type(filewithPath)))
                return 0
            return True

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        # Db Cleanup and then
        self.database_reset()


    def tearDown(self):
        """ Teardown testcase before running the next one """
        # close connection
        pass

    ### Give assert failure Resons as third parameter in assert statement
    def test_01(self):
        """TS-1850:Prevalence Queue Loader: Check executable exists or not"""
        self.assertTrue(self.isFileExist(BIN_START_AGENT), 'Queue loader scripts does not exists')

    def test_02(self):
        """TS-1851:Prevalence Queue Loader: Check if the application.properties exist or not"""
        self.assertTrue(self.isFileExist(APP_PROP), 'Application property file does not exists')

    def test_03(self):
        """TS-1852:Prevalence Queue Loader: Check if the application.properties is configured as required"""
        # Creating application.properties file
        application_prop = get_default_application_properties()
        application_prop = get_default_application_properties()
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        self.assertTrue(self.isFileExist(APP_PROP), 'application.properties file DO NOT exist [%s]'%(APP_PROP))

        self.assertTrue(application_prop['mssql.telemetry.host'], 'mssql.telemetry.host doesnt exists')
        self.assertTrue(application_prop['mssql.telemetry.db'], 'mssql.telemetry.db doesnt exists')
        self.assertTrue(application_prop['mssql.telemetry.username'], 'mssql.telemetry.username doesnt exists')
        self.assertTrue(application_prop['mssql.telemetry.password'], 'mssql.telemetry.password doesnt exists')
        self.assertTrue(application_prop['mssql.telemetry.telemetryTables'], 'mssql.telemetry.telemetryTables doesnt exists')

        self.assertTrue(application_prop['mongodb.topsite.host'], 'mongodb.topsite.host doesnt exists')
        self.assertTrue(application_prop['mongodb.topsite.port'], 'mongodb.topsite.port doesnt exists')
        self.assertTrue(application_prop['mongodb.topsite.database'], 'mongodb.topsite.database doesnt exists')
        self.assertTrue(application_prop['mongodb.topsite.collection'], 'mongodb.topsite.collection doesnt exists')


    def test_04(self):
        """TS-1854:Prevalence Queue Loader: All top site URLs are queued from Mongo DB"""
        application_prop = get_default_application_properties()
        application_prop['sanityFile'] = VALID_EMPTY_SANITY_URL_PATH
        application_prop['mongodb.topsite.collection'] = VALID_TOPSITE_COLLECTION
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        d2_conn = TsMsSqlWrap('TELEMETRY')
        TOP_SITE_URLS_COUNT = self.mongodb_connect()
        stdo,stderr = self.queue_loader_execution()
        topsite_queue_pattern = 'Starting to add TopSites URLs cl_hash to PrevalenceQueue.'
        self.assertTrue(re.search(topsite_queue_pattern,stdo,re.I|re.M),"Exception encountered \
        sanity url queue not started")
        queue_completion_pattern = 'Completed queuing TopSites and SanityURLs.'
        self.assertTrue(re.search(queue_completion_pattern,stdo,re.I|re.M),"Exception encountered \
        queuing TopSites and SanityURLs not completed")

        top_site_queue_validation = "select * from PrevalenceQueue (nolock)"
        logging.info(d2_conn.get_row_count(top_site_queue_validation))
        self.assertEqual(d2_conn.get_row_count(top_site_queue_validation), TOP_SITE_URLS_COUNT, 'topsites urls \
        not queued')

    def test_05(self):
        """TS-1853:Prevalence Queue Loader: All sanity URLs are queued"""
        application_prop = get_default_application_properties()
        application_prop['sanityFile'] = VALID_SANITY_URL_PATH
        application_prop['mongodb.topsite.collection'] = VALID_EMPTY_TOPSITE_COLLECTION
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        d2_conn = TsMsSqlWrap('TELEMETRY')

        stdo,stderr = self.queue_loader_execution()
        sanity_queue_pattern = 'Starting to add Sanity URLs cl_hash to PrevalenceQueue.'
        self.assertTrue(re.search(sanity_queue_pattern,stdo,re.I|re.M),"Exception encountered \
        sanity url queue not started")
        queue_completion_pattern = 'Completed queuing TopSites and SanityURLs.'
        self.assertTrue(re.search(queue_completion_pattern,stdo,re.I|re.M),"Exception encountered \
        queuing TopSites and SanityURLs not completed")

        sanity_queue_validation = "select * from PrevalenceQueue (nolock)"
        logging.info(d2_conn.get_row_count(sanity_queue_validation))
        self.assertEqual(d2_conn.get_row_count(sanity_queue_validation), SANITY_URLS_COUNT, 'Sanity urls \
        not queued')

    def test_06(self):
        """TS-1856:Prevalence Queue Loader: Duplicates are allowed in the queue"""
        application_prop = get_default_application_properties()
        application_prop['sanityFile'] = VALID_SANITY_URL_PATH
        application_prop['mongodb.topsite.collection'] = VALID_EMPTY_TOPSITE_COLLECTION
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        d2_conn = TsMsSqlWrap('TELEMETRY')

        stdo,stderr = self.queue_loader_execution()
        sanity_queue_pattern = 'Starting to add Sanity URLs cl_hash to PrevalenceQueue.'
        self.assertTrue(re.search(sanity_queue_pattern,stdo,re.I|re.M),"Exception encountered \
        sanity url queue not started")
        queue_completion_pattern = 'Completed queuing TopSites and SanityURLs.'
        self.assertTrue(re.search(queue_completion_pattern,stdo,re.I|re.M),"Exception encountered \
        queuing TopSites and SanityURLs not completed")

        ## Running the agent again to ensure duplicates are added
        stdo,stderr = self.queue_loader_execution()

        sanity_queue_validation = "select * from PrevalenceQueue (nolock)"
        logging.info(d2_conn.get_row_count(sanity_queue_validation))
        self.assertEqual(d2_conn.get_row_count(sanity_queue_validation), SANITY_URLS_COUNT*2, 'Sanity urls \
        not queued')

    def test_07(self):
        """TS-1842 Prevalence Queue Loader:PrevalenceQueueLoader_Queue_Check_Sanity_Valid_TopSite_Empty:\
        Sanity URL list is not empty and valid.Top_site collection is empty"""
        application_prop = get_default_application_properties()
        application_prop['sanityFile'] = VALID_SANITY_URL_PATH
        application_prop['mongodb.topsite.collection'] = VALID_EMPTY_TOPSITE_COLLECTION
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        d2_conn = TsMsSqlWrap('TELEMETRY')

        stdo,stderr = self.queue_loader_execution()
        sanity_queue_pattern = 'Starting to add Sanity URLs cl_hash to PrevalenceQueue.'
        self.assertTrue(re.search(sanity_queue_pattern,stdo,re.I|re.M),"Exception encountered \
        sanity url queue not started")
        queue_completion_pattern = 'Completed queuing TopSites and SanityURLs.'
        self.assertTrue(re.search(queue_completion_pattern,stdo,re.I|re.M),"Exception encountered \
        queuing TopSites and SanityURLs not completed")

        sanity_queue_validation = "select * from PrevalenceQueue (nolock)"
        logging.info(d2_conn.get_row_count(sanity_queue_validation))
        self.assertEqual(d2_conn.get_row_count(sanity_queue_validation), SANITY_URLS_COUNT, 'Sanity urls \
        not queued')

    def test_08(self):
        """TS-1843: Prevalence Queue Loader:PrevalenceQueueLoader_Queus_Count_Check_Sanity_Valid_TopSite_Empty:\
        Sanity URL list is not empty and valid.Top_site collection is empty"""
        application_prop = get_default_application_properties()
        application_prop['sanityFile'] = VALID_SANITY_URL_PATH
        application_prop['mongodb.topsite.collection'] = VALID_EMPTY_TOPSITE_COLLECTION
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        d2_conn = TsMsSqlWrap('TELEMETRY')

        stdo,stderr = self.queue_loader_execution()
        sanity_queue_pattern = 'Starting to add Sanity URLs cl_hash to PrevalenceQueue.'
        self.assertTrue(re.search(sanity_queue_pattern,stdo,re.I|re.M),"Exception encountered \
        sanity url queue not started")
        queue_completion_pattern = 'Completed queuing TopSites and SanityURLs.'
        self.assertTrue(re.search(queue_completion_pattern,stdo,re.I|re.M),"Exception encountered \
        queuing TopSites and SanityURLs not completed")

        sanity_queue_validation = "select * from PrevalenceQueue (nolock)"
        logging.info(d2_conn.get_row_count(sanity_queue_validation))
        self.assertEqual(d2_conn.get_row_count(sanity_queue_validation), SANITY_URLS_COUNT, 'Sanity urls \
        not queued')


    def test_09(self):
        """TS-1844: Prevalence Queue Loader:PrevalenceQueueLoader_Queue_Check_Sanity_Valid_TopSite_Invalid:\
        Sanity URL list is not empty and valid.Top_site collection is invalid ie doesn’t exists"""
        application_prop = get_default_application_properties()
        application_prop['sanityFile'] = VALID_SANITY_URL_PATH
        application_prop['mongodb.topsite.collection'] = VALID_EMPTY_TOPSITE_COLLECTION
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        d2_conn = TsMsSqlWrap('TELEMETRY')

        stdo,stderr = self.queue_loader_execution()
        sanity_queue_pattern = 'Starting to add Sanity URLs cl_hash to PrevalenceQueue.'
        self.assertTrue(re.search(sanity_queue_pattern,stdo,re.I|re.M),"Exception encountered \
        sanity url queue not started")
        queue_completion_pattern = 'Completed queuing TopSites and SanityURLs.'
        self.assertTrue(re.search(queue_completion_pattern,stdo,re.I|re.M),"Exception encountered \
        queuing TopSites and SanityURLs not completed")

        sanity_queue_validation = "select * from PrevalenceQueue (nolock)"
        logging.info(d2_conn.get_row_count(sanity_queue_validation))
        self.assertEqual(d2_conn.get_row_count(sanity_queue_validation), SANITY_URLS_COUNT, 'Sanity urls \
        not queued')

    def test_010(self):
        """Prevalence Queue Loader:PevalenceQueueLoader_Queue_Check_Sanity_Empty_TopSite_Valid:Sanity URL \
        list is empty and valid.Top_site collection list is not empty and valid."""
        application_prop = get_default_application_properties()
        application_prop['sanityFile'] = VALID_EMPTY_SANITY_URL_PATH
        application_prop['mongodb.topsite.collection'] = VALID_TOPSITE_COLLECTION
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        d2_conn = TsMsSqlWrap('TELEMETRY')
        TOP_SITE_URLS_COUNT = self.mongodb_connect()

        stdo,stderr = self.queue_loader_execution()
        sanity_queue_pattern = 'Starting to add Sanity URLs cl_hash to PrevalenceQueue.'
        self.assertTrue(re.search(sanity_queue_pattern,stdo,re.I|re.M),"Exception encountered \
        sanity url queue not started")
        queue_completion_pattern = 'Completed queuing TopSites and SanityURLs.'
        self.assertTrue(re.search(queue_completion_pattern,stdo,re.I|re.M),"Exception encountered \
        queuing TopSites and SanityURLs not completed")

        sanity_queue_validation = "select * from PrevalenceQueue (nolock)"
        logging.info(d2_conn.get_row_count(sanity_queue_validation))
        self.assertEqual(d2_conn.get_row_count(sanity_queue_validation), TOP_SITE_URLS_COUNT, 'Top site urls \
        not queued')

    def test_011(self):
        """Prevalence Queue Loader:PrevalenceQueueLoader_Queue_Count_Check_Sanity_Empty_TopSite_Valid:Sanity \
        URLs is empty and valid.Top_site collection is not empty and valid path."""
        application_prop = get_default_application_properties()
        application_prop['sanityFile'] = VALID_EMPTY_SANITY_URL_PATH
        application_prop['mongodb.topsite.collection'] = VALID_TOPSITE_COLLECTION
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        d2_conn = TsMsSqlWrap('TELEMETRY')
        TOP_SITE_URLS_COUNT = self.mongodb_connect()
        stdo,stderr = self.queue_loader_execution()
        sanity_queue_pattern = 'Starting to add Sanity URLs cl_hash to PrevalenceQueue.'
        self.assertTrue(re.search(sanity_queue_pattern,stdo,re.I|re.M),"Exception encountered \
        sanity url queue not started")
        queue_completion_pattern = 'Completed queuing TopSites and SanityURLs.'
        self.assertTrue(re.search(queue_completion_pattern,stdo,re.I|re.M),"Exception encountered \
        queuing TopSites and SanityURLs not completed")

        sanity_queue_validation = "select * from PrevalenceQueue (nolock)"
        logging.info(d2_conn.get_row_count(sanity_queue_validation))
        self.assertEqual(d2_conn.get_row_count(sanity_queue_validation), TOP_SITE_URLS_COUNT, 'Top site urls \
        not queued')

    def test_012(self):
        """Prevalence Queue Loader:PrevalenceQueueLoader_Queue_Check_Sanity_Invalid_TopSite_Valid:Sanity \
        URLs is empty and invalidTop_site collection is not empty and valid path"""
        application_prop = get_default_application_properties()
        application_prop['sanityFile'] = INVALID_SANITY_URL_PATH
        application_prop['mongodb.topsite.collection'] = VALID_TOPSITE_COLLECTION
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        d2_conn = TsMsSqlWrap('TELEMETRY')

        stdo,stderr = self.queue_loader_execution()
        sanity_queue_pattern = 'java.io.IOException: Sanity file /opt/sftools/bin/sanityfile_invalid.txt does not exist. Exiting'
        self.assertTrue(re.search(sanity_queue_pattern,stderr,re.I|re.M),"Exception not encountered for \
        invalid Sanity URL path sanity url queue not started")
        queue_completion_pattern = 'Completed queuing TopSites and SanityURLs.'
        self.assertFalse(re.search(queue_completion_pattern,stdo,re.I|re.M),"Exception not encountered \
        queuing TopSites and SanityURLs")

        sanity_queue_validation = "select * from PrevalenceQueue (nolock)"
        logging.info(d2_conn.get_row_count(sanity_queue_validation))
        self.assertEqual(d2_conn.get_row_count(sanity_queue_validation), 0, 'Top site urls \
        are queued')

    def test_013(self):
        """Prevalence Queue Loader:PrevalenceQueueLoader_Queue_Check_Sanity_Valid_TopSite_Valid:Sanity \
        URLs list is not empty and valid.Top_site collection is not empty and valid"""
        application_prop = get_default_application_properties()
        application_prop['sanityFile'] = VALID_SANITY_URL_PATH
        application_prop['mongodb.topsite.collection'] = VALID_TOPSITE_COLLECTION
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        d2_conn = TsMsSqlWrap('TELEMETRY')
        TOP_SITE_URLS_COUNT = self.mongodb_connect()
        stdo,stderr = self.queue_loader_execution()
        sanity_queue_pattern = 'Starting to add Sanity URLs cl_hash to PrevalenceQueue.'
        self.assertTrue(re.search(sanity_queue_pattern,stdo,re.I|re.M),"Exception encountered \
        sanity url queue not started")
        queue_completion_pattern = 'Completed queuing TopSites and SanityURLs.'
        self.assertTrue(re.search(queue_completion_pattern,stdo,re.I|re.M),"Exception encountered \
        queuing TopSites and SanityURLs not completed")

        sanity_queue_validation = "select * from PrevalenceQueue (nolock)"
        logging.info(d2_conn.get_row_count(sanity_queue_validation))
        self.assertEqual(d2_conn.get_row_count(sanity_queue_validation), TOP_SITE_URLS_COUNT+SANITY_URLS_COUNT, 'Top \
        site and sanity urls not queued')

    def test_014(self):
        """Prevalence Queue Loader:PrevalenceQueueLoader_Queue_Count_Check_Sanity_Valid_TopSite_Valid:Sanity \
        URLs list is not empty and valid.Top_site collection is not empty and valid"""
        application_prop = get_default_application_properties()
        application_prop['sanityFile'] = VALID_SANITY_URL_PATH
        application_prop['mongodb.topsite.collection'] = VALID_TOPSITE_COLLECTION
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        d2_conn = TsMsSqlWrap('TELEMETRY')
        TOP_SITE_URLS_COUNT = self.mongodb_connect()
        stdo,stderr = self.queue_loader_execution()
        sanity_queue_pattern = 'Starting to add Sanity URLs cl_hash to PrevalenceQueue.'
        self.assertTrue(re.search(sanity_queue_pattern,stdo,re.I|re.M),"Exception encountered \
        sanity url queue not started")
        queue_completion_pattern = 'Completed queuing TopSites and SanityURLs.'
        self.assertTrue(re.search(queue_completion_pattern,stdo,re.I|re.M),"Exception encountered \
        queuing TopSites and SanityURLs not completed")

        sanity_queue_validation = "select * from PrevalenceQueue (nolock)"
        logging.info(d2_conn.get_row_count(sanity_queue_validation))
        self.assertEqual(d2_conn.get_row_count(sanity_queue_validation), TOP_SITE_URLS_COUNT+SANITY_URLS_COUNT, 'Top \
        site and sanity urls not queued')

    def test_015(self):
        """TS-1857:Customer Ticket: Script is present"""
        self.assertTrue(self.isFileExist(CUSTOMER_TICKET_SCRIPT), 'Customer ticket script does not exists')

    def test_016(self):
        """ TS-1860:Customer Ticket: Future date"""
        stdo,stderr = self.customer_ticket_execution('20540701')
        pattern = 'Finish updating Customer Ticket cl_hash in prevalence table.'
        self.assertTrue(re.search(pattern,stdo,re.I|re.M),"An exception encountered.")

    def test_017(self):
        """ TS-1859:Customer Ticket: Invalid date"""
        stdo,stderr = self.customer_ticket_execution('2511111111')
        pattern = 'java.sql.SQLException: Conversion failed when converting date and/or time from character string.'
        self.assertTrue(re.search(pattern,stderr,re.I|re.M),"No or inappropriate exception thrown on invaliddate input")

    def test_018(self):
        """ TS-1861:Customer Ticket: specific date"""
        stdo,stderr = self.customer_ticket_execution('20140701')
        pattern = 'java.sql.SQLException: Conversion failed when converting date and/or time from character string.'
        self.assertFalse(re.search(pattern,stderr,re.I|re.M),"exception thrown on valid date input")

    def test_019(self):
        """ Sanity File with empty lines in beginning"""
        application_prop = get_default_application_properties()
        application_prop['sanityFile'] = VALID_SANITY_URL_NEWLINES_AT_STARTING_PATH
        application_prop['mongodb.topsite.collection'] = VALID_TOPSITE_COLLECTION
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        d2_conn = TsMsSqlWrap('TELEMETRY')

        stdo,stderr = self.queue_loader_execution()
        sanity_queue_pattern = 'Canonicalization error for url : java.lang.IllegalArgumentException: IRI_sc_parse: Missing required domain name'
        self.assertTrue(re.search(sanity_queue_pattern,stderr,re.I|re.M),"Exception not encountered for sanity URLs\
        with new line the the beginning")

    def test_020(self):
        """ Sanity File with empty lines in between the urls"""
        application_prop = get_default_application_properties()
        application_prop['sanityFile'] = VALID_SANITY_URL_NEWLINES_IN_BETWEEN_PATH
        application_prop['mongodb.topsite.collection'] = VALID_TOPSITE_COLLECTION
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        d2_conn = TsMsSqlWrap('TELEMETRY')

        stdo,stderr = self.queue_loader_execution()
        sanity_queue_pattern = 'Canonicalization error for url : java.lang.IllegalArgumentException: IRI_sc_parse: Missing required domain name'
        self.assertTrue(re.search(sanity_queue_pattern,stderr,re.I|re.M),"Exception not encountered for \
        Sanity File with empty lines in between the urls")


    def test_021(self):
        """ Sanity File with empty lines at the end of the file"""
        application_prop = get_default_application_properties()
        application_prop['sanityFile'] = VALID_SANITY_URL_NEWLINES_AT_END_PATH
        application_prop['mongodb.topsite.collection'] = VALID_TOPSITE_COLLECTION
        with open(APP_PROP, 'w') as fpw:
            application_prop.store(fpw)

        d2_conn = TsMsSqlWrap('TELEMETRY')

        stdo,stderr = self.queue_loader_execution()
        sanity_queue_pattern = 'Canonicalization error for url : java.lang.IllegalArgumentException: IRI_sc_parse: Missing required domain name'
        self.assertTrue(re.search(sanity_queue_pattern,stderr,re.I|re.M),"Exception not encountered for \
        Sanity File with empty lines at the end of the file")