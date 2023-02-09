"""
=================================
Harvester Utility Functions
=================================
"""
import os
import re
import copy
import pprint
import logging
import datetime
import fileinput
import tempfile

from path import Path

import runtime
from harvesters.harvester_config import HarvesterConfig
import lib.utils.servers
import lib.utils.serverstatus
import libx.filex
from libx.process import OSProcessHandler





#import logging

from framework.test import SandboxedTest
from libx.utils import DictDiffer
from libx.process import ShellExecutor
from lib.exceptions import FileNotFoundError, ValidationError, ProcessingError
from lib.db.mssql import TsMsSqlWrap


class NoURLsModified(AssertionError):
    """ Exception when no urls are modified at end of harvester run"""
    pass


class SandboxedHarvesterTest(SandboxedTest):
    """
    Class for dealing specific harvester releated cleanup actions
    including copying harvester.log, processed_files(if possible) etc
    to sandbox directory
    """

    @classmethod
    def setUpClass(cls):
        #### Is app server up?
        if lib.utils.serverstatus.is_app_server_up(runtime.AppServer.host) is False:
            raise Exception('App Server is Down')

        #### Is Guvnor up?
        if lib.utils.servers.is_guvnor_server_up() != 1:
            raise Exception('Guvnor Server is Down')

    def setUp(self):
        """Cleans working directory"""
        SandboxedTest.setUp(self)
        if not hasattr(self, 'default_har_config'):
            logging.warning('default_har_config was not set')
            raise Exception('Harvester Configuration is not set')
        _work_dir = self.default_har_config.working_dir
        _base_dir = self.default_har_config.base_working
        if not _work_dir.startswith(_base_dir):
            raise Exception('Cleanup: %s must start with base: %s' % (
                            _work_dir, _base_dir))
        logging.info('Cleanup: working dir: %s' , _work_dir)
        if _work_dir == _base_dir:
            raise Exception('Working DIR is not specified in harvesterConfig for ' + self.default_har_config.harvester_name)
        else:
            Harvester.clean_any_dir(_work_dir)
        _src_dir = self.default_har_config.src_dir
        _base_dir = self.default_har_config.base_src
        if not _src_dir.startswith(_base_dir):
            raise Exception('Cleanup: %s must start with base: %s' % (
                            _src_dir, _base_dir))
        logging.info('Cleanup: source dir: %s' , _work_dir)
        if _src_dir == _base_dir:
            logging.warning('Source DIR is not specified in harvesterConfig for ' + self.default_har_config.harvester_name)
        else:
            Harvester.clean_any_dir(_src_dir)
        #kill harvester process
        _process_name = '/opt/sftools/bin/start_harvester.sh %s' % self.default_har_config.properties_file
        _pobj = OSProcessHandler(_process_name, full_format=True, exclude_grep=True)
        _pobj.kill_processes()


    def tearDown(self):
        '''Copies required files back to sandbox'''
        if not hasattr(self, 'default_har_config'):
            __err_msg = 'default_har_config was not set'
            logging.warning('default_har_config was not set')
            raise Exception(__err_msg)
        #### copy harvester log file
        _file = self.default_har_config.log_file_name
        if os.path.isfile(_file):
            Path.copy(_file, '.')
            logging.debug('Sandbox: Harvester log file copied from %s', _file)
        else:
            logging.warning('Sandbox: Harvester log not found: %s', _file)

        #### copy sfimport temp files
        #todo: import latest sfimport

        for tmp, dirs, files in os.walk('/tmp'):
            for basename in files:
                _file = os.path.join(tmp, basename)
                _tstamp = datetime.datetime.fromtimestamp(os.path.getmtime(_file))

                stat = os.stat(_file)
                if (_tstamp > self.sandbox.time_start):
                    print('gr: %s' % _file)
                    try:
                        Path.copy(_file, '.')
                        logging.debug('Sandbox: copy modified file: %s', _file)
                    except:
                        logging.warning('Sandbox: copy failed for file: %s', _file)
        #todo: copy working dir or file listin it
        #copy processed files
        #todo: copy files inside specific folders/all folders
                if (str(_file).startswith('sfimport') and
                        _tstamp > self.sandbox.time_start):
                    print(('sfi', _file))
                    Path.copy(Path(_file), '.')
                    logging.debug('Sandbox: sfimport log copied from %s', _file)
        SandboxedTest.tearDown(self)


class HarvesterExecutor(ShellExecutor):
    """
    Class to run harvester.
        It can run the harvester based on set of input parameters.
        The process exit code can be checked for any non consistent values
        Can validate the stdout and stderr streams for certain terms
        Retains the process object so that further processing can be done

    .. code-block:: python

        fn16 = HarvesterExecutor('/opt/sftools/conf/cleanmxportal.properties')
        log = logging.getLogger()
        result = fn16.run_and_validate(['Exception'],
                              [False],
                              ['ERROR', 'Generating', 'Processing' ],
                              [False, True, True]
    """
    def __init__(self,
                 properties_file,
                 binfile='/opt/sftools/bin/start_harvester.sh ',
                 ):
        """init"""
        ShellExecutor.__init__(self)
        self.cmd = []

        self.cmd_builder(properties_file, binfile)


    def cmd_builder(self, properties_file, binfile):
        """Build the execution command

        :param properties_file: properties file location for harvester
        :param bin_file: start_harvester.sh with path

        """
        self.cmd.append (binfile)
        self.cmd.append (properties_file)


class Harvester:
    """Harvester related functions

    :param harvester_config: HarvesterConfig object
    :param source_data_file: Path to source data file
    """
    def __init__(self, harvester_config, match_type='full'):#, source_data_file):
        """init"""
        #todo: get harvester config based on harvester name!
        #hard: set default to APWG

        #self.hconfig = harvester_config
        self.u2 = TsMsSqlWrap('U2')
        self.match_type=match_type
        if isinstance(harvester_config, HarvesterConfig):
            self.hconfig = harvester_config
        else:
            raise TypeError('harvester_config object should be an' \
                            + ' instance of HarvesterConfig')


    def clean_working_dir(self):
        """Clean the Files in the working directory
        If working directory is not found, it creates it

        :rtype: string  'pass' on success and 'fail' on failure
        """
        logging.info('Cleaning working directory')
        _dir = self.hconfig.working_dir
        _base = self.hconfig.base_working
        if _dir == _base:
            raise Exception('Working DIR is not specified in harvesterConfig for ' + self.default_har_config.harvester_name)

        if not _dir.startswith(_base):
            msg = 'working_dir: %s must start with base: %s' % (_dir, _base)
            raise Exception(msg)
        return Harvester.clean_any_dir(_dir)

    @staticmethod
    def clean_any_dir(_dir):
        """Cleans any directory, creates if dir doesnt exist"""
        if _dir.strip() == '/':
            raise Exception('target directory cant be root!')
        if not os.path.isdir(_dir):
            logging.info('%s doesnt exist/not directory. Trying to create',
                         _dir)
            os.makedirs(_dir)
        fileList = os.listdir(_dir)
        for fileName in fileList:
            item = os.path.join(_dir, fileName)
            if os.path.isfile(item):
                os.remove(item)
        logging.info("Clean dir: %s - ok", _dir)
        return True

    def create_temp_file(self, source_data, prefix='tmp_', suffix=''):
        """Places source_data in the current directory
        :source_data: data for the
        :rtype: filename as string
        """
        #:todo: should i include more ?
        _fd, _file = tempfile.mkstemp(prefix='tmp_', dir='.', text=True)
        with os.fdopen(_fd, 'w+') as fpw:
            fpw.write(source_data)
        return _file

    def put_file_in_working(self, source_file, use_base_source=True):
        """Places source_file Files in the working directory of harvster
        :source_file: the given files will be put in working directory
        :type: string or list of strings
        Raises:
            EnvironmentError when unable to copy file
        """
        _target_dir = self.hconfig.working_dir
#        self.put_files_in_target(source_file, _target_dir)
        if not use_base_source:
            libx.filex.put_files_in_target(source_file, _target_dir,source_base='/', create_target_path = True)
        else:
            libx.filex.put_files_in_target(source_file, _target_dir,
                                    source_base = self.hconfig.base_source,
                                    create_target_path = True)

    def put_file_in_source(self, source_file):
        """Places source_file in source folder of harvester"""
        _target_dir = self.hconfig.src_dir
        logging.info('Putting ' + source_file + ' in ' + _target_dir)
        libx.filex.put_files_in_target(source_file, _target_dir,
                                    source_base = self.hconfig.base_source,
                                    create_target_path = True)



    def check_open_session(self):
        """
        This function will return the status of Open Sessions exist
        for a harvester

        :rtype bool: Open session exist for the harvester
        Raises:
            :Exception: If unable to perform as expected
        """
        try:
            _sql = "select count(*) as 'Total' from U2.dbo.Session where " \
                 + "closedOn IS NULL AND sessionOwner='%(sessionOwner)s'; " % (
                    {'sessionOwner':self.hconfig.session_owner})
            logging.debug("Executing Query : %s", (_sql))
            u2_cur = self.u2.get_select_cursor(_sql)
            for row in u2_cur:
                if row['Total'] == 0:
                    logging.info("Session: None open for %s",
                                    (self.hconfig.harvester_name))
                    return False
                else:
                    logging.info('Session: Open session exists for: %s',
                                            self.hconfig.harvester_name)
                    return True
        except Exception as err:
            logging.error('Cannot process open session info %s', err.args[0])
            raise

    def remove_open_session(self):#md:
        """This function will remove all the open sessions created for a harvester

        Returns:
            :rtype bool: Removed all open sessions properly of the harvester - Success
            :'fail': Not able to remove all open session of the harvester - Failure
        """
        if not self.check_open_session():
            return True
        try:
            _sql = "delete from U2.dbo.session where " \
                   + "closedOn is NULL AND " \
                   + "sessionOwner = '%(sessionOwner)s'; " % (
                        {'sessionOwner':self.hconfig.session_owner})
            logging.debug("Running Query : %s", _sql)
            self.u2.execute_sql_commit(_sql)
            if not self.check_open_session():
                logging.info('Session: removed for: %s',
                                    self.hconfig.harvester_name)
                return True
            else:
                raise Exception('Session: remove open session failed!')
        except Exception as err:
            logging.error('Cannot remove open session: %s', err.args[0])
            raise

    def create_open_session(self):
        """This function will create an open session for the harvester

        Returns:
            :'pass': Open session is created successfully.
            :'fail': Open session is not created by the agent.
        Raises:
            :Exception: If problem in executing this function.
        """
        if self.remove_open_session():
            logging.debug("Reset of Open session of %s harvester is " \
                    + "successfull", (self.hconfig.harvester_name))
        else:
            logging.error("Unable to reset open session of %s harvester",
                            self.hconfig.harvester_name)
            return False

        logging.info("creating new open session for %s harvester ",
                            self.hconfig.harvester_name)
        try:
            logging.debug (" Creating an open Session for %s Harvester ",
                            self.hconfig.harvester_name)
            _sql_u = "delete from U2.dbo.Session where sessionid = '12345678-1234-1234-1234-123456789abc'"
            logging.debug("Running Query : %s", _sql_u)
            self.u2.execute_sql_commit(_sql_u)
            _sql = " INSERT INTO Session ([sessionId],[lastRecordNumber],[openedOn],[closedOn] ,[filePath], [throughput]," + \
                   "[sessionOwner]) VALUES ('12345678-1234-1234-1234-123456789abc',0,SYSDATETIME(),NULL,NULL, 0, " + \
                   "'%(sessionOwner)s' ); " % ({'sessionOwner': self.hconfig.session_owner})
            print(_sql)
            logging.debug("Running Query : %s", _sql)
            u2_cur = self.u2.execute_sql_commit(_sql)
        except Exception as err:
            logging.error('Cannot create session info %s', err.args[0])
            raise

        if self.check_open_session():
            logging.info('createOpenSession has created an open session for ' \
                        + '%s Harvester ', self.hconfig.harvester_name)
            return True
        logging.error ("createOpenSession is not able to create an open " \
                  + "sesion for %s Harvester ", self.hconfig.harvester_name)
        return False

    def check_properties_file(self):  #Need to review this function
        """Function to verify the harvester Property File existance
        Raises:
            FileNotFoundError
        """
        _har_name = self.hconfig.harvester_name
        _prop_file = self.hconfig.properties_file
        _har_prop_file = self.hconfig.base_conf+ 'harvester.properties'
        if not os.path.exists(_prop_file):
            msg = "Property file: %s not found for:%s"% \
                            (_prop_file, _har_name)
            raise FileNotFoundError(msg)
        if not os.path.exists(_har_prop_file):
            msg = "Property file: %s not found "% \
                            (_har_prop_file)
            raise FileNotFoundError(msg)
        logging.debug("Property file: %s found for %s"%(_prop_file, _har_name))

    def reset_processed_files (self):
        """
        Resets the processedfile.txt file with an empty file.

        Raises:
            :EnvironmentError: if file cannot be reset/deleted
        """
        _pfile = self.hconfig.processed_files
        logging.info('Resetting processed file: %s' % _pfile)
        _pdir, _psep, _rel_file = _pfile.rpartition('/')
        try:
            if not os.path.isdir(_pdir):
                logging.error('%s directory doest exist. Creating...')
                os.makedirs(_pdir)

            if os.path.isfile(_pfile):
                os.remove(_pfile)
            if os.path.isfile(_pfile):
                raise EnvironmentError('Unable to delete Processed Files: %s' \
                                            %_pfile)
            with open(_pfile, 'w+'):
                pass    #Creates empty file
        except:
            logging.error('Unable to reset Processed Files: %s'%_pfile)
            raise

    def find_in_processed_files (self, source_data):
        """
        Finds the given string in processedfile.txt. Returns True

        Raises:
            :EnvironmentError: if file not found!
        """
        if not type(source_data) in (list, str):
            raise TypeError('str_list must be a string or list of strings')
        if type(list) == str:
            source_data = (source_data)
        with open(self.hconfig.processed_files) as fp:
            pdata = ''.join(fp.readlines())
        msg = []
        for term in source_data:
            _term = str(term).strip().replace('.','\\.').rpartition('/')[2]
            if not re.search(_term, pdata):
                msg.append('Not found: %s'%term)
        if msg:
            raise ValidationError('\n'.join(msg))
        logging.info('Check: Processed file has all input files')#todo: change message
        return True

    def run_preprocessor(self, pre_path):
        """Runs preprocessor for harvfester specified"""
        cmd = 'sh ' + pre_path
        stdout,stderr = ShellExecutor.run_wait_standalone(cmd, create_log_file=False)
        if stderr != '':
            logging.error('Preprocessor Error : ' + stderr)
        logging.info('Preprocessor Stdout : ' + stdout)
        return stdout

    def process_log (self):
        """process_log is used to process harvester.logging.

        It extracts all possible rules matched/action taken pairs and returns
        a list of values in the order encountered.

        Raises:
            NoURLsModified
        """

        _hlog = self.hconfig.log_file_name
        if not os.path.isfile(_hlog):
            raise  ProcessingError('File Not Found: %s'%_hlog)
        pl_results = []
        #todo: check for statistics match in log,
            #before Actions Taken
            #based on harvester name
        #todo: return exception when no URL Modified/Processed
        result = DataHolder()
        result.action_taken = {}
        result.rules_matched = {}
        action_taken = False    # state variable to extract text
        rules_matched = False
        err_list = []
        no_urls_modified = False
        for line in fileinput.input(_hlog):
            if 'ERROR' in line.strip() :
                err_list.append(line.strip())
            if line.strip() == "No urls modified.":
                no_urls_modified = True
            if line.strip() == "Actions taken:":
                action_taken = True
            elif line.strip() == "Rules matched:":
                rules_matched = True
            elif line.strip() == "" or line.strip().startswith('Timing'):  # reset state vars
                if action_taken:
                    action_taken = False
                if rules_matched:
                    rules_matched = False
                    pl_results.append(copy.deepcopy(result))
                    logging.debug('rules extracted:%s', result.rules_matched)
                    logging.debug('actions taken:%s', result.action_taken)
                    result.action_taken = {}    #reset for next iteration
                    result.rules_matched = {}   #end of iteration
            else:
                if action_taken:
                    value, sep, key = str(line).strip().partition(':')
                    if key.strip() not in result.action_taken:
                        result.action_taken[key.strip()] = value.strip()
                    else:
                        raise KeyError('key already found!! %s'%key)
                elif rules_matched:
                    value, sep, key = str(line).strip().partition('(')
                    if key.strip() not in result.rules_matched:
                        result.rules_matched['(' + key.strip()] = value.strip()
                    else:
                        raise KeyError('key already found!! %s'%key)
        if no_urls_modified:
            raise NoURLsModified('\n'.join(err_list))
        if pl_results:
            return pl_results
        logging.error(dir(pl_results))
        raise Exception('Errors/Exceptions in harvester log')

    def check_harvester_result(self): #Need to review this function
        """
        Function for chekcing harvester.log for errors.

        Returns:
            :1: on success (no errors in log)
            :0: on failure (in case of errors)
        """

    #    fp = open(self.hconfig.log_file_name, 'r')
    #    hlog_data = fp.read()
    #    fp.close()
    #    error_exists = re.search( r'(.*) Error(\.*)', hlog_data, re.M|re.I)
    #    critical_error_exists = re.search( r'(.*) Critical Error(\.*)', hlog_data, re.M|re.I)

    #    #if (hlog_data.__contains__('ERROR') or hlog_data.__contains__('CRITICAL ERROR')):
    #    if ((error_exists != None) or (critical_error_exists != None)):
    #        return 0
        return 1

    def remove_harvester_log(self):
        """
        Deletes harvester log file in the system, and creates an empty one

        Raises:
            EnvironmentalError if unable to delete the file.
        """
        #Archive or back up harvester.log
        #ret=subprocess.call('cat '+hlog+' >> '+hlog+'.bak',shell=True)
        #Empty harvester.log
        pfile = self.hconfig.log_file_name
        if os.path.isfile(pfile):
            os.remove(pfile)
        if os.path.isfile(pfile):
            raise EnvironmentError('Unable to delete Harvester log: %s'%pfile)
        with open(pfile, 'w+'):
            pass

    def clean_mapr_dir(self):
        """Empties mapr directory contents for specific Harvester"""
        _dir = self.hconfig.mapr_dir
        _base = self.hconfig.base_mapr
        if _dir == _base:
            raise Exception('Working DIR is not specified in harvesterConfig for ' + self.default_har_config.harvester_name)
        if not _dir.startswith(_base):
            msg = 'mapr_dir: %s must start with base: %s' % (_dir, _base)
            raise Exception(msg)
        return Harvester.clean_any_dir(_dir)

    def clean_src_dir(self):
        """Empties Source dir for harvester"""
        _dir = self.hconfig.src_dir
        _base = self.hconfig.base_src
        if _dir == _base:
            raise Exception('Working DIR is not specified in harvesterConfig for ' + self.default_har_config.harvester_name)
        if not _dir.startswith(_base):
            msg = 'mapr_dir: %s must start with base: %s' % (_dir, _base)
            raise Exception(msg)
        return Harvester.clean_any_dir(_dir)

    def look_in_harvester_log(self, err_str):
        """Check for a string in harvester log"""

        if not os.path.isfile(self.hconfig.log_file_name):
            return False
        tokens = re.findall(err_str, open(self.hconfig.log_file_name).read())
        if tokens:
            logging.debug('Tokens found: %s', tokens)
            return True
        logging.debug('%s is not found in log', err_str)
        return False

    def run_harvester(self, source_file, resume_mode=True, copy_to_source=False, use_source_base=True):
        """
        mode  = True/False
        Function to run the harvester in normal mode (RESUME mode to added later as required).
        Prerequisite - there is no open session in U2.dbo.sessions table for the harvester.

        :source_file: the given files will be put in working directory
        :type: string or list of strings

        :rtype: string  'pass' on success and 'fail' on failure
        """
        #step: 1. Verify that gurvnor and applications servers are up and running
        self.check_properties_file()  #   Checking properties file of harvester Exist
        self.reset_processed_files()
        self.remove_harvester_log()

        if not source_file:
            if resume_mode:
                logging.info('source_file: None - No new files will be copied to working_dir')
            else:
                logging.info('source_file: None - No new files will be copied to src_dir')
        else:
            if resume_mode:
                self.clean_working_dir()
                self.put_file_in_working(source_file, use_source_base)
            else:
                if copy_to_source:
                    self.put_file_in_source(source_file)
        if resume_mode:
            if (not self.create_open_session()):  # Is a session open?
                raise Exception('No open session in DB')
        else:
            self.remove_open_session()
            self.clean_mapr_dir()
            self.clean_working_dir()


    #Run harvester
        hexe = HarvesterExecutor(self.hconfig.properties_file)
        #kill harvester process
        _process_name = '/opt/sftools/bin/start_harvester.sh %s' % self.hconfig.properties_file
        _pobj = OSProcessHandler(_process_name, full_format=True, exclude_grep=True)
        _pobj.kill_processes()
        hresult = hexe.run_and_validate([], [], [], []
                                #['Exception'], [False],
                                #['Exception'],[False],
                                ###['Error','ERROR', 'Exception'],
                                ###[False,False,False],
                                ###['Error','ERROR', 'Exception'],
                                ###[False,False,False],
                                )
        #todo: check for additional errors in log file
        if not hresult:
            raise AssertionError("Errors while running harvester. See log files for more information")
        return True

    def test_harvester_base(self,
                            source_file,
                            exp_action_taken=None,
                            exp_rules_matched=None,
                            resume_mode = True,
                            copy_to_source=False ):
        """
        Template for harvester test execution
        """
        if exp_action_taken is None:
            exp_action_taken = self.hconfig.action_taken
        if exp_rules_matched is None:
            exp_rules_matched = self.hconfig.rules_matched
        run_result = self.run_harvester(source_file, resume_mode=resume_mode, copy_to_source=copy_to_source)



        if source_file:
            logging.warning('Processed file check skipped!Enable it')
            #self.find_in_processed_files([source_file])
        else:
            logging.info('Check: Processed file check skipped. No source file specified')

        if source_file:
            pass
            #check for archive
        if source_file:
            pass
            #check .previous

        try:
            log_obj = self.process_log()
        except NoURLsModified:
            logging.error('No URL: Log file does not contain any URL processed statistics.')
            raise

        if not (isinstance(log_obj, list) and (len(log_obj) >= 1)):
            msg = 'Test Result: ERROR - Unknown Error in harvester_log_parser'
            raise Exception(msg)

        #Output verification
        if self.match_type=='full':
            action_obj = DictDiffer(log_obj[-1].action_taken, exp_action_taken)
            rules_obj = DictDiffer(log_obj[-1].rules_matched, exp_rules_matched)

            msg = ''
            if (action_obj.ismatch()):
                msg += 'Action Taken: Results match\nDict: %s'% \
                            pprint.pformat(exp_action_taken, width=4, indent=4)
            else:
                msg += '\nAction Taken: Results mismatch!\n%s'% str(action_obj)
            if (rules_obj.ismatch()):
                msg += '\nRules: Results match!\nDict: %s'% \
                            pprint.pformat(exp_rules_matched, width=4, indent=4)
            else:
                msg += '\nRules: Results mismatch!\n%s' % str(rules_obj)

            if not (rules_obj.ismatch() and action_obj.ismatch()):
                print(msg)
                logging.error(msg)
                logging.critical('Test result: FAIL')
                raise ValidationError('Output Verification Failed:\n%s'%msg)
            print(msg)
            logging.info(msg)
        else:
            action_obj = DictDiffer(exp_action_taken, log_obj[-1].action_taken)
            rules_obj = DictDiffer(exp_rules_matched, log_obj[-1].rules_matched)

            msg = ''
            if (action_obj.partial_match()):
                msg += 'Action Taken: Results match\nDict: %s'% \
                            pprint.pformat(exp_action_taken, width=4, indent=4)
            else:
                msg += '\nAction Taken: Results mismatch!\n%s'% str(action_obj)
            if (rules_obj.partial_match()):
                msg += '\nRules: Results match!\nDict: %s'% \
                            pprint.pformat(exp_rules_matched, width=4, indent=4)
            else:
                msg += '\nRules: Results mismatch!\n%s' % str(rules_obj)

            if not (rules_obj.partial_match() and action_obj.partial_match()):
                raise ValidationError('Output Verification Failed:\n%s'%msg)
            logging.info(msg)


if __name__ == "__main__":
    raise NotImplementedError('This module must be imported!')
