from harvesters.harvester_config import NetcraftConfig

__author__ = 'Anurag'
from harvesters.harvester import *


class NetcraftFunc(SandboxedTest):


    def test_resume_mode(self):
        """Run it only in Resume mode.
        Otherwise it starts collecting data from SampleDB
        and never ends in automation"""

        hcon = NetcraftConfig()
        hcon.action_taken['Urls Queued']='5'

        hcon.rules_matched['(Salience=000920) Queue URL with no path']='5'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('Netcraft/nc_01.txt')

    def a_test_non_resume(self):
        """Test by running it in non resume mode"""
        pass