from harvesters.harvester_config import QuantcastConfig

__author__ = 'Anurag'
from harvesters.harvester import *


class QuantcastFunc(SandboxedTest):


    def test_resume_mode(self):
        """Run it only in Resume mode.
        Otherwise it starts collecting data from SampleDB
        and never ends in automation"""

        hcon = QuantcastConfig()
        hcon.action_taken['Urls Queued']='100'

        hcon.rules_matched['(Salience=000000) Queue Quantcast Uncat URL']='100'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('QuantcastUncatURLs/quantcast_tw.txt')

    def a_test_non_resume(self):
        """Test by running it in non resume mode"""
        pass