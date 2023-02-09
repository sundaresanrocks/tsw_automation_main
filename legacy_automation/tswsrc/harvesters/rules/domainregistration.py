"""
===================================
DomainRegistration tests
===================================
"""


from harvesters.harvester import *
from harvesters.harvester_config import HarvesterDomainRegistration


class DomainRegistrationTests(SandboxedHarvesterTest):
    default_har_config = HarvesterDomainRegistration
    
    def test_domain_registration_01(self):
        """
            TS-884:Check rule "(Salience=000300) Skip urls already Malicious
        """
        tcid = 'DomainRegistration_Salience_000300_Skip_urls_already_Malicious.txt'
        hcon = HarvesterDomainRegistration()
        hcon.action_taken['Urls Ignored']='2'
        hcon.rules_matched['(Salience=000300) Skip urls already Malicious']='2'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('DomainRegistration/%s'%tcid)
        
        
    def test_domain_registration_02(self):
        """
            TS-885:Check rule ""(Salience=000250) Skip urls that match the DMS Sanity Check"".
        """
        tcid = 'DomainRegistration_Salience_000250_Skip_urls_that_match_the_DMS_Sanity_Check.txt'
        hcon = HarvesterDomainRegistration()
        hcon.action_taken['Urls Ignored']='2'
        hcon.rules_matched['(Salience=000250) Skip urls that match the DMS Sanity Check']='2'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('DomainRegistration/%s'%tcid)
        
        
    def test_domain_registration_03(self):
        """
            TS-886:Check rule "(Salience=000200) Email urls already rated Spam".
        """
        tcid = 'DomainRegistration_Salience_000200_Email_urls_already_rated_Spam.txt'
        hcon = HarvesterDomainRegistration()
        hcon.action_taken['Urls Ignored']='2'
        hcon.rules_matched['(Salience=000200) Skip urls already rated Spam']='2'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('DomainRegistration/%s'%tcid)
        
        
    def test_domain_registration_04(self):
        """
            TS-887:Check rule "(Salience=000150) New register domain has IP Spam Reputation 100 percent red yellow".
        """
        tcid = 'DomainRegistration_Salience_000150_New_register_domain_has_IP_Spam_Reputation_100_percent_red_yellow.txt'
        hcon = HarvesterDomainRegistration()
        hcon.action_taken['Urls with Categories Appended']='2'
        hcon.rules_matched['(Salience=000150) New register domain has IP Spam Reputation 100 percent red yellow']='2'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('DomainRegistration/%s'%tcid)
        
        
    def test_domain_registration_05(self):
        """
            TS-888:Check rule "(Salience=000125) New domain on spam IPs hosted with other questionable domains".
        """
        tcid = 'DomainRegistration_Salience_00125_New_domain_on_spam_IPs_hosted_with_other_questionable_domains.txt'
        hcon = HarvesterDomainRegistration()
        hcon.action_taken['Urls with Categories Appended']='2'
        hcon.rules_matched['(Salience=000125) New domain on spam IPs hosted with other questionable domains']='2'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('DomainRegistration/%s'%tcid)
        
    
    def test_domain_registration_06(self):
        """
            TS-889:Check rule "(Salience=000000) Default rule to skip URL".
        """
        tcid = 'DomainRegistration_Salience_000000_Default_rule_to_skip_URL.txt'
        hcon = HarvesterDomainRegistration()
        hcon.action_taken['Urls Ignored']='2'
        hcon.rules_matched['(Salience=000000) Default rule to skip URL']='2'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('DomainRegistration/%s'%tcid)
        
        
    