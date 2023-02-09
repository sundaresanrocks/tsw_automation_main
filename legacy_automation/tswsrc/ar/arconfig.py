"""
================================
Autorating related settings
================================
"""

import sys
import time
import logging

from lib.db.mssql import TsMsSqlWrap
import runtime
from libx.process import OSProcessHandler
import runtime


#from framework.config.ar import AR2 as EnvConClass
from domip.tcDIBP import CallAgents
#todo: remove above statement
logging.warning('Remove default envcon variable!')
from lib.build import Build
import datetime
from lib.exceptions import ProcessingError

LQM_MAX_TIMEOUT = 120
LQM_TIMEOUT_INTERVAL = 10
WFA_MAX_TIMEOUT = 120
WFA_TIMEOUT_INTERVAL = 10
SCORER_MAX_TIMEOUT = 300
SCORER_TIMEOUT_INTERVAL = 20
SCORER_TOLERANCE_PERCENT = 80 #95

class InternalVarsSSH:
    """Interal class for internal vars"""
    def __init__(self):
        """ set vars to None"""
        self.scorer = None
        self.as_root = None
        self.scorer_root = None


class ARSystem:
    """
    Contains connection to various auto rating machines, databases.
    """

    def __init__(self,
                 app_s=runtime.AppServer,
                 scorer_s=runtime.SCORER):
        """constructor"""

        self.ssh = InternalVarsSSH()
        self.scorer_s = scorer_s
        self.app_s = app_s

        self.u2_con = TsMsSqlWrap('U2')
        self._connect(app_s.host, scorer_s.host)

    def _connect(self, app_server, scorer_server): 
        """establish connection with remote sytems"""
        logging.info('Connecing to the Scorer, App server...')
        dt1 = datetime.datetime.now()
        self.ssh.scorer = runtime.get_ssh(scorer_server, 'toolguy')
        self.ssh.as_root = runtime.get_ssh(app_server, 'root')
        self.ssh.scorer_root = runtime.get_ssh(scorer_server, 'root')
        dt2 = datetime.datetime.now() - dt1
        logging.debug('Connection took %s seconds', dt2.seconds)

    def _setup_scorer_web_cache(self):
        """clean web cache on scorers machine"""
        self.ssh.scorer.execute('mkdir -p /tmp/webcache')
        self.ssh.scorer.execute('rm -rf /tmp/webcache/*')

    def _clean_fetcher_results(self):
        """remove all fetcher results from fetcher table"""
        _qry = 'delete from fetch_results'
        self.u2_con.execute_sql_commit(_qry)

    def _db_clean_all(self):
        """remove all irrelevent entries from U2 database"""
        _qryl = ['delete from fetch_results',
                 'delete from scorer_event',
                 'delete from scorer_event_detail',
                 'delete from activeprocessinstance',
                 'delete from categories',
                 'delete from harvester_event where url_id >= 56515406',
                 'delete from language_stats where url_id >= 56515406',
                 'delete from akamai',
                 'delete from queue']
        #_qryl.append('delete from WorkTask')
        ####_qryl.append('DBCC CHECKIDENT (scorer_event_detail, reseed, 72036854775808 )')

        #_qryl.append('delete from url_info where url_id >= 56515406')
        #_qryl.append('delete from url_state where url_id >= 56515406')
        #_qryl.append('delete from urls where url_id >= 56515406')
        # execute all queries
        [self.u2_con.execute_sql_commit(_qry) for _qry in _qryl]



    def _stop_puppet(self): #done
        """stop all puppet systems"""
        logging.info('Turning puppet OFF...')
        self.ssh.scorer_root.service_stop('puppet')
        self.ssh.as_root.service_stop('puppet')

    def _stop_ar_system(self):#done
        """Stop all remote systems"""
        logging.info('Stop all remote systems...')
        self.scorers_stop()
   #$     self.ssh.as_root.service_stop('jboss')

    def _clear_logs(self):
        """clear all log files"""
        logging.info('Clearing the logs...')
        self.ssh.as_root.execute('rm -f ' + ' '.join(runtime.ARLOG.as_logs))
        self.ssh.scorer.execute ('rm -f ' + ' '.join(runtime.ARLOG.scorer_logs))

    def _yum_update(self):
        """yum updates all systems"""
        self.ssh.as_root.yum_update()
        self.ssh.scorer_root.yum_update()

    def _odbc_setup(self):
        """setup odbc all systems"""
        self.ssh.scorer_root.ts_odbc_setup(runtime.DB.U2_name, runtime.DB.D2_name, runtime.DB.R2_name)
        self.ssh.as_root.ts_odbc_setup(runtime.DB.U2_name, runtime.DB.D2_name, runtime.DB.R2_name)

    def _aus_reset_all_urls(self):
        """reset all urls for LQM"""
        from ar.qrytemplates import WORKTASK_TWEAK, \
                                            URLSTATE_TWEAK, \
                                            QUEUE_TWEAK
        self.u2_con.execute_sql_commit(QUEUE_TWEAK)
        self.u2_con.execute_sql_commit(URLSTATE_TWEAK)
        self.u2_con.execute_sql_commit(WORKTASK_TWEAK)

    def _aus_count_urls(self):
        """return number of urls that will be processed by LQM"""
        return 

    def _fix_app_server_standalone_full_ha(self):#done
        """fixes app server standalone-full-ha.xml file"""
        #standalone-full-ha.xml
        self.ssh.as_root.sed_file(runtime.PuppetConf.db_host,
                                  runtime.DB.U2_host, #assuming hosts are same
                                  self.app_s.xml_standalone)
        #todo: get file, modify in python, put back for all
    def _fix_app_server_application_properties(self):#done
        """fixes app server application.properties file"""
        #application.properties
        raise Exception("Use Properties")
        #
        # self.ssh.as_root.sed_file(
        #         'autorating.mongohost=' + runtime.PuppetConf.mdb_host,
        #         'autorating.mongohost=' + runtime.Mongo.host,
        #         self.app_s.prop_application)
        # self.ssh.as_root.sed_file(
        #         'autorating.mongodb=' + runtime.PuppetConf.mdb_name,
        #         'autorating.mongodb=' + runtime.Mongo.dbname,
        #         self.app_s.prop_application)
        # self.ssh.as_root.sed_file(
        #         'autorating.mongoport=' + runtime.PuppetConf.mdb_port,
        #         'autorating.mongoport=' + str(runtime.Mongo.port),
        #         self.app_s.prop_application)
        # self.ssh.as_root.sed_file(
        #         'autorating.mongocollection=' + runtime.PuppetConf.mdb_coll,
        #         'autorating.mongocollection=' + runtime.Mongo.coll,
        #         self.app_s.prop_application)

    def _fix_scorer_server_properties(self):#done
        """fixes scorer server properties"""
        #scorer.properties
        #sqm.webservice                           = 
        self.ssh.scorer.sed_file(
                runtime.PuppetConf.as_host,
                self.app_s.host,
                self.scorer_s.prop_scorer)

        #worktaskpopulator.properties
        self.ssh.scorer.sed_file(
                'appserver=' +runtime.PuppetConf.as_host,
                'appserver=' +self.app_s.host,
                self.scorer_s.prop_worktask)
        self.ssh.scorer.sed_file(
                'maxQueueSize=' + runtime.PuppetConf.wqp_max_queue,
                'maxQueueSize=' + runtime.SCORER.wqp_max_queue,
                self.scorer_s.prop_worktask)
        self.ssh.scorer.sed_file(
                'fetchCount=' + runtime.PuppetConf.wqp_fetch_count,
                'fetchCount=' + runtime.SCORER.wqp_fetch_count,
                self.scorer_s.prop_worktask)
        #urlscheduler.properties
        self.ssh.scorer.sed_file(
                'appserver=' + runtime.PuppetConf.as_host,
                'appserver=' + self.app_s.host,
                self.scorer_s.prop_url_schduler)
        #jboss-ejb-client.properties
        #'remote.connection.default.host=' 
        self.ssh.scorer.sed_file(
                'remote.connection.default.host=' + runtime.PuppetConf.as_host,
                'remote.connection.default.host=' + self.app_s.host,
                self.scorer_s.prop_jboss_ejb)

        #fetcher.properties
        comment = ''
        host = self.scorer_s.proxy_host
        port = self.scorer_s.proxy_port
        if self.scorer_s.proxy_host == '':
            comment = '#'
        lines ='%sWebFetcherScorer.proxyHost = %s\n' % (comment, host) \
             + '%sWebFetcherScorer.proxyPort = %s\n' % (comment, port)
        tmp_file = './fetcher.properties.tmp'
        with open(tmp_file , 'w+') as fpw:
            fpw.write(lines)
        self.ssh.scorer_root.execute('rm -f %s' % runtime.SCORER.prop_fetcher)
        self.ssh.scorer.put(tmp_file, runtime.SCORER.prop_fetcher)


    def prepare_environment(self):
        """Prepares the autorating environment"""
        #todo: reset minimal db ?
               #db execute cleanup queries ?

        self._stop_puppet()
        self._stop_ar_system()          #stop before yum update!
        self._yum_update()
        self._odbc_setup()
    #    self._db_clean_all() #todo: remove comment!

    def _wait_for_aus(self):
        """
        #. restarts LQM (app server)
        #. waits till LQM puts URLs in worktask!
        Raises Exception if Timeout
        """
        count1 = self.u2_con.get_table_row_count('WorkTask')
        wait_time = 0
        while LQM_MAX_TIMEOUT > wait_time:
            wait_time += LQM_TIMEOUT_INTERVAL
            time.sleep(LQM_TIMEOUT_INTERVAL)
            count2 = self.u2_con.get_table_row_count('WorkTask')
            if count2 > count1:
                logging.info('LQM: new urls in worktask: %s', 
                             str(count2 - count1))
                time.sleep(LQM_TIMEOUT_INTERVAL)        #2nd sleep as buffer
                return True
        raise ProcessingError('LQM: No URLs in WorkTask!')

    def dispatch_urls(self):
        """
        #. Dispatch URLs
        Raises Exception if Timeout
        """
        QRY_WFA = 'select * from worktask where dispatchcount=1'
        count0 = self.u2_con.get_table_row_count('WorkTask')
        count1 = self.u2_con.get_row_count(QRY_WFA)
        #### dispatch URLs
        _cmd = '%s %s %s' %(runtime.ENV.get_env_for_ssh_cmd(),
                            runtime.SCORER.bin_aqp,
                           runtime.SCORER.prop_worktask)
        self.ssh.scorer.exec_recv_exit_code(_cmd)

        wait_time = 0
        while WFA_MAX_TIMEOUT > wait_time:
            wait_time += WFA_TIMEOUT_INTERVAL
            time.sleep(WFA_TIMEOUT_INTERVAL)
            count2 = self.u2_con.get_row_count(QRY_WFA)
            logging.debug('WFA: URLs dispatched!: %s', str(count2 - count1))
            if count2 >= count1 and count2>= count0:
                logging.info('WFA: URLs dispatched!: %s', 
                             str(count2 - count1))
                return True
        raise ProcessingError('WFA: URLs NOT dispatched!')

    def _wait_for_scorer(self):
        """
        #. starts Scorer
        #. waits till Scorer scorers from worktask
        Raises Exception if Timeout
        """
        QRY_PENDING = 'select taskid from worktask where returnCode is NULL'
        count1 = self.u2_con.get_row_count(QRY_PENDING)
        logging.info('SCORER: Total URLs to be scored: %s' % count1)
        if count1 <= 0:
            raise ProcessingError('SCORER: No Pending URLs in worktask')
        #### restart jboss
        self.scorers_start()
        wait_time = 0
        percent = 0
        while SCORER_MAX_TIMEOUT > wait_time:
            wait_time += SCORER_TIMEOUT_INTERVAL
            time.sleep(SCORER_TIMEOUT_INTERVAL)
            count2 = self.u2_con.get_row_count(QRY_PENDING)
            percent = float(count1 - count2)/count1 * 100  #count1==0 raise err
            logging.info('SCORER: Wait time: %ss ' % str(wait_time) 
                         + 'Percent urls scored: %s' % str(percent))
            if count2 == 0:
                logging.info('SCORER: URLs scored!: %s', 
                             str(count1 - count2))
                return True
        raise ProcessingError('SCORER: Percent URLs scored:%s' % str(percent))

    def scorers_stop(self):
        """stop chain scorers process"""
        pkill = OSProcessHandler('ChainedScorer.sh', 
                                 ssh_con=self.ssh.scorer,
                                 full_format = True)
        pkill.kill_processes()

    def scorers_start(self):
        """start chain scorers process"""
        self.scorers_stop()
        #### ensure no chainedscorers are running
        osp_obj = OSProcessHandler('ChainedScorer.sh', 
                              full_format = True, 
                              ssh_con=self.ssh.scorer, 
                              exclude_grep=True
                              )
        scorer_pids = osp_obj.get_pid_list()
        if len(scorer_pids) != 0:
            raise EnvironmentError('Scorer: Unable to kill process.' \
                        + 'AutoratingChainedScorer process is running!')

        #### start the AutoratingChainedScorer
        _cmd = 'nohup %s' % runtime.ENV.get_env_for_ssh_cmd() \
               + self.scorer_s.bin_acs \
               + ' ' + self.scorer_s.prop_scorer \
               + ' ' + self.scorer_s.prop_fetcher \
               + ' >scorer_run.log 2>&1 '
        logging.debug('Scorer: Starting scorers: %s', _cmd)
        channel = self.ssh.scorer.exec_open_channel(_cmd)
        time.sleep(2)
        scorer_pids = osp_obj.get_pid_list()
        if len(scorer_pids) <= 0:
            raise EnvironmentError('Scorer: Unable to start ChainedScorers')
        logging.info('Scorer: ChainedScorer is running, Count=%s', 
                     len(scorer_pids))
        return True

    def _sfimport_db_tweaks(self, urls):
        """sfimport, tweak urls in db"""
        #sfimport all urls
        local_file_name = 'tmp-ar-sfimport.txt'
        with open(local_file_name, 'r') as fpw:
            '\n'.join(urls)
        stdoe = self.ssh.scorer.ts_sfimport(local_file_name)
        #stdoe = self.ssh.scorer.ts_sfimport(runtime.data_path \
        #                                    + '/tsw/ar/url-list-spl.txt')
        from lib.db.u2_urls import U2Urls
        u2url = U2Urls(self.u2_con)
        url_86 = []#'HTTP://PORN-RANK.COM/cgi-bin/sw.cgi']
        url_352 = []#['HTTP://CUMFIESTA.COM']
        url_state_2 = []# ['HTTP://INCHSONG.COM/morecash']
        url_schedule_2 = []#['HTTP://INCHSONG.COM/morecash']
        def get_url_id(url):
            try:
                uid = u2url.get_id_from_url(url)
                return uid
            except ProcessingError as err:
                if 'URLNOTFOUND' in err.args[0]:
                    logging.warning(err.args[0] + ' url: %s' % url)
                    return None
                raise
        _qryl = []
        for url in url_86:
            uid = get_url_id(url)
            if uid:
                _qry = 'update queue set queue=86 where url_id = %s' % uid
                _qryl.append(_qry)
        for url in url_352:
            uid = get_url_id(url)
            if uid:
                _qry = 'update queue set queue=86 where url_id = %s' % uid
                _qryl.append(_qry)
        for url in url_state_2:
            uid = get_url_id(url)
            if uid:
                _qry = 'update url_state set state_id=2 where url_id = %s' % uid
                _qryl.append(_qry)
        for url in url_schedule_2:
            uid = get_url_id(url)
            if uid:
                _qry = 'update url_state set scheduled_count=2 ' \
                     + 'where url_id = %s' % uid
                _qryl.append(_qry)

        #execute all queries
        [self.u2_con.execute_sql_commit(_qry) for _qry in _qryl]


    def setup(self):
        """setup autorating system"""
   #     self._stop_ar_system()
   #     self._clear_logs()
        #create sandbox
    #$    ste = SandboxTestEnvironment('tsw/ar', 'setup')
    #$    ste.setup_sandbox()
        logging.info('Initialize remote systems...')
    #    stdoe = self.ssh.scorer.ts_sfimport(runtime.data_path \
    #                                        + '/tsw/ar/url-list.txt')

    #    self._lqm_reset_all_urls()
        #handle special urls
    #   self._sfimport_db_tweaks()
    #    sys.exit()
        self._fix_app_server_standalone_full_ha()
        self._fix_app_server_application_properties()
        #### restart jboss
    #    self.ssh.as_root.service_restart('jboss')

        #start autorating url scheduler
   #     self._wait_for_aus(count1)

        #scorer - fix fetcher, scorer.properties
        self._fix_scorer_server_properties()
        self._clean_fetcher_results()
        self._setup_scorer_web_cache()

        sys.exit()

        # #wfa - wait for URLs to be dispatched
        #
        # self.dispatch_urls()
        # try:
        #     self._wait_for_scorer()
        # except ProcessingError as err:
        #     logging.error(err)
        #     percent = float(str(err.args[0]).rpartition(':')[2][:4])
        #     if percent < SCORER_TOLERANCE_PERCENT:
        #         raise
        # logging.info('SETUP: Scorers started')
        #
        # #exit sandbox
        # #ste.exit_sandbox()

    def _build_master(self):
        """ build the system """
        exe_agents = CallAgents()
        exe_agents.call_all_agents()

        #   Calling build process
        build_obj = Build()
        build_obj.reset_build()
        print('EXECUTING BUILD')
        result = build_obj.build_run('master', 'all')
        logging.warning(result)

def _system_unit_tests():
    """unit tests for ar system"""
    obj = ARSystem()
    #osp = OSProcessHandler('ChainedScorers', 
    #                      full_format = True, 
    #                      ssh_con=obj.scorer_ssh, 
    #                      exclude_grep=True
    #                      )
    #print osp.get_pid_list()
    #print osp.kill_processes()

    #osp = OSProcessHandler('ChainedScorers\' | grep -v \'grep', 
    #                      full_format = True, 
    #                      ssh_con=obj.scorer_ssh)
    #print osp.get_pid_list()
    #print obj.scorers_stop()

def _quick_autorate():
    """autorate all urls in WFA"""
    #app server - wait for LQM to put URLs in queue

if __name__ == '__main__':

#def _end2end():
    '''end to end flow'''
#    _quick_autorate()
#    obj = ARSystem()
 #   obj.prepare_environment()
#    obj.setup()
    #obj._wait_for_scorer()
    arssh = runtime.get_ssh('tsqa32arscorer01.wsrlab', 'toolguy')
    # arpo.set_worktask(envcon.SCORER.prop_worktask , 'nion')



    # {
    # "status": "success",
    # "data": {"sha256":"c624031238f7e4915b5fbf2ec9d6b9b74e3641b936a161a4b62cdf40b242be04",
    #          "cl-hash":"0X012e8c6afcd2fd3fadf669a6",
    #          "original-url":"google.com",
    #          "md5":"0X15d53530a03f455fa94dce410dcdf884",
    #          "canon-url":"*:\/\/GOOGLE.COM",
    #          "db-hash":"962cb790495d088406731a41"}
    # }

    raise Exception()
