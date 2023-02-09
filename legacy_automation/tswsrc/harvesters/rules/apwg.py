"""
===================================
APWG tests
===================================
"""


from harvesters.harvester import *
from harvesters.harvester_config import HarvesterAPWG


class APWG(SandboxedHarvesterTest):
    """APWG Tests"""
    testprefix = 'test'
    default_har_config = HarvesterAPWG
    def test_apwg_01(self):
        """

        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=000000) Default rule is to queue url'] = '1'
        hcon.action_taken['Urls Queued'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/01.txt', hcon.action_taken, hcon.rules_matched)

    def test_apwg_02(self):
        """
        rule "(Salience=000200) Append Ph to url with path - score greater or equal to 50"
        The Path score of the URL supplied is greater than 50 then Category of that URL will be Appended with "Ph" (phishing category) along with its existing category
        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=000200) Append Ph to url with path - score greater or equal to 50'] = '1'
        hcon.action_taken['Urls with Categories Appended'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/02.txt', hcon.action_taken, hcon.rules_matched)
    
    def test_apwg_03(self):
        """
        rule "(Salience=000300) Queue categorized url with path - score greater or equal to 50"
        If the URL has path then score of the URL supplied is greater than 50 then Category of that URL will be Appended with "Ph" (phishing category) along with its existing category
        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=000300) Queue categorized url with path - score greater or equal to 50'] = '1'
        hcon.action_taken['Urls Queued'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/03.txt', hcon.action_taken, hcon.rules_matched)
    
    def test_apwg_04(self):
        """
        rule "(Salience=000400) Append Ph to url - score equal to 100"
        If the score of the URL supplied is greater than 100 then Category of that URL will be Appended with "Ph" (phishing category) along with its existing category
        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=000400) Append Ph to url - score equal to 100'] = '1'
        hcon.action_taken['Urls with Categories Appended'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/04.txt', hcon.action_taken, hcon.rules_matched)

    
    def test_apwg_05(self):
        """
        rule "(Salience=000500) Shorten to target term in path score greater or equal to 50"
        If the score of the URL supplied is greater than 50 and the url path contains any of the terms such as 82bank|abcbrasil|abnamro then shorten the url till the target term (action taken field for url shortening rule is "Urls with Categories Appended") 
        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=000500) Shorten to target term in path score greater or equal to 50'] = '1'
        hcon.action_taken['Urls with Categories Appended'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/05.txt', hcon.action_taken, hcon.rules_matched)
    
    def test_apwg_06(self):
        """
        rule "(Salience=000600) Queue and Email url with fp term - path"
        If path contains any of the terms such as newsletter-|/newsletter/|-amazon|amazon- then queue the url to phishing queue with priority 8800
        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=000600) Queue and Email url with fp term - path'] = '2'
        hcon.action_taken['Urls Emailed to Web Analysts'] = '1'
        hcon.action_taken['Urls Queued'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/06.txt', hcon.action_taken, hcon.rules_matched)

    def test_apwg_07(self):
        """
        rule "(Salience=000601) Queue and Email url with fp term - cgi"
        If query matches "utm_.*" in the url then queue the url to phishing queue with priority 8800
        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=000601) Queue and Email url with fp term - cgi'] = '2'
        hcon.action_taken['Urls Queued'] = '1'
        hcon.action_taken['Urls Emailed to Web Analysts'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/07.txt', hcon.action_taken, hcon.rules_matched)
    
    def test_apwg_08(self):
        """
        rule "(Salience=000602) Queue and Email url with fp term - file"
        If path matches ".*\\.(png|gif|jpg|jpeg|pdf) in the url then queue the url to phishing queue with priority 8800
        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=000602) Queue and Email url with fp term - file'] = '2'
        hcon.action_taken['Urls Queued'] = '1'
        hcon.action_taken['Urls Emailed to Web Analysts'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/08.txt', hcon.action_taken, hcon.rules_matched)
    
    def test_apwg_09(self):
        """
        rule "(Salience=000603) Queue and Email url with fp term - file+cgi"
        If path matches ".*\\.(asp|aspx)" and the query != null in the url then queue the url to phishing queue with priority 8800
        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=000603) Queue and Email url with fp term - file+cgi'] = '2'
        hcon.action_taken['Urls Queued'] = '1'
        hcon.action_taken['Urls Emailed to Web Analysts'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/09.txt', hcon.action_taken, hcon.rules_matched)
    
    def test_apwg_10(self):
        """
        rule "(Salience=000700) Append Ph to url with security cats"
        If the current category is in any of the security cats such as Malicious Sites","Malicious Downloads","Spyware","PUPs","Browser Exploit","Spam Email URLs, then append the  phishing category to the url
        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=000700) Append Ph to url with security cats'] = '1'
        hcon.action_taken['Urls with Categories Appended'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/10.txt', hcon.action_taken, hcon.rules_matched)
    
    def test_apwg_11(self):
        """
        rule "(Salience=001000) Skip url that is already Phishing"
        If the current category is phishing then ignore the URL and take no action
        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=001000) Skip url that is already Phishing'] = '1'
        hcon.action_taken['Urls Ignored'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/11.txt', hcon.action_taken, hcon.rules_matched)
    
    def test_apwg_12(self):
        """
        rule "(Salience=001100) Remove ph category"
        If the current category is phishing and the remove flaf is set in the url then remove the ph category to the url and queue the url for TMAN
        Ex: "EBAY",2013-01-20 06:38:14,0,"http://www.ec-firstclass.org/","http%3A%2F%2Fwww.ec-firstclass.org%2F",URL
        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=001100) Remove ph category'] = '1'
        hcon.action_taken['Urls with Categories Removed'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/12.txt', hcon.action_taken, hcon.rules_matched)

    def test_apwg_13(self):
        """
        rule "(Salience=000800) Queue HTTPS url"
        If the url has https:// then queue the url to WA for further analysis
        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=000800) Queue HTTPS url'] = '1'
        hcon.action_taken['Urls Queued'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/13.txt', hcon.action_taken, hcon.rules_matched)

    def test_apwg_14(self):
        """
        rule "(Salience=000900) Queue URL with trusted cats"
        If the url has trusted categories such as "Stock Trading","Finance/Banking","Business" then queue the url to TrustedCats_DMS queue with priority "8800" for further analysis
        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=000900) Queue URL with trusted cats'] = '1'
        hcon.action_taken['Urls Queued'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/14.txt', hcon.action_taken, hcon.rules_matched)
    
    def test_apwg_15(self):
        """
        rule "(Salience=000100) Queue url with no path - score greater or equal to 50"
        If the url has no path and the score is >=50 tqueue the url to TrustedCats_DMS queue with priority "8800" for further analysis
        """
        hcon = HarvesterAPWG()
        hcon.rules_matched['(Salience=000100) Queue url with no path - score greater or equal to 50'] = '1'
        hcon.action_taken['Urls Queued'] = '1'
        hobj = Harvester(hcon,"partial")
        hobj.test_harvester_base('APWG/15.txt', hcon.action_taken, hcon.rules_matched)

