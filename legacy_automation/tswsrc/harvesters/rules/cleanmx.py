"""
===================================
CleanMx tests
===================================
Harvester related test cases for 
1. CleanMxVirus
2. CleanMxPortal
"""


from harvesters.harvester import *
from harvesters.harvester_config import HarvesterConfig, CMXVirusConfig


class CMXPortalConfig(HarvesterConfig):
    harvester_name = 'CleanMxPortal'
    session_owner = 'CleanMxPortal'
    properties_file = HarvesterConfig.base_conf + 'cleanmxportal.properties'
    working_dir = HarvesterConfig.base_working + 'CleanMxPortal/working/'
    processed_files = HarvesterConfig.base_working + 'CleanMxPortal/processedFiles.txt'
    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            "(Salience=000102) Crawl url":'0',
            "(Salience=000101) Skip url if virusname is DefacedSite or Unknown":'0',
            "(Salience=000300) Skip url that is already categorized as malicious":'0',
            "(Salience=000200) Skip url that matches Sanity Check List":'0',
            "(Salience=000100) Skip Categorized url with No Path":'0',
            "(Salience=000000) Default rule is to queue url":'0'
            }


class Portal(SandboxedHarvesterTest):
    default_har_config = CMXPortalConfig

    def test_01(self):
        """TS-1164:CleanMxPortal: Verify the rule: Skip url that is already categorized as malicious
        (Salience=000300) Skip url that is already categorized as malicious
        """
        hcon = CMXPortalConfig()
        hcon.action_taken['Urls Ignored']='1'
        hcon.rules_matched['(Salience=000300) Skip url that is already categorized as malicious']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('CleanMxPortal/300.txt')

    def test_02(self):
        """TS-1165:CleanMxPortal: Verify the rule: Skip url that matches Sanity Check List
        (Salience=000200) Skip url that matches Sanity Check List
        """
        hcon = CMXPortalConfig()
        hcon.action_taken['Urls Ignored']='1'
        hcon.action_taken['Urls Emailed to Web Analysts']='1'
        hcon.rules_matched['(Salience=000200) Skip url that matches Sanity Check List']='2'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('CleanMxPortal/200.txt')

    def test_03(self):
        """TS-1166:CleanMxPortal: Verify the rules: 1. Crawl url, 2. Skip url if virusname is DefacedSite or Unknown
        (Salience=000102) Crawl url
        (Salience=000101) Skip url if virusname is DefacedSite or Unknown
        """
        hcon = CMXPortalConfig()
        hcon.action_taken['Urls to flat log file']='1'
        hcon.action_taken['Urls Ignored']='1'
        hcon.rules_matched['(Salience=000101) Skip url if virusname is DefacedSite or Unknown']='1'
        hcon.rules_matched['(Salience=000102) Crawl url']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('CleanMxPortal/102-101.txt')

    def test_04(self):
        """TS-1167:CleanMxPortal: Verify the rules: 1. Crawl url, 2. Default rule is to queue url
        (Salience=000102) Crawl url
        (Salience=000000) Default rule is to queue url
        """
        hcon = CMXPortalConfig()
        hcon.action_taken['Urls to flat log file']='1'
        hcon.action_taken['Urls Queued']='1'
        hcon.rules_matched['(Salience=000102) Crawl url']='1'
        hcon.rules_matched['(Salience=000000) Default rule is to queue url']='1'
        
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('CleanMxPortal/102-000.txt')


class Virus(SandboxedHarvesterTest):
    default_har_config = CMXVirusConfig
    def test_01(self):
        """TS-255:Testing data Processing of Cleanmx-virus Harvester
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls Ignored']='1'
        hcon.rules_matched['(Salience=000700) Skip url that is already malicious']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('CleanMxVirus/700.txt')

    def test_02(self):
        """TS-256:Verify the Rule :Skip url that is already malicious
        (Salience=000700) Skip url that is already malicious
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls Ignored']='1'
        hcon.rules_matched['(Salience=000700) Skip url that is already malicious']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('CleanMxVirus/700a.txt')

    def test_03(self):
        """TS-257:Verify the Rule :Crawl url - trusted categories(To be verified)
        (Salience=000601) Crawl url - trusted categories
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls Queued']='5'
        hcon.rules_matched['(Salience=000600) Queue url - trusted categories']='5'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('CleanMxVirus/600.txt')

    def test_04(self):
        """TS-258:Verify the Rule : Queue url - trusted categories
        (Salience=000600) Queue url - trusted categories
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls Queued']='5'
        hcon.rules_matched['(Salience=000600) Queue url - trusted categories']='5'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('CleanMxVirus/600.txt')

    def test_05(self):
        """TS-259:Verify the Rule :Queue url - low vtscore
        (Salience=000500) Queue url - low vtscore
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls Queued']='1'
        hcon.rules_matched['(Salience=000500) Queue url - low vtscore']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('CleanMxVirus/500.txt')

    def test_06(self):
        """TS-259:Verify the Rule :Queue url - low vtscore
        (Salience=000400) Queue url - scanner is undef
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls Queued']='1'
        hcon.rules_matched['(Salience=000400) Queue url - scanner is undef']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('CleanMxVirus/400.txt')

    def test_07(self):
        """TS-261:Verify the Rule :Queue url - virusname is unknown
        (Salience=000300) Queue url - virusname is unknown
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls Queued']='1'
        hcon.rules_matched['(Salience=000300) Queue url - virusname is unknown']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('CleanMxVirus/300.txt')

    def test_08(self):
        """TS-262:Verify the Rule : Queue url - no path
        (Salience=000200) Queue url - no path
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls Queued']='1'
        hcon.rules_matched['(Salience=000200) Queue url - no path']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('CleanMxVirus/200.txt')

    def test_09(self):
        """TS-263:Verify the Rule :Append ms to url
        (Salience=000100) Append ms to url
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=000100) Append ms to url']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('CleanMxVirus/100.txt')

    def test_10(self):
        """TS-264:Verify the Rule :Queue url
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls Queued']='1'
        hcon.rules_matched['(Salience=000000) Queue url']='1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('CleanMxVirus/000.txt')

    def test_11(self):
        """verify the Rule: Skip urls in the DMS sanity list
        (Salience=000999) Skip urls in the DMS sanity list
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls Ignored']='1'
        hcon.rules_matched['(Salience=000999) Skip urls in the DMS sanity list']='1'
        hobj = Harvester(hcon, 'partial')
        hobj.test_harvester_base('CleanMxVirus/999.txt')

    def test_12(self):
        """Verify the Rule: scanner is Sophos -Append dl
        (Salience=000515)  scanner is Sophos -Append dl
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=000515)  scanner is Sophos -Append dl']='1'
        hobj = Harvester(hcon, 'partial')
        hobj.test_harvester_base('CleanMxVirus/515.txt')

    def test_13(self):
        """verify the Rule: scanner is Kaspersky -Append dl
        (Salience=000514)  scanner is Kaspersky -Append dl
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=000514)  scanner is Kaspersky -Append dl']='1'
        hobj = Harvester(hcon, 'partial')
        hobj.test_harvester_base('CleanMxVirus/514.txt')

    def test_14(self):
        """Verify the Rule: scanner is Avast -Append dl
        (Salience=000513)  scanner is Avast -Append dl
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=000513)  scanner is Avast -Append dl']='1'
        hobj = Harvester(hcon, 'partial')
        hobj.test_harvester_base('CleanMxVirus/513.txt')

    def test_15(self):
        """Verify the Rule: scanner is AVG -Append dl
        (Salience=000512)  scanner is AVG -Append dl
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=000512)  scanner is AVG -Append dl']='1'
        hobj = Harvester(hcon, 'partial')
        hobj.test_harvester_base('CleanMxVirus/512.txt')

    def test_16(self):
        """Verify the Rule: scanner is TrendMicro -Append dl
        (Salience=000511)  scanner is TrendMicro -Append dl
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=000511)  scanner is TrendMicro -Append dl']='1'
        hobj = Harvester(hcon, 'partial')
        hobj.test_harvester_base('CleanMxVirus/511.txt')

    def test_17(self):
        """Verify the Rule: scanner is BitDefender -Append dl
        (Salience=000510)  scanner is BitDefender -Append dl
        """
        hcon = CMXVirusConfig()
        hcon.action_taken['Urls with Categories Appended']='1'
        hcon.rules_matched['(Salience=000510)  scanner is BitDefender -Append dl']='1'
        hobj = Harvester(hcon, 'partial')
        hobj.test_harvester_base('CleanMxVirus/510.txt')
