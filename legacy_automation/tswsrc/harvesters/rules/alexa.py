from harvesters.harvester_config import AlexaConfig

__author__ = 'Anurag'
from harvesters.harvester import *


class AlexaFunc(SandboxedTest):


    def test_resume_mode(self):
        """Run it only in Resume mode.
        Otherwise it starts collecting data from SampleDB
        and never ends in automation"""

        hcon = AlexaConfig()
        hcon.action_taken['Urls Queued']='100'

        hcon.rules_matched['(Salience=000000) Queue Alexa Uncat URL']='100'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('AlexaUncatURLs/alexa_01.txt')

    def a_test_non_resume(self):
        """Test by running it in non resume mode"""
        pass