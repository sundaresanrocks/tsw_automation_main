from harvesters.harvester_config import SURBLABConfig

__author__ = 'Anurag'

from harvesters.harvester import *


class SURBLABFunc(SandboxedTest):

    @classmethod
    def setUpClass(cls):
        cls.hcon = SURBLABConfig()
        cls.host = 'localhost'
        cls.user = 'toolguy'

    def test_resume_mode(self):
        """Run it only in Resume mode.
        Otherwise it starts collecting data from SampleDB
        and never ends in automation"""
        hcon = SURBLABConfig()
        hcon.action_taken['Urls Queued']='2'
        hcon.action_taken['Urls Ignored']='98'

        hcon.rules_matched['(Salience=000550) Skip urls that are already Spam']='90'
        hcon.rules_matched['(Salience=000600) Skip urls that are already Malicious']='8'
        hcon.rules_matched['(Salience=000500) Queue url - trusted categories']='2'

        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('surb/surblab_01.txt')


    def a_test_non_resume(self):
        """Harvester picks data from sample DB."""
        #TODO: Need to figure out how to end this harvester in automation.
        #It runs for more than 1 hour with the data it has.
        pass


#TODO : Implement it for same set of harvesters
# [SURBLWS SURBLSC SURBLPH SURBLMW SURBLJP SURBLAB]
