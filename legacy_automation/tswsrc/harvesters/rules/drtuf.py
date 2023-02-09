"""
===================================
DRTUF tests
===================================
"""


from harvesters.harvester import *
from harvesters.harvester_config import HarvesterDRTUF


class DRTUF(SandboxedHarvesterTest):
    default_har_config = HarvesterDRTUF
    def test_harvester_DRTUF_01(self):
        """
        
        """
        tcid = '01'
        hcon = HarvesterDRTUF()
        hcon.action_taken['Urls Queued']='1'
        hcon.rules_matched['(Salience=000000) Default rule is to queue url']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('DRTUF/drtuf_alligator_test_case_Salience_000000.txt')
        
    def test_harvester_DRTUF_02(self):
        """
        
        """
        tcid = '02'
        hcon = HarvesterDRTUF()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=000400) Append dl to url with high Confidence score']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('DRTUF/drtuf_alligator_test_case_Salience=000400_Append_dl_to_url_with_high_Confidence_score.txt')
        
    def test_harvester_DRTUF_03(self):
        """
        
        """
        tcid = '03'
        hcon = HarvesterDRTUF()
        hcon.action_taken['Urls Queued']='1'
        hcon.rules_matched['(Salience=000450) Queue url that is already categorized as hw']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('DRTUF/drtuf_alligator_test_case_Salience_000450_Queue_url_that_is_already_categorized_as_hw.txt')
        
    def test_harvester_DRTUF_04(self):
        """
        
        """
        tcid = '04'
        hcon = HarvesterDRTUF()
        hcon.action_taken['Urls Ignored']='1'
        hcon.rules_matched['(Salience=000600) Skip url that is already categorized as dl or ms in TSWDB']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('DRTUF/drtuf_alligator_test_case_Salience_000500_Skip_url_that_is_already_categorized_as_dl_or_ms.txt')