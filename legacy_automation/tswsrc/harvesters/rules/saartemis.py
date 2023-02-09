from harvesters.harvester_config import SAArtemisConfig

__author__ = 'Anurag'
from harvesters.harvester import *


class SAArtemisFunc(SandboxedTest):

    @classmethod
    def setUpClass(cls):
        cls.hcon = SAArtemisConfig()
        cls.host = 'localhost'
        cls.user = 'toolguy'

    def test_resume_mode(self):
        """Run it only in Resume mode.
        Otherwise it starts collecting data from SampleDB
        and never ends in automation"""
        hcon = SAArtemisConfig()
        hcon.action_taken['Urls Queued']='1'
        hcon.action_taken['Urls Ignored']='1'
        hcon.action_taken['Urls Emailed to Web Analysts']='1'
        hcon.action_taken['Urls to flat log file']='1'
        hcon.action_taken['Urls with Categories Appended'] ='7'

        hcon.rules_matched['(Salience=004997) SampleDB - content is PUP - with fishy extension']='1'
        hcon.rules_matched['(Salience=004995) Send the url to the SFOH crawler']='2'
        hcon.rules_matched['(Salience=005000) SampleDB - content is TROJAN']='6'
        hcon.rules_matched['(Salience=010004) Queue urls that match Sanity Check List']='1'
        hcon.rules_matched['(Salience=009999) Skip content classification type that are clean']='1'

        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('SAArtemis/saartemis_01.txt')


    def a_test_non_resume(self):
        """Harvester picks data from sample DB."""
        #TODO: Need to figure out how to end this harvester in automation.
        #It runs for more than 1 hour with the data it has.
        pass

