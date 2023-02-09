# -*- coding: utf-8 -*-
"""
Webcache related tests
"""
__author__ = 'Anurag'
from lib.properties.sshprop import SSHProperties
import runtime
from framework.test import SandboxedTest
from lib.exceptions import TestFailure
from libx.process import OSProcessHandler
import logging
import time
import io
import runtime


class WebCache(SandboxedTest):
    @classmethod
    def setUpClass(self):
        self.username = 'toolguy'
        self.CONF_HOME = '/opt/sftools/conf/'
        self.ssh_obj = runtime.get_ssh(runtime.SCORER.host, user=self.username)
        self.webcache = '/tmp/webcache/'
        self.start_scorer_cmd = 'nohup %s %s %s > /dev/null 2>&1 &' % \
                                (runtime.SCORER.bin_acs, runtime.SCORER.prop_scorer, runtime.SCORER.prop_fetcher)
        self.score_url = '%s %s ' % (runtime.SCORER.bin_qa_ausubmit, runtime.AppServer.host)
        logging.info('Starting Scorer')
        self.ssh_obj.execute(self.start_scorer_cmd)

    @classmethod
    def tearDownClass(self):
        process_obj = OSProcessHandler('java', full_format=True, ssh_con=self.ssh_obj)
        if process_obj.is_running():
            process_obj.kill_processes()

    def setUp(self):
        SandboxedTest.setUp(self)
        # Emptying Webcache before each test
        logging.info('Emptying WebCache')
        self.ssh_obj.execute('rm /tmp/webcache/*')

    def tearDown(self):
        SandboxedTest.tearDown(self)

    def test_sanity(self):
        """TS-1583:Check if /tmp/webcache/ exists on Scorer Box"""
        if not self.ssh_obj._file_exists(self.webcache):
            raise TestFailure(self.webcache + ' folder does not exist')

    def test_01(self):
        """TS-1581"""
        is_warc_present = False
        prop_obj = SSHProperties(self.ssh_obj, self.CONF_HOME + 'scorer.properties')
        preserveWarc = prop_obj.pobj['preserveWARCFiles']
        url = 'http://cartoonnetwork.com'
        if not preserveWarc == 'true':
            # Making preserve WARCS is true
            prop_obj.pobj['preserveWARCFiles'] = 'true'
            prop_obj.properties_put()
        self.ssh_obj.execute(self.score_url + url)
        for i in range(6):
            time.sleep(3)
            sout, serr = self.ssh_obj.execute('ls /tmp/webcache')
            if 'warc.gz' in sout:
                is_warc_present = True
                break
        if not is_warc_present:
            logging.info("WARC file not created for " + url)

    def test_02(self):
        """Individual warc files for 2 URLs crawled"""
        is_warc_present = False
        prop_obj = SSHProperties(self.ssh_obj, self.CONF_HOME + 'scorer.properties')
        preserveWarc = prop_obj.pobj['preserveWARCFiles']
        url1 = 'http://cartoonnetwork.com'
        # url2 = 'http://espnsports.com'
        if not preserveWarc == 'true':
            prop_obj.pobj['preserveWARCFiles'] = 'true'
            prop_obj.properties_put()
        self.ssh_obj.execute(self.score_url + url1)
        #self.ssh_obj.execute(self.score_url + url2)
        for i in range(6):
            sout, serr = self.ssh_obj.execute('ls /tmp/webcache')
            time.sleep(3)
            if 'warc.gz' in sout:
                buf = io.StringIO(sout)
                lines = buf.readlines()
                if len(lines) == 1:
                    is_warc_present = True
                    break
        if not is_warc_present:
            logging.info("WARC file not created for %s" % (url1))

    def test_03(self):
        """Remove WARC file if preserveWarc is False"""
        process_obj = OSProcessHandler('java', full_format=True, ssh_con=self.ssh_obj)
        if process_obj.is_running():
            process_obj.kill_processes()
        is_warc_present = None
        prop_obj = SSHProperties(self.ssh_obj, self.CONF_HOME + 'scorer.properties')
        preserveWarc = prop_obj.pobj['preserveWARCFiles']
        url = 'http://example.com'
        if preserveWarc == 'true':
            # Making preserve WARCS is true
            prop_obj.pobj['preserveWARCFiles'] = 'false'
            prop_obj.properties_put()
            logging.warning(prop_obj.pobj['preserveWARCFiles'])
        # start scorer
        self.ssh_obj.execute(self.start_scorer_cmd)
        logging.info('Submitting %s for Scoring' % url)
        self.ssh_obj.execute(self.score_url + url)
        for i in range(6):
            sout, serr = self.ssh_obj.execute('ls /tmp/webcache')
            time.sleep(3)
            if 'warc.gz' in sout:
                is_warc_present = True
                logging.info('Created WARC for ' + url)
                break
        if not is_warc_present:
            logging.info('WARC not created for ' + url)
            #waiting for 10 seconds for WARC to get deleted automatically
        for i in range(10):
            time.sleep(1)
            sout, serr = self.ssh_obj.execute('ls /tmp/webcache')
            if len(sout) == 0:
                is_warc_present = False
                break
        if is_warc_present:
            logging.info("WARC file did not get deleted in 10 seconds for " + url)

    def test_04(self):
        """Check if no WARC for nonexistant urls"""
        is_warc_present = False
        prop_obj = SSHProperties(self.ssh_obj, self.CONF_HOME + 'scorer.properties')
        preserveWarc = prop_obj.pobj['preserveWARCFiles']
        url = 'http://anurag.com'
        if not preserveWarc == 'true':
            # Making preserve WARCS is true
            prop_obj.pobj['preserveWARCFiles'] = 'true'
            prop_obj.properties_put()
        self.ssh_obj.execute(self.score_url)
        for i in range(6):
            time.sleep(3)
            sout, serr = self.ssh_obj.execute('ls /tmp/webcache')
            if 'warc.gz' in sout:
                is_warc_present = True
                break
        if is_warc_present:
            logging.info("WARC file is created for non existant " + url)

    def test_05(self):
        """Single WARC files for redirect"""
        url = 'http://www.mcafeetesting.net23.net/samples/redirect.php'
        is_warc_present = False
        prop_obj = SSHProperties(self.ssh_obj, self.CONF_HOME + 'scorer.properties')
        preserveWarc = prop_obj.pobj['preserveWARCFiles']
        if not preserveWarc == 'true':
            prop_obj.pobj['preserveWARCFiles'] = 'true'
            prop_obj.properties_put()
        self.ssh_obj.execute(self.score_url + url)
        for i in range(6):
            time.sleep(3)
            sout, serr = self.ssh_obj.execute('ls /tmp/webcache')
            if 'warc.gz' in sout:
                buf = io.StringIO(sout)
                lines = buf.readlines()
                if len(lines) == 1:
                    logging.info('%s' % lines)
                    is_warc_present = True
                    break
        if not is_warc_present:
            logging.info("WARC file not created for %s" % (url))

    def test_06(self):
        """ 404 pages serving content"""
        url = 'http://www.cuoma.com/404'
        is_warc_present = False
        prop_obj = SSHProperties(self.ssh_obj, self.CONF_HOME + 'scorer.properties')
        preserveWarc = prop_obj.pobj['preserveWARCFiles']
        if not preserveWarc == 'true':
            prop_obj.pobj['preserveWARCFiles'] = 'true'
            prop_obj.properties_put()
        self.ssh_obj.execute(self.score_url + url)
        for i in range(6):
            time.sleep(3)
            sout, serr = self.ssh_obj.execute('ls /tmp/webcache')
            if 'warc.gz' in sout:
                buf = io.StringIO(sout)
                lines = buf.readlines()
                if len(lines) == 1:
                    logging.info('%s' % lines)
                    is_warc_present = True
                    break
        if not is_warc_present:
            logging.info("WARC file not created for 404 page serving content %s" % (url))

    def test_07(self):
        """Encoding check for different language URLs"""
        url = 'http://kekkonsikiuta.seesaa.net/'
        is_warc_present = False
        prop_obj = SSHProperties(self.ssh_obj, self.CONF_HOME + 'scorer.properties')
        preserveWarc = prop_obj.pobj['preserveWARCFiles']
        if not preserveWarc == 'true':
            prop_obj.pobj['preserveWARCFiles'] = 'true'
            prop_obj.properties_put()
        self.ssh_obj.execute(self.score_url + url)
        if not is_warc_present:
            logging.info("WARC file not created for %s" % (url))

    def test_08(self):
        """ Check 2 new WARC files fo same URL twice"""
        url = 'http://example.com/'
        wait_sum = 0
        is_warc_present = False
        prop_obj = SSHProperties(self.ssh_obj, self.CONF_HOME + 'scorer.properties')
        preserveWarc = prop_obj.pobj['preserveWARCFiles']
        if not preserveWarc == 'true':
            prop_obj.pobj['preserveWARCFiles'] = 'true'
            prop_obj.properties_put()
        self.ssh_obj.execute(self.score_url + url)

        if not is_warc_present:
            logging.info("WARC file not created for %s" % (url))









