"""
===============================================
         List Build Test Case Automation
===============================================
"""

__author__ = 'avimehenwal'

import os
import re
import pprint
import logging
import os.path
from path import Path
import runtime
import lib.miscellaneous
from lib.build import Build
from lib.build import *
from libx.process import ShellExecutor
from lib.db.mssql import TsMsSqlWrap
from framework.test import SandboxedTest
from lib.db.telemetrydb import PrevalenceTable
from lib.utils import db_reset
from  prevalence import test_publish_agent
import subprocess
from  libx.ssh import SSHConnection

#db_reset.db_reset()

# Global configurations and environment settings for build
BUILD_HOST = runtime.BuildSys.system
BUILD_USER = runtime.BuildSys.user
SFDBSERVERU2 = runtime.DB.U2_name
SFDBSERVERD2 = runtime.DB.D2_name
SFDBSERVERR2 = runtime.DB.R2_name
BUILD_AGENT = runtime.LIST.build_agent
TS = str(runtime.LIST.ts_db)
XL = str(runtime.LIST.xl_db)
build_script_path = runtime.BuildSys.build_dir


# Build Sanity File Test Data and url Data File
sanity_contents_valid = "*://ENROLAR.RU su"
sanity_contents_invalid = "*://ENROLAR.RU ph"
sanity_contents_skipped ="*://ENROLAR.RU ci"
test_urls = str(Path.joinpath(runtime.data_path, 'build_publication', 'urls.txt'))


# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def sfimport_insert_urls(filePath=test_urls):
    """ Inserts urls present in urls.txt to U2 database """
    # runtime.BIN.sfimport
    cmd = "/usr2/smartfilter/import/sfimport -a 81 -H 'hits' -f u -i -l " + filePath + " -c ch -L French"
    stdo, stderr = ShellExecutor.run_wait_standalone(cmd)
    # logging.info("stdo=%s\nstderr=%s" % (stdo, stderr))
    return stdo


def sfimport_delete_urls(filePath=test_urls):
    """ Deletes urls from urls.txt in U2 database """
    cmd = "/usr2/smartfilter/import/sfimport -a  81 -f u -d -l " + filePath + " -H 'hits' -L French"
    stdo, stderr = ShellExecutor.run_wait_standalone(cmd)
    # logging.info("stdo=%s\nstderr=%s" %(stdo, stderr))
    return stdo

def run_build_cmd(cmd):
    """ Run the command on build system and return the output of command """
    system = runtime.BuildSys.system
    logging.debug("Build system is")
    logging.debug(system)
    ssh = runtime.get_ssh(system, 'sfcontrol')
    _cmd = "%(ssh)s SHELL=/bin/bash; %(sh_build)s" % (
        {'sh_build': cmd,
         'ssh': runtime.ENV.get_env_for_ssh_cmd()})
    stdout, stderr = ssh.execute(_cmd)
    if stderr == '':
        return stdout

def setup_build_script():
    """ Runs setup_build_script on host as sfcontrol """
    return run_build_cmd(runtime.SH.setup_build_script)

def reset_list_build():
    """This function will reset the build process"""
    # if self.is_state_resume():        [avi] commented as its useless check
    d2_conn = TsMsSqlWrap('D2')
    db_initialization_prevalence = "update prevalence set is_top_site=0,is_locked=0,is_sanity_url=0,customer_ticket=0,publish_xl=0, \
    publish_ts=0,last_checked =NULL,last_seen=NULL,xl_removed=NULL,ts_removed=NULL,xl_inserted=NULL,ts_inserted=NULL"

    logging.debug("Build Reset in progress.")
    system = runtime.BuildSys.system
    ssh = runtime.get_ssh(system, 'sfcontrol')
    _cmd = "%(ssh)s SHELL=/bin/bash; %(sh_build)s %(reset)s" % (
        {'sh_build': runtime.SH.build_lists,
         'reset': 'reset',
         'ssh': runtime.ENV.get_env_for_ssh_cmd()
        })
    _xlcmd = "%(ssh)s SHELL=/bin/bash; %(command)s" % (
        {'command': "rm /usr2/smartfilter/build/xl/*",
         'ssh': runtime.ENV.get_env_for_ssh_cmd()
        })
    _tscmd = "%(ssh)s SHELL=/bin/bash; %(command)s" % (
        {'command': "rm /usr2/smartfilter/build/ts/* && touch /usr2/smartfilter/build/ts/TS4.3_URLS.txt",
         'ssh': runtime.ENV.get_env_for_ssh_cmd()
        })

    build_out, build_err = ssh.execute(_cmd)
    xl_out, xl_err = ssh.execute(_xlcmd)
    ts_out, ts_err = ssh.execute(_tscmd)
    d2_conn.execute_sql_commit(db_initialization_prevalence)
    test_publish_agent.PublishingAgentSandbox.agent_execution()
    remote_connect = SSHConnection("localhost", username="sfcontrol", password="1qazse4")
    stdout_str, stderr_str = remote_connect.execute("cd /usr2/smartfilter/build && export SFDBSERVERD2=hil-wsr-q-dci01_D2 && export SFDBSERVERU2=hil-wsr-q-dci01_U2 \
    && export SFDBSERVERR2=hil-wsr-q-dci01_R2 && /usr2/smartfilter/build/setup_build_script.sh")
    logging.info(stdout_str)
    return build_out,build_err

def run_agents():
    """ Starts TMAN Agent to push queued urls from U2 to D2  """
    stdo, stderr = ShellExecutor.run_wait_standalone("/usr2/smartfilter/dbtools/tman -n 3")
    # logging.info("stdo=%s\nstderr=%s" %(stdo, stderr))
    stdo, stderr = ShellExecutor.run_wait_standalone("/usr2/smartfilter/dbtools/wrua -t 5 -n 10 -D")
    # logging.info("stdo=%s\nstderr=%s" %(stdo, stderr))
    stdo, stderr = ShellExecutor.run_wait_standalone("/usr2/smartfilter/dbtools/wrman -t 5 -n 10 -D")
    # logging.info("stdo=%s\nstderr=%s" %(stdo, stderr))

    # [todo :] make use of agents.py file. Environment is different
    # #   Call TMAN Agent
    # tman_obj = Agents('tman')
    # tman_obj.run_agent(" -l 50 -n 2 -t 2 -d -i -s ")
    # logging.info(" TMAN Ran successfully")
    #
    # # Call WRUA Agent
    # wrua_obj = Agents('wrua')
    # wrua_obj.run_agent("-n 50 -t 2 ")
    # logging.info(" WRUA Ran successfully")
    #
    # # Call WRMAN Agent
    # wrman_obj = Agents('wrman')
    # wrman_obj.run_agent(" -n 50 -t 2 ")
    # logging.info(" WRMAN Ran successfully")
    return stdo

def read_file(_path):
    """ Reads the provided file and returns its content """
    fd = open(_path, 'r')
    return fd.read().strip()


class BuildSpecificChecks(object):
    """ Checks If Log files are properly generated every build run """

    def build_loggeneration_checks(self):
        """ Performs assertion checks on build values """
        try:    # If build did not ran or values not set. Console logs are written for all builds
            if not Path.isfile(self.build_values['build_console_log']):
                raise FileNotFoundError("File %s do not exists" % self.build_values['build_console_log'])
        except:
            return False

        if self.build_values['build_type'] == 'migt':
            assert self.build_values['build_master_new'] - self.build_values['build_master_old'] == 0
            if self.build_values['list_type'] == 'xl':
                assert self.build_values['build_xl_new'] - self.build_values['build_xl_old'] == 1
                assert self.build_values['build_ts_new'] - self.build_values['build_ts_old'] == 0
                assert self.build_values['build_xl_new'] > self.build_values['build_xl_old']
            elif self.build_values['list_type'] == 'ts':
                assert self.build_values['build_ts_new'] - self.build_values['build_ts_old'] == 1
                assert self.build_values['build_xl_new'] - self.build_values['build_xl_old'] == 0
                assert self.build_values['build_ts_new'] > self.build_values['build_ts_old']
        if self.build_values['build_type'] == 'master':
            # assert self.b['build_new'] - self.b['build_old'] == 1
            assert self.build_values['build_master_new'] - self.build_values['build_master_old'] == 1
            assert self.build_values['build_ts_new'] - self.build_values['build_ts_old'] == 0
            assert self.build_values['build_xl_new'] - self.build_values['build_xl_old'] == 0
        return True

    def build_listincrements_checks(self):
        """ Checks build lists databases increments for migt builds
        1. [database].current file should exist
        2. Read the value of [database].current file as DBNo
        3. [database].DBNo file should exist
        """
        def check_increments(_path, _list):
            fileName = _list + '.current'
            assert lib.miscellaneous.file_dir_checker(_path, fileName)
            val_fileName = read_file(os.path.join(_path, fileName))
            inc_fileName = _list + '.' + val_fileName
            assert lib.miscellaneous.file_dir_checker(_path, inc_fileName)

        if self.build_values['list_type'] == 'ts':
            check_increments(self.build_values['tsListPath'], self.build_values['tsdatabase'])
            check_increments(self.build_values['tsListPath'], self.build_values['tscontrol'])
        elif self.build_values['list_type'] == 'xl':
            check_increments(self.build_values['xlListPath'], self.build_values['sfcontrol'])
        return True

    def build_consolelogs_checks(self):
        """ Checks for specific pattern from console logs generated by build_list script """
        def search_log(pattern=None):
            """ Searches provided patters in build log files and returns True and False """
            boolean = re.search(pattern, self.build_values['build_out'], re.IGNORECASE)
            assert boolean

        # Build No Run
        if self.build_values['build_out'] == '':
            # raise ValueError('Either build did not ran or build_out not set')
            pass

        # Build Help
        elif self.build_values['build_type'] == '' and self.build_values['list_type'] == '':
            search_log('Usage:')
            search_log('./build_lists.sh master all')
            search_log('./build_lists.sh reset')
            search_log('./build_lists.sh manual <xl|ts|all>')
            search_log('./build_lists.sh migt <xl|ts>')
            search_log('Invalid number of commandline args')

        # Master Build Normal Mode
        elif self.build_values['build_type'] == 'master' and self.build_values['list_type'] == 'all':
            search_log('BuildScript=started')
            search_log('Running in master build mode.')
            search_log('Building TS and XL databases.')
            search_log('Rotating/archiving files from last run....')
            search_log('Generate the MIGT files needed to create a control list via the merge tool...')
            search_log('Running command to create migt files /usr2/smartfilter/build/migt/migt')
            search_log('Creating Prevalence Publication History Data')
            search_log('Testing the newly-created control lists...')
            search_log('Testing XL sfcontrol against XL4.3_URLS.txt sanity file.')
            search_log('Testing tsdatabase against TS4.3_URLS.txt sanity file.')
            search_log('Building incremental files...')
            # search_log('Testing incremental tsdatabase against TS4.3_URLS.txt sanity file.')
            search_log('Testing XL incremental sfcontrol against XL4.3_URLS.txt sanity file.')
            search_log('Staging XL files...')
            search_log('XL Files staged OK.')
            search_log('Staging TS Control files...')
            search_log('TS Control Files staged OK.')
            search_log('Master database built, log file /usr2/smartfilter/build/logs/master/log.')
            search_log('XL_Current_Serial_Num=')
            search_log('TS_Current_Serial_Num=')
            search_log('BuildScript=finished at')

        # Migt XL Normal Mode
        elif self.build_values['build_type'] == 'migt' and self.build_values['list_type'] == 'xl':
            search_log('Building the XL list.')
            search_log('Setting STATE to init')
            search_log('Rotating/archiving files from last run...')
            search_log('Generating control lists via the MIGT tool...')
            search_log('Running command to create migt files /usr2/smartfilter/build/migt/migt')
            search_log('Creating the XL list.')
            search_log('Created XL list.')
            search_log('Cleaning up MIGT files...')
            search_log('List build finished:')
            search_log('Testing the newly-created control lists...')
            search_log('Checking the size of newly-built XL database...')
            search_log('The newly-built XL database size is under the maximum size.')
            search_log('Testing XL sfcontrol against XL4.3_URLS.txt sanity file.')
            search_log('Building incremental files...')
            search_log('List increments finished:')
            search_log('Check for /usr2/smartfilter/build/infofile/xl/.webserv.lock lock files.')
            search_log('Staging XL files...')
            search_log('Done staging files at:')
            search_log('MIGT XL database built, log file /usr2/smartfilter/build/logs/migt/xl/log')
            search_log('XL_Current_Serial_Num=')
            search_log('TS_Current_Serial_Num=')
            search_log('BuildScript=finished at')

        # Migt TS Normal Mode
        elif self.build_values['build_type'] == 'migt' and self.build_values['list_type'] == 'ts':
            search_log('Building the TS list.')
            search_log('Setting STATE to init')
            search_log('Rotating/archiving files from last run....')
            search_log('Generating control lists via the MIGT tool...')
            search_log('Running command to create migt files /usr2/smartfilter/build/migt/migt')
            search_log('Creating the TS list.')
            search_log('Created TS list.')
            search_log('Cleaning up MIGT files...')
            search_log('List build finished:')
            search_log('Testing the newly-created control lists...')
            search_log('Checking the size of newly-built TS database...')
            search_log('The newly-built TS database size is under the maximum size.')
            search_log('Testing tsdatabase against TS4.3_URLS.txt sanity file.')
            search_log('Building incremental files...')
            search_log('List increments finished:')
            search_log(' Check for /usr2/smartfilter/build/infofile/ts/.webserv.lock lock files.')
            search_log('Preparing files for to be moved to staging directory')
            search_log('Done staging files at:')
            search_log('MIGT TS database built, log file /usr2/smartfilter/build/logs/migt/ts/log.')
            search_log('XL_Current_Serial_Num=')
            search_log('TS_Current_Serial_Num=')
            search_log('BuildScript=finished at')

        # Build Reset Mode
        elif self.build_values['build_type'] == 'reset' and self.build_values['list_type'] == '':
            search_log('BuildScript=started at')
            search_log('Running in RESET mode...')
            search_log('Starting to read state file: /usr2/smartfilter/build/.master_build_state')
            search_log('Starting to read state file: /usr2/smartfilter/build/.ts_build_state')
            search_log('Starting to read state file: /usr2/smartfilter/build/.xl_build_state')
            search_log('Starting to read state file: /usr2/smartfilter/build/.sl_build_state')
            search_log('BuildScript=finished at')

        # Master Build Resume Mode
        # Migt TS Resume Mode
        # Migt XL Resume Mode

    def __init__(self, build_dict):
        self.build_values = build_dict
        self.build_consolelogs_checks()
        self.build_loggeneration_checks()
        if self.build_values['build_type'] == 'migt':
            self.build_listincrements_checks()


class BuildNormalMode(SandboxedTest):
    """ Build Run in normal mode Test Cases """

    @classmethod
    def setUpClass(self):
        """ Create environment for which_list bases tests """
        reset_list_build()

    def setUp(self):
        SandboxedTest.setUp(self)
        self.build = Build(build_host=BUILD_HOST)

    def test_norun(self):
        BuildSpecificChecks(self.build.get_build_values())

    def test_help(self):
        self.build.build_help()
        BuildSpecificChecks(self.build.get_build_values())

    def test_master(self):
        self.build.build_run('master', 'all')
        BuildSpecificChecks(self.build.get_build_values())

    def test_xl(self):
        self.build.build_run('migt', 'xl')
        BuildSpecificChecks(self.build.get_build_values())
        pprint.pprint(self.build.get_build_values())

    def test_ts(self):
        self.build.build_run('migt', 'ts')
        BuildSpecificChecks(self.build.get_build_values())


class BuildWhichList(SandboxedTest):
    """ Tests build based on which_;ist values and compares in ts and xl databases """

    @classmethod
    def setUpClass(self):
        """ Create environment for which_list bases tests """
        self.build = Build(build_host=BUILD_HOST)
        logger.info("Build object instantiated")
        self.d2_conn = TsMsSqlWrap('D2')
        logging.info("Connected to DB : %s" %
                     self.d2_conn.get_select_data("select SERVERPROPERTY ('ServerName' ) AS ServerName"))
        sfimport_out = sfimport_insert_urls()
        self.urlIds_urls = re.findall("urlId=(\d+)\W+url\=(?P<name>[\w/.\*\:/\/]+)", sfimport_out)
        logging.info(self.urlIds_urls)
        run_agents()

        sql = list()
        sql.insert(0, "update D2.dbo.build set which_list=99 where url_id=%s" % self.urlIds_urls[0][0])
        sql.insert(1, "update D2.dbo.build set which_list=100 where url_id=%s" % self.urlIds_urls[1][0])
        sql.insert(2, "update D2.dbo.build set which_list=101 where url_id=%s" % self.urlIds_urls[2][0])
        sql.insert(3, "update D2.dbo.build set which_list=299 where url_id=%s" % self.urlIds_urls[3][0])
        sql.insert(4, "update D2.dbo.build set which_list=300 where url_id=%s" % self.urlIds_urls[4][0])
        sql.insert(5, "update D2.dbo.build set which_list=301 where url_id=%s" % self.urlIds_urls[5][0])
        sql.insert(6, "update D2.dbo.build set which_list=311 where url_id=%s" % self.urlIds_urls[6][0])
        sql.insert(7, "update D2.dbo.build set which_list=312 where url_id=%s" % self.urlIds_urls[7][0])
        sql.insert(8, "update D2.dbo.build set which_list=313 where url_id=%s" % self.urlIds_urls[8][0])
        sql.insert(9, "update D2.dbo.build set which_list=399 where url_id=%s" % self.urlIds_urls[9][0])
        sql.insert(10, "update D2.dbo.build set which_list=400 where url_id=%s" % self.urlIds_urls[10][0])
        sql.insert(11, "update D2.dbo.build set which_list=401 where url_id=%s" % self.urlIds_urls[11][0])
        sql.insert(12, "update D2.dbo.build set which_list=411 where url_id=%s" % self.urlIds_urls[12][0])
        sql.insert(13, "update D2.dbo.build set which_list=412 where url_id=%s" % self.urlIds_urls[13][0])
        sql.insert(14, "update D2.dbo.build set which_list=413 where url_id=%s" % self.urlIds_urls[14][0])
        sql.insert(15, "update D2.dbo.build set which_list=499 where url_id=%s" % self.urlIds_urls[15][0])
        sql.insert(16, "update D2.dbo.build set which_list=500 where url_id=%s" % self.urlIds_urls[16][0])
        sql.insert(17, "update D2.dbo.build set which_list=501 where url_id=%s" % self.urlIds_urls[17][0])
        logging.info(sql)

        for query in sql:
            logging.info('EXECUTING QUERY : %s' % query)
            self.d2_conn.execute_sql_commit(query)
        self.output = self.build.build_run('master', 'all')
        BuildSpecificChecks(self.build.get_build_values())

    @classmethod
    def tearDownClass(self):
        """ removes added urls from build table """
        sfimport_delete_urls()
        run_agents()
        logging.info("Removed urls from build table")

    def setUp(self):
        SandboxedTest.setUp(self)

    def tearDown(self):
        SandboxedTest.tearDown(self)

    def test_01(self):
        """ Which list < 100 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[0][1], self.urlIds_urls[0][0]))
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[0][1], XL), 'url present in xl list')
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[0][1], TS), 'url present in ts list')

    def test_02(self):
        """ Which list = 100 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[1][1], self.urlIds_urls[1][0]))
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[1][1], XL), 'url NOT in xl list')
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[1][1], TS), 'url NOT in ts list')

    def test_03(self):
        """ Which list > 100 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[2][1], self.urlIds_urls[2][0]))
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[2][1], XL), 'url NOT in xl list')
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[2][1], TS), 'url NOT in ts list')

    def test_04(self):
        """ Which list < 300 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[3][1], self.urlIds_urls[3][0]))
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[3][1], XL), 'url NOT in xl list')
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[3][1], TS), 'url NOT in ts list')

    def test_05(self):
        """ Which list = 300 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[4][1], self.urlIds_urls[4][0]))
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[4][1], XL), 'url NOT in xl list')
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[4][1], TS), 'url NOT in ts list')

    def test_06(self):
        """ Which list > 300 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[5][1], self.urlIds_urls[5][0]))
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[5][1], XL), 'url NOT in xl list')
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[5][1], TS), 'url NOT in ts list')

    def test_07(self):
        """ Which list < 312 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[6][1], self.urlIds_urls[6][0]))
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[6][1], XL), 'url NOT in xl list')
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[6][1], TS), 'url NOT in ts list')

    def test_08(self):
        """ Which list = 312 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[7][1], self.urlIds_urls[7][0]))
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[7][1], XL), 'url NOT in xl list')
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[7][1], TS), 'url NOT in ts list')

    def test_09(self):
        """ Which list > 312 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[8][1], self.urlIds_urls[8][0]))
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[8][1], XL), 'url present in xl list')
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[8][1], TS), 'url NOT in ts list')

    def test_10(self):
        """ Which list < 400 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[9][1], self.urlIds_urls[9][0]))
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[9][1], XL), 'url present in xl list')
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[9][1], TS), 'url NOT in ts list')

    def test_11(self):
        """ Which list = 400 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[10][1], self.urlIds_urls[10][0]))
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[10][1], XL), 'url present in xl list')
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[10][1], TS), 'url NOT in ts list')

    def test_12(self):
        """ Which list > 400 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[11][1], self.urlIds_urls[11][0]))
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[11][1], XL), 'url present in xl list')
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[11][1], TS), 'url NOT in ts list')

    def test_13(self):
        """ Which list < 412 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[12][1], self.urlIds_urls[12][0]))
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[12][1], XL), 'url present in xl list')
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[12][1], TS), 'url NOT in ts list')

    def test_14(self):
        """ Which list = 412 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[13][1], self.urlIds_urls[13][0]))
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[13][1], XL), 'url present in xl list')
        self.assertTrue(self.build.check_url_in_database(self.urlIds_urls[13][1], TS), 'url NOT in ts list')

    def test_15(self):
        """ Which list > 412 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[14][1], self.urlIds_urls[14][0]))
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[14][1], XL), 'url present in xl list')
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[14][1], TS), 'url present in ts list')

    def test_16(self):
        """ Which list < 500 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[15][1], self.urlIds_urls[15][0]))
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[15][1], XL), 'url present in xl list')
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[15][1], TS), 'url present in ts list')

    def test_17(self):
        """ Which list = 500 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[16][1], self.urlIds_urls[16][0]))
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[16][1], XL), 'url present in xl list')
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[16][1], TS), 'url present in ts list')

    def test_18(self):
        """ Which list > 500 """
        logging.info('URL = %s ID = %s' % (self.urlIds_urls[17][1], self.urlIds_urls[17][0]))
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[17][1], XL), 'url present in xl list')
        self.assertFalse(self.build.check_url_in_database(self.urlIds_urls[17][1], TS), 'url present in ts list')


class BuildPublishingBits(SandboxedTest):
    """ Test url publication based on publishing bits values in D2.prevalence table """

    @classmethod
    def setUpClass(self):
        """ Create environment for prevalence publishing bits test cases """

        # 1. get 30 url cl_hash from prevalence table
        # 2. For first 5 set 100<which_list<312 in D2.build table : Both xl/ts
        #     set xl/ts test cases
        # 3. next 5 : Only TS  312<which_list<412
        #     set xl/ts test cases
        # 4. next 5 : None in ts/xl  100<which_list<412
        #     set xl/ts test cases
        # 5. Run build_script
        # 6. Test in publishing databases
        #     First preference is for prevalence table if publishing bits are not found then which_list values

        # 17 hashed -- Must be present in prevalence table
        cl_hashes = """(
            0x00A872ABC467AD7526EC343F,
            0x01D8CFB3CE162906479AB54B,
            0x01ED13583C0C94422F73CE19,
            0x0346D7F28668C95DB888AA13,
            0x081C5AE70506BE9A182735CA,
            0x09AEECE59A01E3986CC835DB,
            0x0BCE0B40B2128F5211920EF9,
            0xFDF248AC9928D98D5BD781C6,
            0xFE9983CEDCB7AB24EC91223F,
            0x8E5E196ED0D0427C6C97E142,
            0x2F5E5BF07E160D5512FBF201,
            0x10535EBD21DB7E1229E40626,
            0x35B72F424557E33CB4E7B3E5,
            0x15CC967B7F1F7DE1636E7A55,
            0x161E8D2841844892D4749CF7,
            0x1627DFFC9CCAD1AE93605833,
            0x19837290DA9A5BE790A6438C
        ) """

        # Query
        # insert into D2.dbo.prevalence
        # (cl_hash, is_top_site, is_locked, is_sanity_url, prevalence, publish_xl, publish_ts, customer_ticket)
        # values (0x19837290DA9A5BE790A61111, 0,0,0,0,0,0,0)

        self.build = Build(build_host=BUILD_HOST)
        logger.info("Build object instantiated")
        self.d2_conn = TsMsSqlWrap('D2')
        logging.info("Connected to DB : %s" %
                     self.d2_conn.get_select_data("select SERVERPROPERTY ('ServerName' ) AS ServerName"))
        # sfimport_out = sfimport_insert_urls()
        # self.urlIds = re.findall("urlId\=(\d+)", sfimport_out)
        # self.urlIds_t = tuple(self.urlIds)
        # logging.info(self.urlIds_t)
        # logging.info(type(self.urlIds_t))
        # run_agents()

        # query = "select top 30 cl_hash, url from D2.dbo.build (nolock) where url_id in " + str(self.urlIds_t)

        # todo : Add cl-hashes in table dynamically
        # self.d2_conn.con.execute("insert into D2.dbo.prevalence\
        # (cl_hash, is_top_site, is_locked, is_sanity_url, prevalence, publish_xl, publish_ts, customer_ticket)\
        # values (0x19837290DA9A5BE790A61111, 0,0,0,0,0,0,0)")

        query = "select cl_hash from D2.dbo.prevalence (nolock) where cl_hash in " + cl_hashes
        logging.info("***************************************************")
        logging.info(query)
        self.cl_hash_bin = self.d2_conn.get_select_data(query)
        logging.info(self.cl_hash_bin)

        self.cl_hash_hex = []
        p = PrevalenceTable()
        for item in self.cl_hash_bin:
            cl_hex = p.d2_con.convert_cl_hash_bin_to_hex_string(item['cl_hash'])
            self.cl_hash_hex.append(cl_hex)
            item['cl_hash'] = cl_hex
            logging.info('binary cl_hash replaced with hex value %s' % cl_hex)
        logging.info('list of selected cl_hashes in hex format generated')
        logging.debug(self.cl_hash_bin)  # List of dictionaries #Binary cl_hash

        self.cl_hash_tuple = tuple(self.cl_hash_bin)
        logging.info(self.cl_hash_tuple)

        # Which_list TS=yes and Xl=Yes
        self.set_publishingbits_whichlist_build(self, 0, 3, 300)
        # Which_list TS=yes and Xl=No
        self.set_publishingbits_whichlist_build(self, 3, 6, 400)
        # Which_list TS=No and Xl=No
        self.set_publishingbits_whichlist_build(self, 6, 9, 500)

        # Run Agents and then build
        # run_agents()
        self.output = self.build.build_run('master', 'all')
        BuildSpecificChecks(self.build.get_build_values())

    def set_publishingbits_whichlist_build(self, start, end, which_list_val):
        for index in range(start, end):
            logging.info('----LOOPVALUES index=%s start=%s end=%s which_list=%s' % (index, start, end, which_list_val))
            self.update_build_whichlist(self, cl_hash=self.cl_hash_tuple[index]['cl_hash'], which_list=which_list_val)

            if index == start:
                logging.info('setting ts = 0 and xl = 0 index=%s' % index)
                self.update_pulishingbits(self, cl_hash=self.cl_hash_tuple[index]['cl_hash'], xl=0, ts=0)
            elif index == start+1:
                logging.info("setting ts = 1 and xl = 0 index=%s" % index)
                self.update_pulishingbits(self, cl_hash=self.cl_hash_tuple[index]['cl_hash'], xl=0, ts=1)
            elif index == start+2:
                logging.info("set ts = 1 and xl = 1 index=%s" % index)
                self.update_pulishingbits(self, cl_hash=self.cl_hash_tuple[index]['cl_hash'], xl=1, ts=1)
            else:
                logging.info('Publishing bits and which_list value set : Now exitting')
                # exit()

    def update_pulishingbits(self, cl_hash=None, xl=0, ts=0):
        """ updates publish_ts and publish_xl bits in prevalence table """
        query = "update D2.dbo.prevalence set publish_xl=%s, publish_ts=%s where cl_hash=%s" % (xl, ts, cl_hash)
        logging.info('Executing : %s' % query)
        self.d2_conn.execute_sql_commit(query)
        # Verify
        self.get_prevalence_values(self, cl_hash)

    def update_build_whichlist(self, cl_hash=None, which_list=101):
        """ updates which_list value in build table """
        query = "update D2.dbo.build set which_list=%s where cl_hash=%s" % (which_list, cl_hash)
        logging.info('Executing : %s' % query)
        self.d2_conn.execute_sql_commit(query)
        # Verify
        self.get_build_values(self, cl_hash)

    def get_prevalence_values(self, cl_hash):
        """ Logs required values for cl_hash from prevalence table """
        query = "Select cl_hash, publish_xl, publish_ts from D2.dbo.prevalence (nolock) where cl_hash=%s" % cl_hash
        logging.info('Executing : %s' % query)
        logging.info("D2.PREVALENCE : %s" % self.d2_conn.get_select_data(query))
        return self.d2_conn.get_select_data(query)

    def get_build_values(self, cl_hash):
        """ Logs required values for cl_hash from build table """
        query = "Select cl_hash, url, which_list from D2.dbo.build (nolock) where cl_hash=%s" % cl_hash
        logging.info('Executing : %s' % query)
        logging.info("D2.BUILD : %s" % self.d2_conn.get_select_data(query))
        return self.d2_conn.get_select_data(query)

    @classmethod
    def tearDownClass(self):
        """ 1. Resent which_list values in build table
        2. Reset publishing bits values to default for selected cl_hashes
        removes added urls from build table """

        # sfimport_delete_urls()
        # run_agents()
        # logging.info("Removed urls from build table")

        # self.reset_db(self)
        # logging.info(self.cl_hash_bin)
        # logging.info(self.d2_conn)

    def reset_db(self):
        for item in self.cl_hash_bin:
            cl_hash = item['cl_hash']
            self.update_build_whichlist(cl_hash)
            self.update_pulishingbits(cl_hash)
        logging.info("D2.Prevalence and D2.build table resett]ed !!!")

    def test_01(self):
        """ Which_list  : 300        Publishing bits : ts=0 xl=0  """
        record = self.cl_hash_tuple[0]
        cl_hash = record['cl_hash']
        logging.info('Testing for : %s' % record)
        q = self.get_build_values(cl_hash)
        url = q[0]['url']
        self.get_prevalence_values(cl_hash)
        self.assertFalse(self.build.check_url_in_database(url, XL), 'url present in xl list')
        self.assertFalse(self.build.check_url_in_database(url, TS), 'url present in ts list')

    def test_02(self):
        """ Which_list  : 300        Publishing bits : ts=1 xl=0  """
        record = self.cl_hash_tuple[1]
        cl_hash = record['cl_hash']
        logging.info('Testing for : %s' % record)
        q = self.get_build_values(cl_hash)
        url = q[0]['url']
        self.get_prevalence_values(cl_hash)
        self.assertFalse(self.build.check_url_in_database(url, XL), 'url present in xl list')
        self.assertTrue(self.build.check_url_in_database(url, TS), 'url NOT in ts list')

    def test_03(self):
        """ Which_list  : 300        Publishing bits : ts=1 xl=1  """
        record = self.cl_hash_tuple[2]
        cl_hash = record['cl_hash']
        logging.info('Testing for : %s' % record)
        q = self.get_build_values(cl_hash)
        url = q[0]['url']
        self.get_prevalence_values(cl_hash)
        self.assertTrue(self.build.check_url_in_database(url, XL), 'url NOT in xl list')
        self.assertTrue(self.build.check_url_in_database(url, TS), 'url NOT in ts list')

    def test_04(self):
        """ Which_list  : 400        Publishing bits : ts=0 xl=0  """
        record = self.cl_hash_tuple[3]
        cl_hash = record['cl_hash']
        logging.info('Testing for : %s' % record)
        q = self.get_build_values(cl_hash)
        url = q[0]['url']
        self.get_prevalence_values(cl_hash)
        self.assertFalse(self.build.check_url_in_database(url, XL), 'url present in xl list')
        self.assertFalse(self.build.check_url_in_database(url, TS), 'url present in ts list')

    def test_05(self):
        """ Which_list  : 400        Publishing bits : ts=1 xl=0  """
        record = self.cl_hash_tuple[4]
        cl_hash = record['cl_hash']
        logging.info('Testing for : %s' % record)
        q = self.get_build_values(cl_hash)
        url = q[0]['url']
        self.get_prevalence_values(cl_hash)
        self.assertFalse(self.build.check_url_in_database(url, XL), 'url present in xl list')
        self.assertTrue(self.build.check_url_in_database(url, TS), 'url NOT in ts list')

    def test_06(self):
        """ Which_list  : 400        Publishing bits : ts=1 xl=1  """
        record = self.cl_hash_tuple[5]
        cl_hash = record['cl_hash']
        logging.info('Testing for : %s' % record)
        q = self.get_build_values(cl_hash)
        url = q[0]['url']
        self.get_prevalence_values(cl_hash)
        self.assertTrue(self.build.check_url_in_database(url, XL), 'url NOT in xl list')
        self.assertTrue(self.build.check_url_in_database(url, TS), 'url NOT in ts list')

    def test_07(self):
        """ Which_list  : 500        Publishing bits : ts=0 xl=0  """
        record = self.cl_hash_tuple[6]
        cl_hash = record['cl_hash']
        logging.info('Testing for : %s' % record)
        q = self.get_build_values(cl_hash)
        url = q[0]['url']
        self.get_prevalence_values(cl_hash)
        self.assertFalse(self.build.check_url_in_database(url, XL), 'url present in xl list')
        self.assertFalse(self.build.check_url_in_database(url, TS), 'url present in ts list')

    def test_08(self):
        """ Which_list  : 500        Publishing bits : ts=1 xl=0  """
        record = self.cl_hash_tuple[7]
        cl_hash = record['cl_hash']
        logging.info('Testing for : %s' % record)
        q = self.get_build_values(cl_hash)
        url = q[0]['url']
        self.get_prevalence_values(cl_hash)
        self.assertFalse(self.build.check_url_in_database(url, XL), 'url present in xl list')
        self.assertTrue(self.build.check_url_in_database(url, TS), 'url NOT in ts list')

    def test_09(self):
        """ Which_list  : 500        Publishing bits : ts=1 xl=1  """
        record = self.cl_hash_tuple[8]
        cl_hash = record['cl_hash']
        logging.info('Testing for : %s' % record)
        q = self.get_build_values(cl_hash)
        # logging.info(q)
        # logging.info(q[0])
        # logging.info(q[0]['url'])
        url = q[0]['url']
        self.get_prevalence_values(cl_hash)
        self.assertTrue(self.build.check_url_in_database(url, XL), 'url NOT in xl list')
        self.assertTrue(self.build.check_url_in_database(url, TS), 'url NOT in ts list')


class BuildResumeMode(SandboxedTest):
    """ Tests for build Resume mode Functionality
    1. Remove ts_sanity / xl_sanity
    2. Run and Error
    3. Revert
    4. Run Resume
    """

    def setUp(self):
        SandboxedTest.setUp(self)
        self.build = Build(build_host=BUILD_HOST)
        self.ts_sanity = runtime.LIST.ts_sanity
        self.xl_sanity = runtime.LIST.xl_sanity
        cmd1 = "rm " + self.ts_sanity
        cmd2 = "rm " + self.xl_sanity
        self.build.run_build_cmd(cmd1)
        self.build.run_build_cmd(cmd2)

    def test_resume_ts(self):
        """ Test migt ts resume mode """
        self.build.build_run('migt', 'ts')
        self.tearDown()
        self.build.build_run('resume', 'ts')
        BuildSpecificChecks(self.build.get_build_values())

    def test_resume_xl(self):
        """ Test migt xl resume mode """
        self.build.build_run('migt', 'xl')
        self.tearDown()
        self.build.build_run('resume', 'xl')
        BuildSpecificChecks(self.build.get_build_values())

    def test_resume_master(self):
        """ Test master build resume mode """
        self.build.build_run('master', 'all')
        self.tearDown()
        self.build.build_run('resume', 'master')
        BuildSpecificChecks(self.build.get_build_values())

    def tearDown(self):
        """ Reverts the changes """
        cmd1 = "touch " + self.ts_sanity
        cmd2 = "touch " + self.xl_sanity
        self.build.run_build_cmd(cmd1)
        self.build.run_build_cmd(cmd2)


class BuildResetMode(SandboxedTest):
    """ Tests build reset mode feature """

    def test_reset(self):
        build = Build(build_host=BUILD_HOST)
        build.reset_build()
        BuildSpecificChecks(build.get_build_values())
        # pprint.pprint(build.get_build_values())


class BuildSanityFile(SandboxedTest):
    """ Sanity Files Check and Categorization Error """

    def setUp(self):
        SandboxedTest.setUp(self)
        self.build = Build(build_host=BUILD_HOST)
        self.build.truncate_sanity_file()
        # self.build.reset_build()

    def tearDown(self):
        self.build.truncate_sanity_file()
        # print(self.build.run_build_cmd("find %s -maxdepth 1 -type f -name '[.]*' -print -delete" % build_script_path))
        # self.build.reset_build()

    def test_xl_sanity_valid(self):
        sanity_file = 'xl'
        self.build.write_into_sanity_file(sanity_file, sanity_contents_valid)
        self.build.build_run('migt', 'xl')
        error = self.build.get_fatal_error()
        BuildSpecificChecks(self.build.get_build_values())
        assert error is False

    def test_xl_sanity_invalid(self):
        sanity_file = 'xl'
        self.build.write_into_sanity_file(sanity_file, sanity_contents_invalid)
        self.build.build_run('migt', 'xl')
        error = self.build.get_fatal_error()
        print(error)
        assert error == 'CATEGORIZATION ERROR'
        # Revert Changes and re-run build resume mode
        self.build.write_into_sanity_file(sanity_file, sanity_contents_valid)
        self.build.build_run('resume', 'xl')
        BuildSpecificChecks(self.build.get_build_values())

    def test_xl_sanity_skipped(self):
        """        """
        sanity_file = 'xl'
        self.build.write_into_sanity_file(sanity_file, sanity_contents_skipped)
        self.build.build_run('migt', 'xl')
        BuildSpecificChecks(self.build.get_build_values())

    def test_ts_sanity_skipped(self):
        """        """
        sanity_file = 'ts'
        self.build.write_into_sanity_file(sanity_file, sanity_contents_skipped)
        self.build.build_run('migt', 'ts')
        BuildSpecificChecks(self.build.get_build_values())

    def test_ts_sanity_valid(self):
        sanity_file = 'ts'
        self.build.write_into_sanity_file(sanity_file, sanity_contents_valid)
        self.build.build_run('migt', 'ts')
        error = self.build.get_fatal_error()
        BuildSpecificChecks(self.build.get_build_values())
        assert error is False

    def test_ts_sanity_invalid(self):
        sanity_file = 'ts'
        self.build.write_into_sanity_file(sanity_file, sanity_contents_invalid)
        self.build.build_run('migt', 'ts')
        error = self.build.get_fatal_error()
        print(error)
        assert error == 'CATEGORIZATION ERROR'
        # Revert Changes and re-run build resume mode
        self.build.write_into_sanity_file(sanity_file, sanity_contents_valid)
        self.build.build_run('resume', 'ts')
        BuildSpecificChecks(self.build.get_build_values())



# class TestClass(SandboxedTest):
#
#     def test_01(self):
#         self.build = Build(build_host=BUILD_HOST)
#         BuildSpecificChecks(self.build.get_build_values())
#         pprint.pprint(self.build.get_build_values())