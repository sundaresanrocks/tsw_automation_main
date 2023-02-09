"""
===================================
MRTUF tests
===================================
"""
#from tswauto.harvesters.harvester import *
from harvesters.harvester import *
from harvesters.harvester_config import HarvesterMRTUF


class MRTUF(SandboxedHarvesterTest):
    default_har_config = HarvesterMRTUF
    def test_harvester_MRTUF_02(self):
        """
        
        """
        tcid = '02'
        hcon = HarvesterMRTUF()
        hcon.action_taken['Urls Queued']='1'
        hcon.rules_matched['(Salience=009998) Queue harvester source is RaidenParsed URLs']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('MRTUF/Hashes-02.txt')
    
    def test_harvester_MRTUF_03(self):
        """
        
        """
        tcid = '03'
        hcon = HarvesterMRTUF()
        hcon.action_taken['Urls Ignored']='1'
        hcon.rules_matched['(Salience=009997) Skip harvester source is RaidenContacted']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('MRTUF/Hashes-03.txt')
    
    def test_harvester_MRTUF_04(self):
        """
        
        """
        tcid = '04'
        hcon = HarvesterMRTUF()
        hcon.action_taken['Urls Ignored']='1'
        hcon.rules_matched['(Salience=009999) Skip content classification type that are clean']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('MRTUF/Hashes-04.txt')
        
    def test_harvester_MRTUF_05(self):
        """
        
        """
        tcid = '05'
        hcon = HarvesterMRTUF()
        hcon.action_taken['Urls to flat log file']='1'
        hcon.action_taken['Urls Emailed to Web Analysts']='1'
        hcon.rules_matched['(Salience=004995) Send the url to the SFOH crawler']='2'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('MRTUF/Hashes-05.txt')
        
    def test_harvester_MRTUF_06(self):
        """
        
        """
        tcid = '06'
        hcon = HarvesterMRTUF()
        hcon.action_taken['Urls Ignored']='1'
        hcon.rules_matched['(Salience=009995) Skip content classification type assumed_dirty']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('MRTUF/Hashes-06.txt')
        
    def test_harvester_MRTUF_07(self):
        """
        
        """
        tcid = '07'
        hcon = HarvesterMRTUF()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=004997) SampleDB - content is assumed_dirty2']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('MRTUF/Hashes-07.txt')
        
    def test_harvester_MRTUF_08(self):
        """
        
        """
        tcid = '08'
        hcon = HarvesterMRTUF()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=004999) SampleDB - content is assumed_dirty4']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('MRTUF/Hashes-08.txt')
        
    def test_harvester_MRTUF_09(self):
        """
        
        """
        tcid = '09'
        hcon = HarvesterMRTUF()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=005002) SampleDB - content is VIRUS']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('MRTUF/Hashes-09.txt')
        
    def test_harvester_MRTUF_10(self):
        """
        
        """
        tcid = '10'
        hcon = HarvesterMRTUF()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=005000) SampleDB - content is TROJAN']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('MRTUF/Hashes-10.txt')
        
    def test_harvester_MRTUF_11(self):
        """
        
        """
        tcid = '11'
        hcon = HarvesterMRTUF()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=004997) SampleDB - content is PUP - with fishy extension']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('MRTUF/Hashes-11.txt')
        
    def test_harvester_MRTUF_12(self):
        """
        
        """
        tcid = '12'
        hcon = HarvesterMRTUF()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=005001) SampleDB - content is JS Wonka']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('MRTUF/Hashes-12.txt')
        
    def test_harvester_MRTUF_13(self):
        """
        
        """
        tcid = '13'
        hcon = HarvesterMRTUF()
        hcon.action_taken['Urls Ignored']='1'
        hcon.rules_matched['(Salience=009996) Skip content classification type Unknown']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('MRTUF/Hashes-13.txt')
        
    def test_harvester_MRTUF_14(self):
        """
        
        """
        tcid = '14'
        hcon = HarvesterMRTUF()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=004998) SampleDB - content is assumed_dirty3']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('MRTUF/Hashes-14.txt')
