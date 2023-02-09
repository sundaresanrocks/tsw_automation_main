import runtime
from path import Path
__author__ = 'manoj'


class HarvesterConfig:
    """ Base harvester config for all harvesters"""
    bin = runtime.SH.harvester
    log_file_name = runtime.LOG.harvester
    base_conf = Path('/opt/sftools/conf/')
    base_working = Path('/usr2/smartfilter/import/harvest_processor/data/')
    base_mapr = Path('/data/mapr/data/tsweb/harvesters/')
    base_src = Path('/data/harvesters/')
    base_source = Path(runtime.data_path + '/tsw/harvesters/')
    src_dir = Path('/data/harvesters/')

    def __init__(self):
        self.action_taken = {'Urls Queued for DWA': '0',
                             'Urls to flat log file': '0',
                             'Urls Ignored': '0',
                             'Urls with Categories Inserted': '0',
                             'Urls Emailed to Web Analysts': '0',
                             'Urls with Categories Removed': '0',
                             'Urls with Categories Appended': '0',
                             'Urls Queued': '0'}

        self.rules_matched = {'(Salience=000000) Default rule': '0',
                              '(Salience=000100) Url matches test': '0',
                              '(Salience=000200) Url does not match test': '0',
                              '(Salience=000300) Domain matches test': '0'}


class AlexaConfig(HarvesterConfig):
    harvester_name = 'AlexaUncatURLs'
    session_owner = 'AlexaUncatURLs'
    properties_file = HarvesterConfig.base_conf + 'AlexaUncatURLs.properties'
    working_dir = HarvesterConfig.base_working + harvester_name + '/working/'
    mapr_dir = HarvesterConfig.base_mapr + harvester_name + '/'
    src_dir = HarvesterConfig.base_src + harvester_name + '/'
    processed_files = HarvesterConfig.base_working + harvester_name + '/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=000000) Queue Alexa Uncat URL': '0'
        }


class HarvesterAPWG(HarvesterConfig):
    harvester_name = 'APWG'
    session_owner = 'APWG'
    properties_file = "/opt/sftools/conf/APWG.properties"
    working_dir = HarvesterConfig.base_working + 'APWG/working/'
    mapr_dir = HarvesterConfig.base_mapr + harvester_name + '/'
    processed_files = HarvesterConfig.base_working + 'APWG/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=000601) Queue and Email url with fp term - cgi': '0',
            '(Salience=000500) Shorten to target term in path score greater or equal to 50': '0',
            '(Salience=000603) Queue and Email url with fp term - file+cgi': '0',
            '(Salience=000400) Append Ph to url - score equal to 100': '0',
            '(Salience=000600) Queue and Email url with fp term - path': '0',
            '(Salience=000700) Append Ph to url with security cats': '0',
            '(Salience=000800) Queue HTTPS url': '0',
            '(Salience=001100) Remove ph category': '0',
            '(Salience=000300) Queue categorized url with path - score greater or equal to 50': '0',
            '(Salience=000200) Append Ph to url with path - score greater or equal to 50': '0',
            '(Salience=000900) Queue URL with trusted cats': '0',
            '(Salience=000100) Queue url with no path - score greater or equal to 50': '0',
            '(Salience=001000) Skip url that is already Phishing': '0',
            '(Salience=000000) Default rule is to queue url': '0',
            '(Salience=000602) Queue and Email url with fp term - file': '0'
        }


class BitDefenderConfig(HarvesterConfig):
    harvester_name = 'BitDefender'
    session_owner = 'BitDefender'
    properties_file = HarvesterConfig.base_conf + 'BitDefender.properties'
    working_dir = HarvesterConfig.base_working + harvester_name + '/working/'
    mapr_dir = HarvesterConfig.base_mapr + harvester_name + '/'
    src_dir = HarvesterConfig.base_src + harvester_name + '/'
    processed_files = HarvesterConfig.base_working + harvester_name + '/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=000265) Queue and Crawl URL with no path': '0',
            '(Salience=000285) Skip urls that match DMS Sanity Check List': '0',
            '(Salience=000275) Queue and Crawl trusted cats': '0',
            '(Salience=000000) Default Rule is to Queue': '0',
            '(Salience=000255) Append ms to URL': '0',
            '(Salience=000295) Skip urls that are already Malicious': '0'
        }


class CMXVirusConfig(HarvesterConfig):
    harvester_name = 'CleanMxVirus'
    session_owner = 'CleanMxVirus'
    properties_file = HarvesterConfig.base_conf + 'cleanmxvirus.properties'
    working_dir = HarvesterConfig.base_working + 'CleanMxVirus/working/'
    processed_files = HarvesterConfig.base_working + 'CleanMxVirus/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=000400) Queue url - scanner is undef': '0',
            '(Salience=000511)  scanner is TrendMicro -Append dl': '0',
            '(Salience=000700) Skip url that is already malicious': '0',
            '(Salience=000514)  scanner is Kaspersky -Append dl': '0',
            '(Salience=000100) Append ms to url': '0',
            '(Salience=000510)  scanner is BitDefender -Append dl': '0',
            '(Salience=000600) Queue url - trusted categories': '0',
            '(Salience=000000) Queue url': '0',
            '(Salience=000512)  scanner is AVG -Append dl': '0',
            '(Salience=000200) Queue url - no path': '0',
            '(Salience=000500) Queue url - low vtscore': '0',
            '(Salience=000999) Skip urls in the DMS sanity list': '0',
            '(Salience=000300) Queue url - virusname is unknown': '0',
            '(Salience=000513)  scanner is Avast -Append dl': '0',
            '(Salience=000515)  scanner is Sophos -Append dl': '0'
        }


class HarvesterCSirt(HarvesterConfig):
    harvester_name = 'CSirt'
    session_owner = 'CSirt'
    properties_file = HarvesterConfig.base_conf + 'CSirt.properties'
    working_dir = HarvesterConfig.base_working + 'CSirt/working/'
    processed_files = HarvesterConfig.base_working + 'CSirt/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=000000) Default Rule to queue': '0',
            '(Salience=000100) Append ph to URL': '0',
            '(Salience=000300) Queue https with trusted cats': '0',
            '(Salience=000400) Skip urls that are already Malicious': '0',
            '(Salience=000200) Queue rated URL with no path': '0',
        }


class HarvesterDomainRegistration(HarvesterConfig):
    harvester_name = 'DomainRegistration'
    session_owner = 'DomainRegistration'
    properties_file = HarvesterConfig.base_conf + 'DomainRegistration.properties'
    working_dir = HarvesterConfig.base_working + 'DomainRegistration/working'
    processed_files = HarvesterConfig.base_working + 'DomainRegistration/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {'(Salience=000300) Skip urls already Malicious': '0',
                              '(Salience=000250) Skip urls that match the DMS Sanity Check': '0',
                              '(Salience=000200) Skip urls already rated Spam': '0',
                              '(Salience=000150) New register domain has IP Spam Reputation 100 percent red yellow': '0',
                              '(Salience=000125) New domain on spam IPs hosted with other questionable domains': '0',
                              '(Salience=000000) Default rule to skip URL': '0',
        }


class HarvesterDRTUF(HarvesterConfig):
    harvester_name = 'DRTUF'
    session_owner = 'DRTUF'
    properties_file = HarvesterConfig.base_conf + 'drtuf.properties'
    working_dir = HarvesterConfig.base_working + 'DRTUF/working/'
    processed_files = HarvesterConfig.base_working + 'DRTUF/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=000500) Skip url that is already categorized as dl or ms': '0',
            '(Salience=000450) Queue url that is already categorized as hw': '0',
            '(Salience=000600) Skip url that is already categorized as dl or ms in TSWDB': '0',
            '(Salience=000400) Append dl to url with high Confidence score': '0',
            '(Salience=000000) Default rule is to queue url': '0'
        }


class HarvesterFaceBookBlackList(HarvesterConfig):
    harvester_name = 'FaceBookBlackList'
    session_owner = 'FaceBookBlackList'
    properties_file = HarvesterConfig.base_conf + 'FaceBookBlackList.properties'
    working_dir = HarvesterConfig.base_working + 'FaceBookBlackList/working/'
    processed_files = HarvesterConfig.base_working + 'FaceBookBlackList/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=000400) Queue trusted cats': '0',
            '(Salience=000800) Skip invalid .COM urls': '0',
            '(Salience=000000) Default Rule to queue': '0',
            '(Salience=000200) Queue Google Docs URLs': '0',
            '(Salience=000700) Remove ms from URL status NONE': '0',
            '(Salience=000300) Queue https URL': '0',
            '(Salience=000500) Skip urls that match Sanity Check List': '0',
            '(Salience=000600) Skip urls that are already Malicious': '0',
            '(Salience=000100) Append ms to URL status BAD': '0'
        }


class HarvesterMalc0de(HarvesterConfig):
    harvester_name = 'Malc0de'
    session_owner = 'Malc0de'
    properties_file = HarvesterConfig.base_conf + 'malc0de.properties'
    working_dir = HarvesterConfig.base_working + 'Malc0de/working/'
    processed_files = HarvesterConfig.base_working + 'Malc0de/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=000000) Default Rule is to queue': '0',
            '(Salience=000099) Append ms to URL with path': '0',
            '(Salience=000098) Queue urls with no path': '0',
            '(Salience=000200) Email URLs on the DMS Sanity list': '0',
        }


class MalwareDomainListConfig(HarvesterConfig):
    harvester_name = 'MalwareDomainList'
    session_owner = 'MalwareDomainList'
    properties_file = HarvesterConfig.base_conf + 'malware_domain_list.properties'
    working_dir = HarvesterConfig.base_working + harvester_name + '/working/'
    mapr_dir = HarvesterConfig.base_mapr + harvester_name + '/'
    src_dir = HarvesterConfig.base_src + harvester_name + '/'
    processed_files = HarvesterConfig.base_working + harvester_name + '/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=000999) Skip urls in the DMS sanity list': '0',
            '(Salience=000030) Queue IPs with no path': '0',
            '(Salience=000000) Default Rule - Append ms': '0',
            '(Salience=000050) Email potential false positives': '0'
        }


class MalwareUrlsConfig(HarvesterConfig):
    harvester_name = 'MalwareUrls'
    session_owner = 'MalwareUrls'
    properties_file = "/opt/sftools/conf/malwareurls.properties"
    working_dir = HarvesterConfig.base_working + 'MalwareUrls/working/'
    processed_files = HarvesterConfig.base_working + 'MalwareUrls/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=99998) Check for URL with high spam probability': '0',
            '(Salience=15) Queue IP with no path': '0',
            '(Salience=25) Append CP to Scam and Fraud URLs with malware cats': '0',
            '(Salience=24) Queue Scam and Fraud and URLs': '0',
            '(Salience=10) Append ms to IP with path': '0',
            '(Salience=20) Email Money Mule URLs': '0',
            '(Salience=26) Skip URLs that are already dl or ms': '0',
            '(Salience=0) Append ms to URL': '0',
            '(Salience=19) Queue a URL that is cat as FI, FS, FN or GV': '0',
        }


class HarvesterConMobileChildReview(HarvesterConfig):
    harvester_name = 'MaliciousChildReview'
    session_owner = 'MaliciousChildReview'
    properties_file = HarvesterConfig.base_conf + 'MaliciousChildReview.properties'
    working_dir = HarvesterConfig.base_working + 'MaliciousChildReview/working/'
    processed_files = HarvesterConfig.base_working + 'MaliciousChildReview/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=202) Clean up URLs with clean SampleDB results': '0',
            '(Salience=502) Skip URLs from redirects': '0',
            '(Salience=200) Skip URLs with dirty SampleDB results': '0',
            '(Salience=500) Skip URLs modifed in the last 90 days': '0',
            '(Salience=201) Clean up URLs with unknown SampleDB results': '0',
            '(Salience=501) Skip URLs that are not malicious': '0',
            '(Salience=301) Clean up 300 URLs after a year': '0',
            '(Salience=302) Clean up 300 URLs that are domains': '0',
            '(Salience=000) Default Rule': '0',
            '(Salience=403) Clean up 404 URLs after a year': '0',
            '(Salience=404) Clean up 404 domains': '0'
        }
        self.action_taken = {
            'Urls with Categories Inserted': '0',
            'Urls with Categories Appended': '0',
            'Urls with Categories Removed': '0',
            'Urls Queued': '0',
            'Urls Ignored': '0',
            'Urls Emailed to Web Analysts': '0',
            'Urls to flat log file': '0',
            'Urls Queued for DWA': '0',
        }


class HarvesterMRTUF(HarvesterConfig):
    harvester_name = 'MRTUF'
    session_owner = 'MRTUF'
    properties_file = HarvesterConfig.base_conf + 'mrtuf.properties'
    working_dir = HarvesterConfig.base_working + 'MRTUF/working/'
    processed_files = HarvesterConfig.base_working + '/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {   '(Salience=004995) Send the url to the SFOH crawler': '0',
            '(Salience=004997) SampleDB - content is PUP - with fishy extension': '0',
            '(Salience=004997) SampleDB - content is assumed_dirty2': '0',
            '(Salience=004998) SampleDB - content is assumed_dirty3': '0',
            '(Salience=004999) SampleDB - content is assumed_dirty4': '0',
            '(Salience=005000) SampleDB - content is TROJAN': '0',
            '(Salience=005001) SampleDB - content is JS Wonka': '0',
            '(Salience=005002) SampleDB - content is VIRUS': '0',
            '(Salience=009995) Skip content classification type assumed_dirty': '0',
            '(Salience=009996) Skip content classification type Unknown': '0',
            '(Salience=009997) Skip harvester source is RaidenContacted': '0',
            '(Salience=009998) Queue harvester source is RaidenParsed URLs': '0',
            '(Salience=009999) Skip content classification type that are clean': '0',
            '(Salience=010000) Skip urls where the sample type is clean': '0',
            '(Salience=010002) Skip urls rated high risk': '0',
            '(Salience=010003) Queue URLs without path': '0',
            '(Salience=010004) Queue urls that match Sanity Check List': '0',
            '(Salience=010005)  queue trusted cats': '0'
        }


class NetcraftConfig(HarvesterConfig):
    harvester_name = 'Netcraft'
    session_owner = 'Netcraft'
    properties_file = HarvesterConfig.base_conf + 'netcraft.properties'
    working_dir = HarvesterConfig.base_working + harvester_name + '/working/'
    mapr_dir = HarvesterConfig.base_mapr + harvester_name + '/'
    src_dir = HarvesterConfig.base_src + harvester_name + '/'
    processed_files = HarvesterConfig.base_working + harvester_name + '/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=000870) Shorten to wellsfargo bank term path': '0',
            '(Salience=000900) Shorten to bank term ebay in path': '0',
            '(Salience=000930) Queue url with trusted cats': '0',
            '(Salience=000890) Shorten to bank term paypal in path': '0',
            '(Salience=000920) Queue URL with no path': '0',
            '(Salience=000940) Queue HTTPS url': '0',
            '(Salience=000880) Shorten to bank term bankofamerica in path': '0',
            '(Salience=000000) Default rule Append ph to the new url': '0',
            '(Salience=001000) Skip urls that are already phishing': '0',
            '(Salience=001005) Skip unblocks': '0',
            '(Salience=000860) Shorten to bank term hsbc in path': '0'
        }


class QuantcastConfig(HarvesterConfig):
    harvester_name = 'QuantcastUncatURLs'
    session_owner = 'QuantcastUncatURLs'
    properties_file = HarvesterConfig.base_conf + 'QuantcastUncatURLs.properties'
    working_dir = HarvesterConfig.base_working + harvester_name + '/working/'
    mapr_dir = HarvesterConfig.base_mapr + harvester_name + '/'
    src_dir = HarvesterConfig.base_src + harvester_name + '/'
    processed_files = HarvesterConfig.base_working + harvester_name + '/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=000000) Queue Quantcast Uncat URL': '0'
        }


class HarvesterRepper(HarvesterConfig):
    harvester_name = 'Repper'
    session_owner = 'Repper'
    properties_file = HarvesterConfig.base_conf + 'Repper.properties'
    working_dir = HarvesterConfig.base_working + 'Repper/working/'
    processed_files = HarvesterConfig.base_working + 'Repper/processedFiles.txt'


class SAArtemisConfig(HarvesterConfig):
    harvester_name = 'SAArtemis'
    session_owner = 'SAArtemis'
    properties_file = HarvesterConfig.base_conf + 'saartemis.properties'
    working_dir = HarvesterConfig.base_working + harvester_name + '/working/'
    mapr_dir = HarvesterConfig.base_mapr + harvester_name + '/'
    src_dir = HarvesterConfig.base_src + harvester_name + '/'
    processed_files = HarvesterConfig.base_working + harvester_name + '/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=009995) Skip content classification type assumed_dirty': '0',
            '(Salience=010003) Queue URLs without path': '0',
            '(Salience=004997) SampleDB - content is PUP - with fishy extension': '0',
            '(Salience=005001) SampleDB - content is JS Wonka': '0',
            '(Salience=004995) Send the url to the SFOH crawler': '0',
            '(Salience=004999) SampleDB - content is assumed_dirty4': '0',
            '(Salience=005002) SampleDB - content is VIRUS': '0',
            '(Salience=004997) SampleDB - content is assumed_dirty2': '0',
            '(Salience=009997) Skip harvester source is RaidenContacted': '0',
            '(Salience=004998) SampleDB - content is assumed_dirty3': '0',
            '(Salience=009998) Queue harvester source is RaidenParsed URLs': '0',
            '(Salience=010000) Skip urls where the sample type is clean': '0',
            '(Salience=005000) SampleDB - content is TROJAN': '0',
            '(Salience=010004) Queue urls that match Sanity Check List': '0',
            '(Salience=010002) Skip urls rated high risk': '0',
            '(Salience=009999) Skip content classification type that are clean': '0',
            '(Salience=010005)  queue trusted cats': '0',
            '(Salience=009996) Skip content classification type Unknown': '0'
        }


class HarvesterSaaS(HarvesterConfig):
    harvester_name = 'SaaS'
    session_owner = 'SaaS'
    properties_file = HarvesterConfig.base_conf + 'saas.properties'
    working_dir = HarvesterConfig.base_working + 'SaaS/working/'
    processed_files = HarvesterConfig.base_working + 'SaaS/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=099992) McAfee Psyme': '0',
            '(Salience=099979) (WW Webwasher) LooksLike': '0',
            '(Salience=099978) WWMCF': '0',
            '(Salience=100007) MGW Heuristic.BehavesLike.JS.BufferOverflow': '0',
            '(Salience=100003) McAfeeGW Heuristic.BehavesLike.Exploit.CodeExec': '0',
            '(Salience=099983) (WW Webwasher) Virus.Eicar-Test-Signature': '0',
            '(Salience=099988) McAfee Unwanted.Hotbar.gen!80': '0',
            '(Salience=099994) McAfee Phish-BankFraud': '0',
            '(Salience=100002) McAfeeGW Heuristic.BehavesLike.Exploit.Flash.CodeExec': '0',
            '(Salience=000001) Append ms to url with known detection': '0',
            '(Salience=0) Email url with unknown detection': '0',
            '(Salience=000002) Queue url with no path': '0',
            '(Salience=099997) McAfee EICAR test file': '0',
            '(Salience=099993) McAfee Phish-Fraud': '0',
            '(Salience=099995) McAfee New Malware': '0',
            '(Salience=099999) ETrust HTML Phishbank': '0',
            '(Salience=099981) (WW Webwasher) Win32 ImgTagVulnerability': '0',
            '(Salience=100005) MGW Heuristic.BehavesLike.JS.Infected': '0',
            '(Salience=099980) (WW Webwasher) NewMalware': '0',
            '(Salience=999990) Skip url if detection string is 0': '0',
            '(Salience=099989) McAfee Unwanted.MyWebSearch.gen!92': '0',
            '(Salience=099986) Sophos Mal': '0',
            '(Salience=099982) (WW Webwasher) Heuristic': '0',
            '(Salience=100001) McAfeeGW Unwanted.WebSearch.gen': '0',
            '(Salience=099991) McAfee Script.Silly.Gen': '0',
            '(Salience=100006) MGW Heuristic.BehavesLike.JS.Exploit': '0',
            '(Salience=099998) ETrust the EICAR test string': '0',
            '(Salience=099996) McAfee JS-Wonka': '0',
            '(Salience=100008) McAfeeGW Heuristic.BehavesLike.Exploit.PDF.CodeExec': '0',
            '(Salience=099984) (WW Webwasher) EICAR-test-file': '0',
            '(Salience=999999) Skip url that is already malicious': '0',
            '(Salience=100000) MGW Heuristic.BehavesLike.JS.CodeUnfolding': '0',
            '(Salience=099987) Sophos EICAR-AV-Test': '0',
            '(Salience=099977) GameVance': '0',
            '(Salience=099976) Skip and Email urls that match Sanity Check List': '0',
            '(Salience=099990) McAfee Unwanted.WebSearch.gen!92': '0',
            '(Salience=099985) Sophos Troj Psyme': '0',
            '(Salience=100004) MGW Heuristic.BehavesLike.JS.Obfuscated': '0'
        }


class SAUserDisputesConfig(HarvesterConfig):
    harvester_name = 'SAUserDisputes'
    session_owner = 'SAUserDisputes'
    properties_file = HarvesterConfig.base_conf + 'sauserdisputes.properties'
    working_dir = HarvesterConfig.base_working + harvester_name + '/working/'
    mapr_dir = HarvesterConfig.base_mapr + harvester_name + '/'
    src_dir = HarvesterConfig.base_src + harvester_name + '/'
    processed_files = HarvesterConfig.base_working + harvester_name + '/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {'(Salience=000000) Queue user dispute URL': '0'}


class SEOTrendsConfig(HarvesterConfig):
    harvester_name = 'SEOTrends'
    session_owner = 'SEOTrends'
    properties_file = HarvesterConfig.base_conf + 'SEOTrends.properties'
    working_dir = HarvesterConfig.base_working + harvester_name + '/working/'
    mapr_dir = HarvesterConfig.base_mapr + harvester_name + '/'
    src_dir = HarvesterConfig.base_src + harvester_name + '/'
    processed_files = HarvesterConfig.base_working + harvester_name + '/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=000001) Crawl url': '0'
        }


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
        self.rules_matched = {
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


class SURBLABConfig(HarvesterConfig):
    harvester_name = 'SURBLAB'
    session_owner = 'SURBLAB'
    properties_file = HarvesterConfig.base_conf + 'SURBLAB.properties'
    working_dir = HarvesterConfig.base_working + harvester_name + '/working/'
    mapr_dir = HarvesterConfig.base_mapr + harvester_name + '/'
    src_dir = HarvesterConfig.base_src + harvester_name + '/'
    processed_files = HarvesterConfig.base_working + harvester_name + '/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=000550) Skip urls that are already Spam': '0',
            '(Salience=000800) Skip urls that were removed from the source': '0',
            '(Salience=000000) Default Rule is to Queue': '0',
            '(Salience=000900) Skip all urls not from AB feed': '0',
            '(Salience=000500) Queue url - trusted categories': '0',
            '(Salience=000450) Queue hl re tr categories': '0',
            '(Salience=000400) Queue Alexa Top 1M': '0',
            '(Salience=000200) Append su to URL': '0',
            '(Salience=000700) Skip URL that matches sanity check list': '0',
            '(Salience=000600) Skip urls that are already Malicious': '0',
            '(Salience=000300) Queue IPs': '0'
        }


class TORConfig(HarvesterConfig):
    harvester_name = 'TOR'
    session_owner = 'TOR'
    properties_file = HarvesterConfig.base_conf + 'tor.properties'
    working_dir = HarvesterConfig.base_working + harvester_name + '/working/'
    mapr_dir = HarvesterConfig.base_mapr + harvester_name + '/'
    src_dir = HarvesterConfig.base_src + harvester_name + '/'
    processed_files = HarvesterConfig.base_working + harvester_name + '/processedFiles.txt'

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=009999) Skip URL that matches sanity check list': '0',
            '(Salience=000000) Import everything as an': '0'
        }


class HarvesterWWUncat(HarvesterConfig):
    harvester_name = 'WWUncat'
    session_owner = 'WWUncat'
    properties_file = HarvesterConfig.base_conf + 'wwuncat.properties'
    working_dir = HarvesterConfig.base_working + 'WWUncat/working/'
    processed_files = HarvesterConfig.base_working + 'WWUncat/processedFiles.txt'


class ZonatorQDConfig(HarvesterConfig):
    """Config for ZonatorQD"""
    start_zonator_harvester = '''java -cp /opt/sftools/conf/:`perl %s /opt/sftools/java/lib`:`perl /home/toolguy/jars_in /opt/sftools/java/jboss/client`-Dlog4j.configuration=log4j.xml -Djava.library.path=/opt/sftools/lib com.securecomputing.sftools.harvester.ZonatorQD /opt/sftools/conf/ZonatorQD.properties''' % (
        runtime.data_path + '/harvesters/ZonatorQD/jars_in')
    harvester_name = 'ZonatorQD'
    session_owner = 'ZonatorQD'
    prev_file_name = '/zonator_ff_domains.txt.previous'
    properties_file = HarvesterConfig.base_conf + 'ZonatorQD.properties'
    working_dir = HarvesterConfig.base_working + harvester_name
    archive_dir = working_dir + '/source_file_archive'
    previous_file = HarvesterConfig.base_working + harvester_name + prev_file_name

    def __init__(self):
        HarvesterConfig.__init__(self)
        self.rules_matched = {
            '(Salience=000100) Append qd to new urls': '0'
        }