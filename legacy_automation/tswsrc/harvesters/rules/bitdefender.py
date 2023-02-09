from harvesters.harvester import *
from harvesters.harvester_config import BitDefenderConfig


class BitDefenderFunc(SandboxedTest):


    def test_resume_mode(self):
        """Run it only in Resume mode.
        Otherwise it starts collecting data from SampleDB
        and never ends in automation"""

        hcon = BitDefenderConfig()
        hcon.action_taken['Urls Ignored']='4'
        hcon.action_taken['Urls Queued']='1'
        hcon.action_taken['Urls to flat log file']='1'

        hcon.rules_matched['(Salience=000265) Queue and Crawl URL with no path']='2'
        hcon.rules_matched['(Salience=000295) Skip urls that are already Malicious']='4'

        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('BitDefender/bd_01.txt')

    def a_test_non_resume(self):
        """Test by running it in non resume mode"""
        pass