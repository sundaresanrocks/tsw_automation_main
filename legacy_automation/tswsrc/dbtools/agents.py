import datetime
import time
import os

import logging
from lib.exceptions import ProcessingError, ValidationError, TestFailure
from lib.db.mssql import TsMsSqlWrap
from libx.process import ShellExecutor, OSProcessHandler
import libx.filex


AGENT_TIMEOUT = 10
AGENT_CHECK_INTERVAL = 0.5


class Agents():
    """

    """

    def __init__(self, agent_name):
        self.d2db = TsMsSqlWrap('D2')
        self.agent_name = agent_name.lower()
        sql = "select * from active_agents with (nolock) where agent_name = '%s'" % self.agent_name.upper()
        if self.d2db.get_row_count(sql) != 1:
            raise ValueError('Agent: %s is not a valid agent name!')

        self.agent_dict = {
            'tman': {
                'bin': '/usr2/smartfilter/dbtools/tman',
                'args': '-d -i -s -n 5 -x 500 -y 500 -z 500 -D',
            },
            'wrman': {
                'bin': '/usr2/smartfilter/dbtools/wrman',
                'args': '-t 5 -n 10 -D',
            },
            'crua': {
                'bin': '/usr2/smartfilter/dbtools/crua',
                'args': '-t 5  -D',
            },
            'cbman': {
                'bin': '/usr2/smartfilter/dbtools/cbman',
                'args': '-t 5  -D',
            },
            'wrua': {
                'bin': '/usr2/smartfilter/dbtools/wrua',
                'args': '-t 5 -n 10 -D',
            },
            'dman': {
                'bin': '/usr2/smartfilter/dbtools/dman',
                'args': '-t 5 -N 10 -W 10 -i -s -D',
            },
            'nrua': {
                'bin': '/usr2/smartfilter/dbtools/nrua',
                # 'args':'',
            }
        }

        if agent_name.lower() not in list(self.agent_dict.keys()):
            raise TypeError('Agent name not supported')
            # todo: check if agent exists in agents table

    def get_status(self):
        """
        This Function is to Check whether the agent is running according to D2.dbo.active_agents table
        returns:
            status of is_running and shutdown_now of Requested Agent
        raises:
            exception if agent is not found in the DB
        """
        _sql = """ select agent_name, last_ran, is_running, shutdown_now from D2.dbo.active_agents (nolock) where agent_name = '%(self.agent_name)s'; """ % (
            {'self.agent_name': self.agent_name.upper()})
        for row in self.d2db.get_select_cursor(_sql):
            logging.info('Agent status: is_running:%s, shutdown_now:%s' % (
                row['is_running'], row['shutdown_now']))
            return row['is_running'], row['shutdown_now']
        raise Exception('Agents: %s not found in db' % self.agent_name)

    def set_status(self):
        """
        This Function sets the Agent to the is_running and shutdown_now to 0
        returns:
            True on Success
        raises:
            Exeception on Error
        """

        logging.info("Updating active_agents table for %s with is_running=0 & shutdown_now = 0 "% self.agent_name)

        _sql = """ update D2.dbo.active_agents set is_running = 0, shutdown_now = 0 where agent_name = '%(self.agent_name)s'; """ % (
            {'self.agent_name': self.agent_name.upper()})
        # Verify Active Agent
        is_running, shutdown_now = self.get_status()
        if not (is_running, shutdown_now) == (False, False):
            self.d2db.execute_sql_commit(_sql)

        # Rechecking the status of Agent
        is_running, shutdown_now = self.get_status()
        if not (is_running, shutdown_now) == (False, False):
            logging.error(
                " updateActiveAgent function is not able to set values of is_running = 0 & shutdown_now = 0 in active_agents table for %s" % (
                    self.agent_name.upper()))
            raise Exception('Error in Executing the query %s ' % _sql)
        return True

    def kill_agent(self):
        """
        This Function kills the Agent Process
        return - Nothing on Success
        raise Exception on Failure
        """
        reset = self.set_status()
        # Checking if process is already running
        agent_process = OSProcessHandler(self.agent_name)
        if not agent_process.is_running():
            return True
        ''' If agent is alredy running, then kill/ shutdown the agent   '''
        # kill Process
        logging.info('Killing agent processes')
        agent_process.kill_processes()
        if agent_process.is_running():
            raise ProcessingError('Unable to kill process for agent: %s' % self.agent_name)
        return True

    def __run_agent_internal(self, _cmd, get_deamon_process):
        """
        Runs The Agent is Verifies its output
        Returns:
            subprocess object if get_deamon_process = True
            True if get_daemon_process = False
        """
        # Kill the Agent if it is already Running before start the Execution of Agent
        self.kill_agent()
        logging.info(" %s Agent Options: %s" % (self.agent_name, _cmd))
        if get_deamon_process:
            return ShellExecutor.run_daemon_standalone(_cmd)
        self.stdout, self.stderr = ShellExecutor.run_wait_standalone(_cmd)
        if ('Invalid Usage' in self.stdout) or ('invalid option' in self.stdout):
            msg = "Not able to execute %s becasue of Invalid Usage OR invalid option " % (self.agent_name)
            logging.error(msg)
            raise Exception(msg)
        # if  FK_scorer_event_detail_event_id error occurs .remove line 143
        if ('ERROR'.lower() in self.stdout.lower() or len(self.stderr) != 0):
            if ('ds_facet_info' in self.stderr):
                logging.error('Inside _run_agent_internal : Error due to data not available in a table which is no more active, to be ignored ')
            elif 'FK_scorer_event_detail_event_id' in self.stdout.lower() or 'FK_scorer_event_detail_event_id' in self.stderr:
                logging.error("error in scorer event detail old")
                raise Exception("FK_scorer_event_detail_event_id error raised")
            else:
                msg = ("Got Error message while running %s " % (self.agent_name))
                logging.error(msg)
                raise Exception(msg)
        return True


    def run_agent(self, agent_args=None, output_file=None,
                  get_deamon_process=False):
        """
        This Method helps in Running any agent
        If we dont provide any arguements ,Default Arguments will be supplied to the Agent

        get_deamon_process: True will get live object without any checks,
                            Faile will wait till execution completes and checks are done

        Returns:
            <subprocess object>: if get_deamon_process = True
            True: if get_deamon_process = False and no errors
        raises:
            exception on Error/Fail

        """

        if agent_args is None:
            agent_args = self.agent_dict[self.agent_name.lower()]['args']
        self.output_file = self.__generate_op_file(output_file)

        return self.__run_agent_internal(
            self.agent_dict[self.agent_name.lower()]['bin'] + ' ' + \
            agent_args + ' -o ' + self.output_file,
            get_deamon_process)

    def __generate_op_file(self, output_file):
        """ generate output file name for the agent """
        if not output_file:
            time_now = datetime.datetime.now()
            sys_time_stamp = libx.filex.get_file_timestamp()

            output_file = self.agent_name + '_' + sys_time_stamp + '.log'
            logging.info("%s log: %s" % (self.agent_name, output_file))
        return output_file

    def tmpl_agent_log(self, agent_args, default_log=False, debug_log=False):
        """ Runs the agent with default log options and returns file name"""
        if default_log:
            start_time = datetime.datetime.now()
            time.sleep(1)  # sleep to avoid conflict with microseconds
            res = self.__run_agent_internal(
                self.agent_dict[self.agent_name.lower()]['bin'] + ' ' + \
                agent_args,
                get_deamon_process=False)
            res_files = libx.filex.get_files_in_dir('/tmp/',
                                                    modified_since=start_time,
                                                    wildcard=self.agent_name)
            logging.debug('Log files in /tmp/: %s' % res_files)
            if len(res_files) == 0:
                raise TestFailure('No default log file found at: %s' % '/tmp/')
            elif len(res_files) > 1:
                raise TestFailure('More than one log file found at: %s' % '/tmp/')
            file_name = res_files[0]
        else:
            self.run_agent(agent_args)
            file_name = os.path.abspath(self.output_file)
        logging.info('Agent log file: %s', file_name)
        with open(file_name , 'rb') as fpr:
            if debug_log:
                if 'DEBUG:'.lower() not in str(fpr.read().lower()):
                    raise ValidationError('DEBUG: not found in debug log life')
            else:
                if 'DEBUG:'.lower() in str(fpr.read().lower()):
                    raise ValidationError('DEBUG: found in plain log life')

    def tmpl_is_running(self, args):
        """Function to help tests that verify whether Agent is running or not"""
        agent_deamon = self.run_agent(agent_args=args,
                                      get_deamon_process=True)
        for x in range(int(AGENT_TIMEOUT / AGENT_CHECK_INTERVAL)):
            is_running, shutdown_now = self.get_status()
            if (False, False) == (is_running, shutdown_now):
                logging.debug('sleeping for %s s...' % AGENT_CHECK_INTERVAL)
                time.sleep(AGENT_CHECK_INTERVAL)
                continue
            if (True, False) == (is_running, shutdown_now):
                logging.info('Agent is running \t' + \
                             'Is running, Shutdown_now = (True,False)')
                break
            else:
                raise ProcessingError('Agent Check failed: Too quick or timeout: \n' + \
                                      '\tExpected: Is running, Shutdown_now = (True,False)' + \
                                      '\nFound\t:%s, %s' % (is_running, shutdown_now))
        # when agent is running
        logging.info('Waiting for agent to exit...')
        stdout, stderr = agent_deamon.communicate()  # waits till agent exits
        logging.error('Agent\'s return code: %s' % agent_deamon.returncode)
        if agent_deamon.returncode != 0:
            raise ProcessingError('Agent\'s return code is not 0')

        # after agent runs
        logging.info('checks after agent is shutdown')
        is_running, shutdown_now = self.get_status()
        if (False, False) != (is_running, shutdown_now):
            raise ProcessingError('Agent Check failed: Timeout: \n' + \
                                  '\tExpected: Is running, Shutdown_now = (True,False)' + \
                                  '\n\tFound:(%s,%s)' % (is_running, shutdown_now))

    def tmpl_agent_stdout_check(self, args, search_list):
        """Test base for help, version tests"""
        self.run_agent(args, get_deamon_process=False)
        missing_terms = []
        for item in search_list:
            if item not in self.stdout:
                missing_terms.append(item)
        if missing_terms:
            raise ValidationError('Version mismatch. Missing info:' +
                                  '\n\t'.join(missing_terms))


class AgentsUtils():
    """
    Has methods that can be used across agents

    """

    def __init__(self, url, url1="", agent_name="wrua"):

        # massage url.
        # Ex:- http://www.autotestwruatwo.com to *://autotestwruatwo.com
        # url = re.sub("http://www." ,"*://" ,url)
        # url = re.sub("https://www." ,"*://" ,url)



        if url.__contains__('[') and url.__contains__(']'):
            url = url.replace('[', '![')
            url = url.replace(']', '!]')

        if url1.__contains__('[') and url1.__contains__(']'):
            url1 = url1.replace('[', '![')
            url1 = url1.replace(']', '!]')

        self.url = url
        self.url1 = url1
        self.agent_name = agent_name


        #self.url2 = url2
        self.d2_obj = TsMsSqlWrap("D2")
        self.tman_obj = Agents("TMAN")
        self.wrua_obj = Agents("WRUA")
        self.webrep = 0
        self.webrep1 = 0
        self.webrep2 = 0


    def url_exists_in_db(self, table="build", db="D2"):

        """Checks the url is present the build or WebReputation tables.
           Can be used for querying other tables having url field
           Returns true if record exists
           false if record doesnot exist

           """
        recs = -1

        query = (
            "SELECT [url] FROM [%s].[dbo].[%s] (nolock) where [url] like \'%s\' escape \'!\' " % (db, table, self.url))

        logging.info("Executing query [%s]" % query)

        recs = self.d2_obj.get_row_count(query)
        if recs > 0:
            return True
        elif recs == 0:
            return False
        else:
            raise ProcessingError('Could not execute query [%s] !!' % query)

    def set_high_priority(self, url):
        """Sets 9999 priority for the url in WRQueue table"""

        # query = ("update [D2].[dbo].[WRQueue] set priority = 9999 where [url] like \'%s\'" % (url))
        query = ("update [D2].[dbo].[WRQueue] set priority = 9999 where [url] like \'%s\' escape \'!\' " % (url))
        self.d2_obj.execute_sql_commit(query)

    def fetch_webrep(self, url, fieldname="web_reputation"):
        """ Fetches web reputation of URL from WebReputation table """


        # webrep_query = ("select web_reputation from [D2].[dbo].[WebReputation] (nolock) where [url] like \'%s\' escape \'!\'"% (url))
        webrep_query = (
            "select %s from [D2].[dbo].[WebReputation] (nolock) where [url] like \'%s\' escape \'!\'" % (
                fieldname, url))
        wlist = self.d2_obj.get_select_data(webrep_query)
        # webrep = wlist[0]['web_reputation']
        fieldvalue = wlist[0][fieldname]
        # logging.info("web_reputation is %s" % (webrep,))
        logging.info("%s for url [%s] is %s" % (fieldname, url, fieldvalue,))

        return fieldvalue

    def execute_wrman(self, wurl=""):
        """
        Runs wrman with required checks.

        """
        agent_name = 'wrman'
        if (wurl != ""):
            url = wurl
        else:
            url = self.url

        # Check if the url is queued in WRQueue for WRMAN agent
        wr_query = ("select agent_name from [D2].[dbo].[WRQueue] (nolock) where [url] like \'%s\' escape \'!\'" % url)
        wlist = self.d2_obj.get_select_data(wr_query)
        wr_agent = wlist[0]['agent_name']

        if wr_agent != "WRMAN":
            # log test failure
            msg = 'url- [%s] not queued for WRMAN !!' % url
            logging.critical(msg)
            raise TestFailure(msg)

        args = ' -n 50 '
        self.set_high_priority(url)
        self.wrman_obj = Agents("WRMAN")
        self.wrman_obj.run_agent(agent_args="-t 10 -n 20 -D",output_file='wrman_out.txt')
        lfile = os.path.abspath(self.wrman_obj.output_file)  # wrman log

        # Verify wrua log file for error msg if any
        sstr = "ERROR"

        with open(lfile, 'rb') as fpr:
            if sstr.lower() in str(fpr.read().lower()):
                raise ValidationError('%s log file: %s' % self.agent_name, lfile + ' has errors !!')

        self.webrep = self.fetch_webrep(url)

    def execute_wr_agent_workflow(self):
        """
        Runs tman, wrua and does required checks.

        Should be called typically after sfimport is run

        """
        logging.info("Executing workflow for agent [%s]" % self.agent_name)

        logging.info("Running tman...")

        # Run tman
        self.tman_obj.run_agent(agent_args="-d -i -s -n 10 -D",output_file='tman_out.txt')

        # Verify tman log file for error msg if any
        sstr = "ERROR"
        lfile = os.path.abspath(self.tman_obj.output_file)  # wrua log

        with open(lfile, 'rb') as fpr:
         if sstr.lower() in str(fpr.read().lower()):
                raise ValidationError('%s log file: %s' % self.agent_name, lfile \
                                      + ' has errors !!')

        # check in build table
        url_exists = self.url_exists_in_db()

        if (url_exists == False):

            msg = 'url- [%s] not found in build table after tman run!!' % self.url
            logging.critical(msg)
            raise TestFailure(msg)
        else:
            msg = 'url- [%s] found in build table after tman run!!' % self.url
            logging.info(msg)

        # Set top priority si that the url gets processed by the agent

        self.set_high_priority(self.url)

        if (self.url1 != ""):
             self.set_high_priority(self.url1)

        logging.info("Running [%s]..." % self.agent_name)

        # Run web rep agent wrua/crua
        self.wrua_obj.run_agent(agent_args="-D", output_file='out.txt')
        lfile = os.path.abspath(self.wrua_obj.output_file)  # log
        # Verify wrua log file for error msg if any
        sstr = "ERROR"

        with open(lfile, 'rb') as fpr:
            if sstr in str(fpr.read().lower()):
                if "sfdb_get_ds_facet_info(): ERROR: Problem running query" in fpr.read():
                   logging.error('Inside execute_wr_agent_workflow: Error due to data not available in a table which is no more active, to be ignored ')
                else:
                    raise ValidationError('%s log file: %s' % self.agent_name, lfile \
                                      + ' has errors !!')

        # Verify the web reputation score of url/domain in D2.WebReputation table.

        wr_exists = self.url_exists_in_db("WebReputation")

        if (wr_exists == False):

            #log test failure
            msg = 'url- [%s] not found in WebReputation table after %s run !!' % (self.agent_name, self.url)
            logging.critical(msg)
            raise TestFailure(msg)
        else:
            msg = 'url- [%s] found in WebReputation table after tman run!!' % self.url
            logging.info(msg)

        self.webrep = self.fetch_webrep(self.url)
        self.child_webrep = self.fetch_webrep(self.url, "child_rep")

        #Query
        if (self.url1 != ""):
            self.webrep1 = self.fetch_webrep(self.url1)
            self.child_webrep1 = self.fetch_webrep(self.url1, "child_rep")

            #def test_log_file
    def execute_crua(self, wurl=""):
        """
        Runs crua with required checks.

        """
        agent_name = 'crua'
        if (wurl != ""):
            url = wurl
        else:
            url = self.url

        self.set_high_priority(url)
        self.crua_obj = Agents("CRUA")
        self.crua_obj.run_agent(agent_args="-t 10 -n 20 -D",output_file='crua_out.txt')
        lfile = os.path.abspath(self.crua_obj.output_file)  # wrman log

        # Verify wrua log file for error msg if any
        sstr = "ERROR"

        with open(lfile, 'rb') as fpr:
            if sstr.lower() in str(fpr.read().lower()):
                raise ValidationError('%s log file: %s' % self.agent_name, lfile + ' has errors !!')

        self.webrep = self.fetch_webrep(url)
        self.child_webrep = self.fetch_webrep(self.url, "child_rep")
