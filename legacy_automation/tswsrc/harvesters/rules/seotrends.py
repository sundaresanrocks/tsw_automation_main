from harvesters.harvester_config import SEOTrendsConfig

__author__ = 'Anurag'
from harvesters.harvester import *


class SEOTrendsFunc(SandboxedTest):


    def test_resume_mode(self):
        """Run it only in Resume mode.
        Otherwise it starts collecting data from SampleDB
        and never ends in automation"""

        hcon = SEOTrendsConfig()
        hcon.action_taken['Urls to flat log file']='1'

        hcon.rules_matched['(Salience=000001) Crawl url']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('SEOTrends/seot_01.txt')

    def a_test_non_resume(self):
        """Test by running it in non resume mode"""
        pass