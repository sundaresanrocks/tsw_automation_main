# # -*- coding: utf-8 -*-
__author__ = 'Anurag'

import logging

from lib.properties.sshprop import SSHProperties
import runtime
from lib.utils.jboss import Jboss
from framework.ddt import testgen_file, tsadriver
from framework.test import SandboxedTest
from lib.exceptions import TestFailure
from ar.arlib import Check
from lib.utils.brm import BRMUtils
from lib.utils.jar import JarUtils


@tsadriver
class SanityAutorating(SandboxedTest):
    """"""

    @classmethod
    def setUpClass(self):
        self.username = 'toolguy'
        self.version = BRMUtils(TestInfo.brm_jenkins_host, TestInfo.brm_sprint_branch,
                                TestInfo.brm_build_number).get_tsw_version_from_jenkins()
        self.CONF_HOME = '/opt/sftools/conf/'
        self.application_properties = self.CONF_HOME + 'application.properties'
        self.xml_standalone = '/opt/sftools/java/jboss7/standalone/configuration/standalone-full-ha.xml'
        self.ejb_client = self.CONF_HOME + 'jboss-ejb-client.properties'
        scorer_ssh = runtime.get_ssh(runtime.SCORER.host, 'root')
        scorer_ssh.execute('/etc/init.d/puppet stop')
        scorer_ssh.put(localpath=runtime.data_path + '/tsw/ar/odbc.ini', remotepath='/etc/odbc.ini')
        scorer_ssh.put(localpath=runtime.data_path + '/tsw/ar/freetds.conf', remotepath='/etc/freetds/freetds.conf')
        scorer_ssh.put(localpath=runtime.data_path + '/tsw/ar/scorer.properties',
                       remotepath='/opt/sftools/conf/scorer.properties')
        scorer_ssh.put(localpath=runtime.data_path + '/tsw/ar/urlscheduler.properties',
                       remotepath='/opt/sftools/conf/urlscheduler.properties')
        scorer_ssh.put(localpath=runtime.data_path + '/tsw/ar/worktaskpopulator.properties',
                       remotepath='/opt/sftools/conf/worktaskpopulator.properties')
        app_ssh = runtime.get_ssh(runtime.AppServer.host, 'root')
        app_ssh.execute('/etc/init.d/puppet stop')
        app_ssh.put(localpath=runtime.data_path + '/tsw/ar/standalone-full-ha.xml', remotepath=self.xml_standalone)


    @testgen_file('tsw/ar/sanity_conf.txt')
    def test_01(self, data):
        """TS-1432,1433,1434,1435 Checks for presence of mandatory properties files"""
        ssh_obj = runtime.get_ssh(runtime.SCORER.host, user=self.username)
        result = ssh_obj._file_exists(data)
        if not result:
            raise TestFailure(data + ' is not present on ' + runtime.SCORER.host)

    @testgen_file('tsw/ar/sanity_scripts.txt')
    def test_02(self, data):
        """TS-1436,1437,1438,1439 Checks for presence of mandatory sh files and verifies version of jars"""
        chk_list = ['scorers', 'harvesters']
        ssh_obj = runtime.get_ssh(runtime.SCORER.host, user=self.username)
        result = ssh_obj._file_exists(data)
        if not result:
            raise TestFailure(data + ' is not present on ' + runtime.SCORER.host)
        obj = JarUtils(runtime.SCORER.host, self.username)
        obj.compare_classpath_n_list(data, chk_list, raise_exception=False, build_props=False)
        if not result:
            raise TestFailure('classpath does not have JAR with version ' + self.version)

    def test_03(self):
        """TS-1442:Sanity: Check if all property files point to the same APP Server"""
        arssh = runtime.get_ssh(runtime.SCORER.host, self.username)
        err_list = []
        expected_property = 'appserver'
        expected_value = runtime.AppServer.host
        configs = ['worktaskpopulator.properties', 'urlscheduler.properties', 'scorer.properties']
        for i in configs:
            arpo = SSHProperties(arssh, self.CONF_HOME + i)
            logging.warning(arpo.pobj[expected_property])
            if arpo.pobj[expected_property] != expected_value:
                err_list.append('%s file has appserver as %s instead of %s' % (
                    self.CONF_HOME + i, arpo.pobj[expected_property], expected_value))

        path = self.CONF_HOME + 'jboss-ejb-client.properties'
        expected_property = 'remote.connection.default.host'
        expected_value = runtime.AppServer.host
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append(
                '%s file has appserver as %s instead of %s' % (path, arpo.pobj[expected_property], expected_value))

        path = self.CONF_HOME + 'scorer.properties'
        expected_property = 'sqm.webservice'
        expected_value = 'http://' + runtime.AppServer.host + ':8080/wfa/ScorerQueueManagerBean'
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append(
                '%s file has appserver as %s instead of %s' % (path, arpo.pobj[expected_property], expected_value))

        expected_property = 'scorer.executor.appserver'
        expected_value = runtime.AppServer.host
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append(
                '%s file has appserver as %s instead of %s' % (path, arpo.pobj[expected_property], expected_value))

        if len(err_list) != 0:
            raise TestFailure('\n'.join(err_list))

    def test_04(self):
        """TS-1431:Sanity: Appserver status : Verify that appserver is alive and running"""
        service_name = 'jboss'
        ssh_obj = runtime.get_ssh(runtime.AppServer.host, user=self.username)
        if not ssh_obj.service_is_running(service_name):
            raise TestFailure('JBOSS is NOT running on ' + runtime.SCORER.host)

    def test_05(self):
        """TS-1430:Sanity: Appserver configurations : Guvnor server and database"""
        err_list = []
        check_obj = Check()
        arssh = runtime.get_ssh(runtime.AppServer.host, self.username)
        scssh = runtime.get_ssh(runtime.SCORER.host, self.username)
        expected_property = 'rulebase.hostname'
        expected_value = runtime.AppServer.guvnor_server
        arpo = SSHProperties(arssh, self.application_properties)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append('%s file has appserver as %s instaead of %s' % (
                self.application_properties, arpo.pobj[expected_property], expected_value))
        expected_property = 'guvnor'
        path = self.CONF_HOME + 'scorer.properties'
        arpo = SSHProperties(scssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append(
                '%s file has appserver as %s instaead of %s' % (path, arpo.pobj[expected_property], expected_value))
        check_obj.property_check_in_standalone_xml(runtime.AppServer.host, self.xml_standalone)
        if len(err_list) != 0:
            raise TestFailure('%s' % err_list)

    @testgen_file('tsw/ar/jms_queues.txt')
    def test_06(self, data):
        """TS-1596,1597,1598"""
        jboss_obj = Jboss(runtime.AppServer.host)
        queues = jboss_obj.jms_metrics(data)
        if len(queues) == 0:
            raise TestFailure(data + ' is not present in JMS Destinations')
        for i in queues:
            if len(i) == 0:
                raise TestFailure(
                    'Cannot connect to JBOSS client . Please modify localhost to <IPADDRESS> on /opt/sftools/java/jboss7/bin/jboss-cli.xml on %s' \
                    % runtime.AppServer.host)
            logging.info(i)

    def test_07(self):
        """TS-1441:Sanity: All Scorers properties"""
        arssh = runtime.get_ssh(runtime.SCORER.host, self.username)
        err_list = []
        #Residential Scorer
        expected_property = 'ResidentialScorer.whitelist'
        fp = self.CONF_HOME + 'residential/whitelist.txt'
        expected_value = fp
        path = self.CONF_HOME + 'scorer.properties'
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append('%s points to %s instead of %s ' % (
                runtime.AppServer.host, arpo.pobj[expected_property], expected_value))
        result = arssh._file_exists(fp)
        if not result:
            err_list.append(fp + ' is not present on ' + runtime.SCORER.host)

        expected_property = 'ResidentialScorer.blacklist'
        fp = self.CONF_HOME + 'residential/blacklist.txt'
        expected_value = fp
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append('%s points to %s instead of %s ' % (
                runtime.AppServer.host, arpo.pobj[expected_property], expected_value))
        result = arssh._file_exists(fp)
        if not result:
            err_list.append(fp + ' is not present on ' + runtime.SCORER.host)
        if len(err_list) != 0:
            raise TestFailure('%s' % err_list)

    def test_08(self):
        """"""
        #Parked Domain Scorer
        arssh = runtime.get_ssh(runtime.SCORER.host, self.username)
        err_list = []
        expected_property = 'ParkedDomainScorer.whitelist'
        fp = self.CONF_HOME + 'pd/pd_whitelist.txt'
        expected_value = fp
        path = self.CONF_HOME + 'scorer.properties'
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append('%s points to %s instead of %s ' % (
                runtime.AppServer.host, arpo.pobj[expected_property], expected_value))
        result = arssh._file_exists(fp)
        if not result:
            err_list.append(fp + ' is not present on ' + runtime.SCORER.host)

        expected_property = 'ParkedDomainScorer.blacklist'
        fp = self.CONF_HOME + 'pd/pd_blacklist.txt'
        expected_value = fp
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append('%s points to %s instead of %s ' % (
                runtime.AppServer.host, arpo.pobj[expected_property], expected_value))
        result = arssh._file_exists(fp)
        if not result:
            err_list.append(fp + ' is not present on ' + runtime.SCORER.host)

        expected_property = 'ParkedDomainScorer.iplist'
        fp = self.CONF_HOME + 'pd/pd_ips.txt'
        expected_value = fp
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append('%s points to %s instead of %s ' % (
                runtime.AppServer.host, arpo.pobj[expected_property], expected_value))
        result = arssh._file_exists(fp)
        if not result:
            err_list.append(fp + ' is not present on ' + runtime.SCORER.host)

        if len(err_list) != 0:
            raise TestFailure('%s' % err_list)

    def test_09(self):
        #DCC Scorer
        arssh = runtime.get_ssh(runtime.SCORER.host, self.username)
        err_list = []
        expected_property = 'DCCScorer.rulePackage'
        fp = self.CONF_HOME + 'mwgdcc/mwg-package.zip'
        expected_value = fp
        path = self.CONF_HOME + 'scorer.properties'
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append('%s points to %s instead of %s ' % (
                runtime.AppServer.host, arpo.pobj[expected_property], expected_value))
        result = arssh._file_exists(fp)
        if not result:
            err_list.append(fp + ' is not present on ' + runtime.SCORER.host)

        expected_property = 'DCCScorer.supportedLanguages'
        fp = 'en'
        expected_value = fp
        path = self.CONF_HOME + 'scorer.properties'
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append('%s points to %s instead of %s ' % (
                runtime.AppServer.host, arpo.pobj[expected_property], expected_value))

        if len(err_list) != 0:
            raise TestFailure('%s' % err_list)

    def test_10(self):
        #CLD Scorer
        arssh = runtime.get_ssh(runtime.SCORER.host, self.username)
        err_list = []
        expected_property = 'CLDLanguageScorer.languagemap'
        fp = self.CONF_HOME + 'cld_lang_map.txt'
        expected_value = fp
        path = self.CONF_HOME + 'scorer.properties'
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append('%s points to %s instead of %s ' % (
                runtime.AppServer.host, arpo.pobj[expected_property], expected_value))
        result = arssh._file_exists(fp)
        if not result:
            err_list.append(fp + ' is not present on ' + runtime.SCORER.host)
        if len(err_list) != 0:
            raise TestFailure('%s' % err_list)

    def test_11(self):
        #URLMetadata Scorer
        arssh = runtime.get_ssh(runtime.SCORER.host, self.username)
        err_list = []
        expected_property = 'UrlMetaDataScorer.urlmetadatascorer_properties'
        fp = self.CONF_HOME + 'metadatascorer.properties'
        expected_value = fp
        path = self.CONF_HOME + 'scorer.properties'
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append('%s points to %s instead of %s ' % (
                runtime.AppServer.host, arpo.pobj[expected_property], expected_value))
        result = arssh._file_exists(fp)
        if not result:
            err_list.append(fp + ' is not present on ' + runtime.SCORER.host)
        if len(err_list) != 0:
            raise TestFailure('%s' % err_list)

    def test_12(self):
        """TS-1488:Check for MongoDB configuration and collection name on app server"""
        arssh = runtime.get_ssh(runtime.AppServer.host, self.username)
        err_list = []
        expected_property = 'autorating.mongohost'
        expected_value = runtime.Mongo.host
        path = self.CONF_HOME + 'application.properties'
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append('%s points to mongodb %s instead of %s ' % (
                runtime.AppServer.host, arpo.pobj[expected_property], expected_value))
        if len(err_list) != 0:
            raise TestFailure('%s' % err_list)

    def test_13(self):
        """DCC Silent Mode scorer in scorer properties"""
        arssh = runtime.get_ssh(runtime.SCORER.host, self.username)
        err_list = []
        expected_property = 'DCCSilentModeScorer.rulePackage'
        fp = self.CONF_HOME + 'mwgdcc/mwg-package-silent.zip'
        expected_value = fp
        path = self.CONF_HOME + 'scorer.properties'
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append('%s points to %s instead of %s ' % (
                runtime.AppServer.host, arpo.pobj[expected_property], expected_value))
        result = arssh._file_exists(fp)
        if not result:
            err_list.append(fp + ' is not present on ' + runtime.SCORER.host)

        expected_property = 'DCCSilentModeScorer.supportedLanguages'
        expected_value = 'pt,es,tr,en,fr,zh,ru,ja,it,de,nl'
        arpo = SSHProperties(arssh, path)
        if arpo.pobj[expected_property] != expected_value:
            err_list.append('%s points to %s instead of %s ' % (
                runtime.AppServer.host, arpo.pobj[expected_property], expected_value))

        if len(err_list) != 0:
            raise TestFailure('%s' % err_list)




