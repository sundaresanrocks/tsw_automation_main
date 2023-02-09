"""
===================================
Malc0de tests
===================================
"""


from harvesters.harvester import *
from harvesters.harvester_config import HarvesterMalc0de


class Malc0de(SandboxedHarvesterTest):
    default_har_config = HarvesterMalc0de
        
    def test_harvester_Malc0de_02(self):
        """
         rule "(Salience=000099) Append ms to URL with path"
        If url has path then append the category of the url to 'ms'
        """
        tcid = '02'
        hcon = HarvesterMalc0de()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=000099) Append ms to URL with path']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('Malc0de/Hashes-02.txt')
        
    def test_harvester_Malc0de_03(self):
        """
       rule "(Salience=000098) Queue urls with no path"
        If url has no path then queue the url to "TrustedCats_DMS", with priority 8500
        """
        tcid = '03'
        hcon = HarvesterMalc0de()
        hcon.action_taken['Urls Queued']='1'
        hcon.rules_matched['(Salience=000098) Queue urls with no path']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('Malc0de/Hashes-03.txt')
        
    def test_harvester_Malc0de_04(self):
        """
         rule "(Salience=000200) Email URLs on the DMS Sanity list"
        If url is present in DMS Sanity list then email the url to "john_rivera@mcafee.com"
        """
        tcid = '04'
        hcon = HarvesterMalc0de()
        hcon.action_taken['Urls Emailed to Web Analysts']='1'
        hcon.rules_matched['(Salience=000200) Email URLs on the DMS Sanity list']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('Malc0de/Hashes-04.txt')