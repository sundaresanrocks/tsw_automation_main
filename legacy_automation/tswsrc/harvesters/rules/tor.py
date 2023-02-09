from harvesters.harvester_config import TORConfig

__author__ = 'Anurag'

from harvesters.harvester import *


class TORFunc(SandboxedTest):


    def test_resume_mode(self):
        """Run it only in Resume mode.
        Otherwise it starts collecting data from SampleDB
        and never ends in automation"""

        hcon = TORConfig()
        hcon.action_taken['Urls with Categories Appended']='3'
        hcon.action_taken['Urls Ignored']='1'

        hcon.rules_matched['(Salience=009999) Skip URL that matches sanity check list']='1'
        hcon.rules_matched['(Salience=000000) Import everything as an']='3'

        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('TOR/tor_01.txt')

    def a_test_non_resume(self):
        """Test by running it in non resume mode"""
        pass