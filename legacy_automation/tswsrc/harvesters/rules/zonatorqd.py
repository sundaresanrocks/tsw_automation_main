"""
This harvester starts with an invocation of Perl Script instead of a
a direct start_harvester.sh
"""
from harvesters.harvester_config import ZonatorQDConfig

__author__ = 'Anurag'

import logging

import runtime
from framework.test import SandboxedTest
from harvesters.harvester import Harvester


#empty /usr2/smartfilter/import/harvest_processor/data/ZonatorQD/source_file_archive/*
# remove /usr2/smartfilter/import/harvest_processor/data/ZonatorQD/zonator_ff_domains.txt.previous
# touch /usr2/smartfilter/import/harvest_processor/data/ZonatorQD/zonator_ff_domains.txt.previous

# copy the perl script to current directory to a file named jars_in

# start harvester by following command
from lib.exceptions import TestFailure


class ZonatorQDFunc(SandboxedTest):

    def test_01(self):
        ignore_errors = [
            'log4j:WARN No appenders could be found for logger (org.xnio).',
            'log4j:WARN Please initialize the log4j system properly.',
            'RuleAgent(default) INFO (Mon Feb 03 02:09:59 CST 2014): Configuring with newInstance=false, secondsToRefresh=30',
            'RuleAgent(default) INFO (Mon Feb 03 02:09:59 CST 2014): Configuring package provider : URLScanner monitoring URLs:  http://tsqaguvnor.wsrlab:8080/drools-guvnor-5.1.0/org.drools.guvnor.Guvnor/package/tsw.harvester.zonatorqd/LATEST',
            'RuleAgent(default) INFO (Mon Feb 03 02:09:59 CST 2014): Applying changes to the rulebase.',
            'RuleAgent(default) INFO (Mon Feb 03 02:09:59 CST 2014): Adding package called tsw.harvester.zonatorqd',
            '\n']
        ssh_obj = runtime.get_ssh('localhost',user = 'toolguy')
        hcon = ZonatorQDConfig()
        Harvester.clean_any_dir(hcon.archive_dir)
        remove_prev = 'rm %s' % hcon.previous_file
        logging.info(remove_prev)
        ssh_obj.execute(remove_prev)
        touch_prev = 'touch %s' % hcon.previous_file
        logging.info(touch_prev)
        ssh_obj.execute(touch_prev)
        stdout,stderr = ssh_obj.execute(hcon.start_zonator_harvester)
        if len(stderr) != 0:
            if 'ERROR' in stderr.strip() or 'Exception' in stderr.strip():
                raise TestFailure(stderr)



