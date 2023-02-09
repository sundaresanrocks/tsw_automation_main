"""
===================================
SFOH_Social Media Harvester tests
Dev Contact - Pramod Mundhra <Pramod_Mundhra@McAfee.com>
QA Contact  - Vemuri, Anurag <Anurag_Vemuri@McAfee.com>
===================================
"""
from harvesters.harvester_config import HarvesterSFOHSocialMedia

__author__ = 'Anurag'

from harvesters.harvester import *
import logging


class SFOH_SocialMedia(SandboxedHarvesterTest):
    """
    Harvester Tests
    """
    default_har_config = HarvesterSFOHSocialMedia


    def test_01(self):
        """
        Test Link id -
        Test for Accurate Rule Triggers
        """
        tcid = '01'
        hcon = HarvesterSFOHSocialMedia()
        hcon.rules_matched['(Salience=001021) Skip HTTPS urls']= '1'
        hcon.rules_matched['(Salience=001020) Skip uncategorized SeedUrls']= '1'
        hcon.rules_matched['(Salience=001019) Skip 1 or 2 letter SeedURLs'] = '1'
        hcon.rules_matched['(Salience=001013) Skip seed urls that have security categories ms,dl,ap,be,cc,cp,cs,hk,pu,ph,su,sy,pd,il'] = '1'
        hcon.rules_matched['(Salience=000060) Skip Query Strings'] = '1'
        hcon.rules_matched['(Salience=000051) Skip URLs with No Path'] = '1'
        hcon.rules_matched['(Salience=000050) Skip None Social Media URLs'] = '1'
        hcon.rules_matched['(Salience=000049) Skip common paths'] = '2'
        hcon.rules_matched['(Salience=000027) Skip Youtube Mobile Rule'] = '1'
        hcon.rules_matched['(Salience=000003) Youtube - Categorize URL based on SeedUrl categories'] = '2'
        hcon.rules_matched['(Salience=000002) Linkedin - Categorize URL based on SeedUrl categories'] = '2'
        hcon.rules_matched['(Salience=000001) Facebook - Categorize URL based on SeedUrl categories'] = '2'
        hcon.rules_matched['(Salience=000000) Twitter - Categorize URL based on SeedUrl categories'] = '2'




        hcon.action_taken['Urls Ignored'] = '10'
        hcon.action_taken['Urls with Categories Appended'] = '8'
        hobj = Harvester(hcon,match_type='half')
        hobj.test_harvester_base('SFOHSocialMedia/test01.txt', hcon.action_taken, hcon.rules_matched)

    def test_02(self):
        """
        Test Link id -
        WWW Test-URls with WWW in path
        """
        tcid = '02'
        hcon = HarvesterSFOHSocialMedia()
        hcon.rules_matched['(Salience=001021) Skip HTTPS urls']= '1'
        hcon.rules_matched['(Salience=001020) Skip uncategorized SeedUrls']= '1'
        hcon.rules_matched['(Salience=001019) Skip 1 or 2 letter SeedURLs'] = '1'
        hcon.rules_matched['(Salience=001013) Skip seed urls that have security categories ms,dl,ap,be,cc,cp,cs,hk,pu,ph,su,sy,pd,il'] = '1'
        hcon.rules_matched['(Salience=000060) Skip Query Strings'] = '1'
        hcon.rules_matched['(Salience=000051) Skip URLs with No Path'] = '1'
        hcon.rules_matched['(Salience=000050) Skip None Social Media URLs'] = '1'
        hcon.rules_matched['(Salience=000049) Skip common paths'] = '2'
        hcon.rules_matched['(Salience=000027) Skip Youtube Mobile Rule'] = '1'
        hcon.rules_matched['(Salience=000003) Youtube - Categorize URL based on SeedUrl categories'] = '2'
        hcon.rules_matched['(Salience=000002) Linkedin - Categorize URL based on SeedUrl categories'] = '2'
        hcon.rules_matched['(Salience=000001) Facebook - Categorize URL based on SeedUrl categories'] = '2'
        hcon.rules_matched['(Salience=000000) Twitter - Categorize URL based on SeedUrl categories'] = '2'

        hcon.action_taken['Urls Ignored'] = '10'
        hcon.action_taken['Urls with Categories Appended'] = '8'
        hobj = Harvester(hcon,match_type='half')
        hobj.test_harvester_base('SFOHSocialMedia/test02.txt', hcon.action_taken, hcon.rules_matched)

    def test_03(self):
        """
        Test Link id -
        WWW Test-IP address as SeedUrl should return proper categories
        Bug 901589 - Will not be fixed
        """
        tcid = '03'
        hcon = HarvesterSFOHSocialMedia()
        hcon.rules_matched['(Salience=000002) Linkedin - Categorize URL based on SeedUrl categories'] = '2'
        hcon.action_taken['Urls with Categories Appended'] = '2'
        logging.error('BUG 901589 raised and will not be fixed')
        hobj = Harvester(hcon,match_type='half')
        hobj.test_harvester_base('SFOHSocialMedia/test03.txt', hcon.action_taken, hcon.rules_matched)
