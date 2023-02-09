"""
===================================
FaceBookBlackList tests
===================================
"""
from harvesters.harvester import *
from harvesters.harvester_config import HarvesterFaceBookBlackList


class FacebookBlacklist(SandboxedHarvesterTest):
    default_har_config = HarvesterFaceBookBlackList
    testprefix = 'test'

    def test_harvester_FacebookBlacklist_01(self):
        """
        rule "(Salience=000100) Append ms to URL status BAD"
	
        """


        hcon = HarvesterFaceBookBlackList()
        hcon.rules_matched['(Salience=000100) Append ms to URL status BAD'] = '1'
        hcon.action_taken['Urls with Categories Appended'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('FacebookBlacklist/01.txt', hcon.action_taken, hcon.rules_matched)


    def test_harvester_FacebookBlacklist_02(self):
        """
        rule "(Salience=000700) Remove ms from URL status NONE"

        """


        hcon = HarvesterFaceBookBlackList()
        hcon.rules_matched['(Salience=000700) Remove ms from URL status NONE'] = '1'
        hcon.action_taken['Urls with Categories Removed'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('FacebookBlacklist/02.txt', hcon.action_taken, hcon.rules_matched)


    def test_harvester_FacebookBlacklist_03(self):
        """
       rule "(Salience=000000) Default Rule to queue"
	
        """


        hcon = HarvesterFaceBookBlackList()
        hcon.rules_matched['(Salience=000000) Default Rule to queue'] = '1'
        hcon.action_taken['Urls Queued'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('FacebookBlacklist/03.txt', hcon.action_taken, hcon.rules_matched)

    def test_harvester_FacebookBlacklist_04(self):
        """
       rule "(Salience=000300) Queue https URL"
	
        """


        hcon = HarvesterFaceBookBlackList()
        hcon.rules_matched['(Salience=000300) Queue https URL'] = '1'
        hcon.action_taken['Urls Queued'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('FacebookBlacklist/04.txt', hcon.action_taken, hcon.rules_matched)

    def test_harvester_FacebookBlacklist_05(self):
        """
       rule "(Salience=000400) Queue trusted cats"
	
        """


        hcon = HarvesterFaceBookBlackList()
        hcon.rules_matched['(Salience=000400) Queue trusted cats'] = '1'
        hcon.action_taken['Urls Queued'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('FacebookBlacklist/05.txt', hcon.action_taken, hcon.rules_matched)

    def test_harvester_FacebookBlacklist_06(self):
        """
        rule "(Salience=000500) Skip urls that match Sanity Check List"
	
        """


        hcon = HarvesterFaceBookBlackList()
        hcon.rules_matched['(Salience=000500) Skip urls that match Sanity Check List'] = '1'
        hcon.action_taken['Urls Ignored'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('FacebookBlacklist/06.txt', hcon.action_taken, hcon.rules_matched)


    def test_harvester_FacebookBlacklist_07(self):
        """
    rule "(Salience=000600) Skip urls that are already Malicious"
	
        """


        hcon = HarvesterFaceBookBlackList()
        hcon.rules_matched['(Salience=000600) Skip urls that are already Malicious'] = '1'
        hcon.action_taken['Urls Ignored'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('FacebookBlacklist/07.txt', hcon.action_taken, hcon.rules_matched)


    def test_harvester_FacebookBlacklist_08(self):
        """
        rule "(Salience=000159) Skip invalid .COM urls"
	
        """


        hcon = HarvesterFaceBookBlackList()
        hcon.rules_matched['(Salience=000800) Skip invalid .COM urls'] = '1'
        hcon.action_taken['Urls Ignored'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('FacebookBlacklist/08.txt', hcon.action_taken, hcon.rules_matched)



        #tcid = '01'
        #hcon = HarvesterFaceBookBlackList()
        #hcon.action_taken['Urls Queued']='1'
        #hcon.rules_matched['']='1'
        #hobj = Harvester(hcon,"partial")
        #hobj.test_harvester_base('FacebookBlacklist/01.txt')

#class FacebookBlacklist(SandboxedHarvesterTest):
#    default_har_config = HarvesterFaceBookBlackList
#    def test_harvester_FacebookBlacklist_01(self):
#        """
        
#        """
#        tcid = '02'
#        hcon = HarvesterFaceBookBlackList()
#        hcon.action_taken['Urls Queued']='1'
#        hcon.rules_matched['']='1'
#        hobj = Harvester(hcon,"partial")
#        hobj.test_harvester_base('FacebookBlacklist/02.txt')
