__author__ = 'Anurag'
from harvesters.harvester import *


class HarvesterSFOHSocialMedia(HarvesterConfig):
    """
    Harvester Base rules
    """
    harvester_name = 'SFOH_SocialMedia'
    session_owner = 'SFOH_SocialMedia'
    properties_file = HarvesterConfig.base_conf + 'sfoh_socialmedia.properties'
    working_dir = HarvesterConfig.base_working + 'SFOH_SocialMedia/working/'
    processed_files = HarvesterConfig.base_working + 'SFOH_SocialMedia/processedFiles.txt'
    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched =  {
                    '(Salience=000000) Twitter - Categorize URL based on SeedUrl categories': '0',
                    '(Salience=000001) Facebook - Categorize URL based on SeedUrl categories': '0',
                    '(Salience=000002) Linkedin - Categorize URL based on SeedUrl categories': '0',
                    '(Salience=000003) Youtube - Categorize URL based on SeedUrl categories': '0',
                    '(Salience=000049) Skip common paths': '0',
                    '(Salience=000050) Skip None Social Media URLs': '0',
                    '(Salience=000051) Skip URLs with No Path': '0',
                    '(Salience=000027) Skip Youtube Mobile Rule': '0',
                    '(Salience=000060) Skip Query Strings': '0',
                    '(Salience=000065) Skip Embedded URLs': '0',
                    '(Salience=000075) Skip Ads Rule': '0',
                    '(Salience=001020) Skip uncategorized SeedUrls': '0',
                    '(Salience=001019) Skip 1 or 2 letter SeedURLs': '0',
                    '(Salience=001013) Skip seed urls that have security categories ms,dl,ap,be,cc,cp,cs,hk,pu,ph,su,sy,pd,il': '0',
                    '(Salience=001021) Skip HTTPS urls': '0'
                               }


class SFOH(SandboxedHarvesterTest):
    """
    Harvester Tests
    """
    default_har_config = HarvesterSFOHSocialMedia


    def test_sfoh_01(self):
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