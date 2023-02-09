"""
===============================
Tiered Harvest tests - obsolete
===============================
"""
import logging
import time
import unittest
from datetime import date
from datetime import timedelta

from harvesters.harvester import Harvester
from harvesters.harvester_config import HarvesterAPWG, HarvesterMRTUF, HarvesterRepper, HarvesterWWUncat
from lib.db.mdbthf import MongoWrapthfDB
from framework.test import SandboxedTest


class NormalizationTest(SandboxedTest):
    default_har_config = HarvesterAPWG

    def __test_normalization_base(self, tcid, original_url, normalized_url):
        """
                Method used by all normalization test cases to run the harvester,
                get the document from DB, perform the comparisons, show the results.
                Also removes the document from DB.
        """
        logging.info("Starting Testcase : " + tcid)

        hcon = HarvesterAPWG()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        run_result = hobj.run_harvester('thf/%s.txt' % tcid)

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        # Wait for 2 seconds
        time.sleep(2)

        # THF properties file path.
        #thf_properties_file='/home/toolguy/tsa/thf/tieredharvest.properties'

        mongo_obj = MongoWrapthfDB("tieroneurl")

        # Get the document from mongodb based on normalized url
        #db_obj= DbConnection(thf_properties_file)
        #document=db_obj.get_mongodb_doc(normalized_url)

        document = mongo_obj.thf_fetch_one_normalized_url(normalized_url)

        # Check whether the document is null.
        if document is not None:
            #{
            logging.info('Document found in DB.')
            #db_obj.remove_mongodb_doc(normalized_url)
            mongo_obj.thf_remove_normalized_url(normalized_url)
            logging.info('Removed document from DB.')

            # Check for the original url in the set of original urls in the document.
            logging.info('original_url:' + original_url)
            if original_url in document["originalUrls"]:
                # {
                # For normalization failure case, check for the "normalized" field in schema.
                if tcid == 18:
                    # {
                    if document["normalized"] == 'no':
                        logging.info('Normalization failure check - %s: PASS' % tcid)
                    else:
                        # {
                        logging.error('normalized field is missing in the document')
                        logging.error('Normalization failure check - %s: FAIL' % tcid)
                        raise AssertionError('Normalization failure check: FAIL')
                        # }
                # }
                logging.info('Normalization test case result - %s: PASS' % tcid)
                # }
            else:
                # {
                logging.error('original url not found in the set of original urls')
                logging.error('Normalization test result - %s: FAIL' % tcid)
                raise AssertionError("Normalization test result: FAIL")
                # }
                # }
        else:
            #{
            logging.error('Document not found in DB.')
            raise AssertionError("Normalization test result: FAIL")
            #}


    def test_normalization_01(self):
        """
        TS-924:Tiered Harvest- URL Normalization - Host and scheme to lower-case
        To test converting the scheme and host to lower case.
        """
        tcid = 'N1'

        original_url = 'HTTP://www.Example.com/'
        normalized_url = 'http://www.example.com/'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_02(self):
        """
        TS-925:Tiered Harvest- URL Normalization - Upper-case escape sequences in path.
        To test capitalizing letters in escape sequences
        in path of the URL.
        """
        tcid = 'N2'

        original_url = 'http://www.example.com/Path/A%c2%b1b'
        normalized_url = 'http://www.example.com/Path/A%C2%B1b'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_03(self):
        """
        TS-926:Tiered Harvest- URL Normalization - Upper-case escape sequences in path and CGI.
        To test capitalizing letters in escape sequences
        in path and CGI of the URL.
        """
        tcid = 'N3'

        original_url = 'http://server.com/path/a%c2%b1bEusername/program?query_stria%3a%3dEng'
        normalized_url = 'http://server.com/path/a%C2%B1bEusername/program?query_stria%3A%3DEng'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_04(self):
        """
        TS-927:Tiered Harvest- URL Normalization - Decoding percent-encoded hex of unreserved characters.
            To test Decoding percent-encoded hex of unreserved characters.
        """
        tcid = 'N4'

        original_url = 'http://www.example.com/%41username/'
        normalized_url = 'http://www.example.com/Ausername/'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_05(self):
        """
        TS-928:Tiered Harvest- URL Normalization - Decoding percent-encoded octets of unreserved characters only in
            To test Decoding percent-encoded octets of unreserved characters only in Path not in CGI.
        """
        tcid = 'N5'

        original_url = 'http://server.com/path/%2Eusername/program?query_stri%3AEng'
        normalized_url = 'http://server.com/path/.username/program?query_stri%3AEng'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_06(self):
        """
        TS-929:Tiered Harvest- URL Normalization . Encoding percent-encoded octets of unreserved characters in path
        To test encoding illegal characters
        in the path (not cgi) portion of the URL.
        """
        tcid = 'N6'

        original_url = 'http://www.example.com/~xyz/'
        normalized_url = 'http://www.example.com/%7Exyz/'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_07(self):
        """
        TS-930:Tiered Harvest- URL Normalization- Add trailing slash (/) for domain based entries.
        To test adding trailing slash (/) for domain based entries.
        """
        tcid = 'N7'

        original_url = 'http://example.com'
        normalized_url = 'http://example.com/'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_08(self):
        """
        TS-931:Tiered Harvest- URL Normalization- Removing all default ports.
        To test removing the default port.
        The default port (port 80 for the http scheme) may be removed from (or added to) a URL. 
        """
        tcid = 'N8'

        original_url = 'https://www.example.com:443/bar.html'
        normalized_url = 'https://www.example.com/bar.html'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_09(self):
        """
        TS-932:Tiered Harvest- URL Normalization- Not removing default ports.
        To test non default port.
        """
        tcid = 'N9'

        original_url = 'http://www.example.com:8080/bar.html'
        normalized_url = 'http://www.example.com:8080/bar.html'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_10(self):
        """
        TS-933:Tiered Harvest- URL Normalization- Removing dot segments.
        To test removing dot-segments. 
        """
        tcid = 'N10'

        original_url = 'http://www.example.com/../a/b/../c/./d.html'
        normalized_url = 'http://www.example.com/a/c/d.html'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_11(self):
        """
        TS-934:Tiered Harvest- URL Normalization- Normalize IPv4 and IPv6 URLs.
        To test Normalizing and canonicalizing
        the different representations of IPv4 and IPv6 URLs 
        """
        tcid = 'N11'

        original_url = 'http://205.147.201.42'
        normalized_url = 'http://205.147.201.42/'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_12(self):
        """
        TS-935:Tiered Harvest- URL Normalization- Different representations of the same IPV4 URL are mapped to the
        To test if different representations of the same IPV4 URL are mapped to the same normalized URL.
        """
        tcid = 'N12'

        original_url = 'http://0xC0.0x00.0x02.0xEB'
        normalized_url = 'http://192.0.2.235/'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_13(self):
        """
        TS-936:Tiered Harvest- URL Normalization- Domains with illegal characters.
        To test if the normalizer accepts URLs with underscores OR -. OR .- in domain names.
        It also accepts URLs with domains starting with – .
        """
        tcid = 'N13'

        original_url = 'http://4-ALL-OBY-.5O4.LATE-5WBF.-Z-L2O-5FIO.SAVINGSMASTERYDEALSALWAYSS.COM'
        normalized_url = 'http://4-all-oby-.5o4.late-5wbf.-z-l2o-5fio.savingsmasterydealsalwayss.com/'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_14(self):
        """
        TS-937:Tiered Harvest- URL Normalization- Illegal escape characters at the end of the path.
        To test URLs with illegal percent-escape sequences are not be rejected.
        For URLs having an illegal percent-escape sequence %7, the % character is itself percent-escaped.
        """
        tcid = 'N14'

        original_url = 'http://www.example.com/Path%7'
        normalized_url = 'http://www.example.com/Path%257'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_15(self):
        """
        TS-938:Tiered Harvest- URL Normalization- Reserved characters in path and CGI.
        To test if reserved characters in path and CGI components are percent-escaped.
        """
        tcid = 'N15'

        original_url = 'http://example.com/path?cgi+name$abc/47rt3'
        normalized_url = 'http://example.com/path?cgi%2Bname%24abc%2F47rt3'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_16(self):
        """
        TS-939:Tiered Harvest- URL Normalization- Percent-escaped unreserved characters in path and CGI.
        To test if percent-escaped unreserved characters in path and CGI
        are decoded back to their unreserved form.
        """
        tcid = 'N16'

        original_url = 'http://example.com/Path/cgi?a=b%5F87880'
        normalized_url = 'http://example.com/Path/cgi?a=b_87880'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_17(self):
        """
        TS-940:Tiered Harvest- URL Normalization- Conversion of non ascii character '.' in the CGI.
        To test for conversion of non ascii character 'δ' in the CGI.
        """
        tcid = 'N17'

        original_url = 'http://www.McAfee.com/us/index.html?var=δ'
        normalized_url = 'http://www.mcafee.com/us/index.html?var=%CE%B4'
        original_url = str(original_url, 'UTF-8')

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_18(self):
        """
        TS-941:Tiered Harvest- URL Normalization- Test for failure of URL Normalization.
        To test whether URL Nomalization fails if the URL is invalid.
        """
        tcid = 'N18'

        original_url = 'HTTP://192.168.275.310'
        normalized_url = 'HTTP://192.168.275.310'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_19(self):
        """
        TS-942:Tiered Harvest- URL Normalization- URLs beginning with *:// are persisted to DB.
        To test if urls beginning with *:// are being persisted to DB
        """
        tcid = 'N19'

        original_url = '*://update.sinkpop.com/d1/cb.exe'
        normalized_url = 'http://update.sinkpop.com/d1/cb.exe'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_20(self):
        """
        TS-943:Tiered Harvest- URL Normalization- Adding protocol (http://) if absent in the URL.
        To test if the protocol(http://) is being added to the url
        which is absent in the input file.(Appending it here for comparison)
        """
        tcid = 'N20'

        original_url = 'http://update.sinkpop.com/d1/cb.exe'
        normalized_url = 'http://update.sinkpop.com/d1/cb.exe'

        self.__test_normalization_base(tcid, original_url, normalized_url)

    @unittest.skip('Unsupported characters in the test data(url)')
    def test_normalization_21(self):
        """
        TS-944:Tiered Harvest- URL Normalization- Convert domain to IDN form.
        To test conversion of illegal and reserved characters to
        IDN puny code strings (assumed utf8) in the domain of the URL. 
        """
        tcid = 'N21'

        original_url = 'http://ÃÂ¢Ã¢âÂ¢ÃÂª.hawx.me/'
        #original_url='http://Ã¢ââÃª.hawx.me/.me/'
        normalized_url = 'http://xn--a-7baa9wbc1807c.hawx.me/'

        original_url = str(original_url, 'UTF-8')

        self.__test_normalization_base(tcid, original_url, normalized_url)

    def test_normalization_22(self):
        """
        TS-945:Tiered Harvest- URL Normalization- urls with more than 256 characters are normalized.
        To test if urls with more than 256 characters are getting normalized.
        """
        tcid = 'N22'

        original_url = 'http://www.google.com/search?hl=en&lr=&c2coff=1&rls=GGLG%2CGGLG%3A2005-26%2CGGLG%3Aen&q=http%3A%2F%2Fwww.google.com%2Fsearch%3Fhl%3Den%26lr%3D%26c2coff%3D1%26rls%3DGGLG%252CGGLG%253A2005-26%252CGGLG%253Aen%26q%3Dhttp%253A%252F%252Fwww.google.com%252Fsearch%253Fhl%253Den%2526lr%253D%2526c2coff%253D1%2526rls%253DGGLG%25252CGGLG%25253A2005-26%25252CGGLG%25253Aen%2526q%253Dhttp%25253A%25252F%25252Fwww.google.com%25252Fsearch%25253Fsourceid%25253Dnavclient%252526ie%25253DUTF-8%252526rls%25253DGGLG%25252CGGLG%25253A2005-26%25252CGGLG%25253Aen%252526q%25253Dhttp%2525253A%2525252F%2525252Fwww%2525252Egoogle%2525252Ecom%2525252Fsearch%2525253Fsourceid%2525253Dnavclient%25252526ie%2525253DUTF%2525252D8%25252526rls%2525253DGGLG%2525252CGGLG%2525253A2005%2525252D26%2525252CGGLG%2525253Aen%25252526q%2525253Dhttp%252525253A%252525252F%252525252Fuk2%252525252Emultimap%252525252Ecom%252525252Fmap%252525252Fbrowse%252525252Ecgi%252525253Fclient%252525253Dpublic%2525252526GridE%252525253D%252525252D0%252525252E12640%2525252526GridN%252525253D51%252525252E50860%2525252526lon%252525253D%252525252D0%252525252E12640%2525252526lat%252525253D51%252525252E50860%2525252526search%252525255Fresult%252525253DLondon%25252525252CGreater%252525252520London%2525252526db%252525253Dfreegaz%2525252526cidr%252525255Fclient%252525253Dnone%2525252526lang%252525253D%2525252526place%252525253DLondon%252525252CGreater%252525252BLondon%2525252526pc%252525253D%2525252526advanced%252525253D%2525252526client%252525253Dpublic%2525252526addr2%252525253D%2525252526quicksearch%252525253DLondon%2525252526addr3%252525253D%2525252526scale%252525253D100000%2525252526addr1%252525253D%2526btnG%253DSearch%26btnG%3DSearch&btnG=Search'
        normalized_url = 'http://www.google.com/search?hl=en&lr=&c2coff=1&rls=GGLG%2CGGLG%3A2005-26%2CGGLG%3Aen&q=http%3A%2F%2Fwww.google.com%2Fsearch%3Fhl%3Den%26lr%3D%26c2coff%3D1%26rls%3DGGLG%252CGGLG%253A2005-26%252CGGLG%253Aen%26q%3Dhttp%253A%252F%252Fwww.google.com%252Fsearch%253Fhl%253Den%2526lr%253D%2526c2coff%253D1%2526rls%253DGGLG%25252CGGLG%25253A2005-26%25252CGGLG%25253Aen%2526q%253Dhttp%25253A%25252F%25252Fwww.google.com%25252Fsearch%25253Fsourceid%25253Dnavclient%252526ie%25253DUTF-8%252526rls%25253DGGLG%25252CGGLG%25253A2005-26%25252CGGLG%25253Aen%252526q%25253Dhttp%2525253A%2525252F%2525252Fwww%2525252Egoogle%2525252Ecom%2525252Fsearch%2525253Fsourceid%2525253Dnavclient%25252526ie%2525253DUTF%2525252D8%25252526rls%2525253DGGLG%2525252CGGLG%2525253A2005%2525252D26%2525252CGGLG%2525253Aen%25252526q%2525253Dhttp%252525253A%252525252F%252525252Fuk2%252525252Emultimap%252525252Ecom%252525252Fmap%252525252Fbrowse%252525252Ecgi%252525253Fclient%252525253Dpublic%2525252526GridE%252525253D%252525252D0%252525252E12640%2525252526GridN%252525253D51%252525252E50860%2525252526lon%252525253D%252525252D0%252525252E12640%2525252526lat%252525253D51%252525252E50860%2525252526search%252525255Fresult%252525253DLondon%25252525252CGreater%252525252520London%2525252526db%252525253Dfreegaz%2525252526cidr%252525255Fclient%252525253Dnone%2525252526lang%252525253D%2525252526place%252525253DLondon%252525252CGreater%252525252BLondon%2525252526pc%252525253D%2525252526advanced%252525253D%2525252526client%252525253Dpublic%2525252526addr2%252525253D%2525252526quicksearch%252525253DLondon%2525252526addr3%252525253D%2525252526scale%252525253D100000%2525252526addr1%252525253D%2526btnG%253DSearch%26btnG%3DSearch&btnG=Search'

        self.__test_normalization_base(tcid, original_url, normalized_url)


class CoreWriteAPITest(SandboxedTest):
    def __corewriteAPI_base(self, tcid, normalized_url):
        """
                Method to get the document from DB and
                return it to the test case.
        """

        # Wait for 2 seconds
        time.sleep(2)

        # THF properties file path.
        #thf_properties_file='/home/toolguy/tsa/thf/tieredharvest.properties'

        # Get the document from mongodb based on normalized url
        #db_obj= DbConnection(thf_properties_file)
        #document=db_obj.get_mongodb_doc(normalized_url)

        mongo_obj = MongoWrapthfDB("tieroneurl")

        document = mongo_obj.thf_fetch_one_normalized_url(normalized_url)

        # Check whether the document is null.
        if document is not None:
            # {
            logging.info('Document found in DB.')
            return document
        # }
        else:
            # {
            logging.error('Document not found in DB. Test result - %s: FAIL' % tcid)
            raise AssertionError("Core write API test result: FAIL")
            # }


    def test_corewrite_api_01(self):
        """
        TS-946:Tiered Harvester - URL persistance & de-duplication for synchronous Write (new url)
        To test Tiered Harvester -URL persistance & de-duplication for synchronous Write
        with a new url from a 3rd party harvester with metadata 
        """
        tcid = 'C1'

        logging.info("Starting Testcase : " + tcid)

        # Create harvester object.
        hcon = HarvesterAPWG()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        # Run the harvester.
        run_result = hobj.run_harvester('thf/C1.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        normalized_url = 'http://testdefaultrule.com/'
        original_url = 'http://testdefaultrule.com'

        document = self.__corewriteAPI_base(tcid, normalized_url)

        # Check whether the document is null.
        if document is None:
            # {
            logging.error('Document not found in DB- Test result - %s: FAIL' % tcid)
            raise AssertionError("Core write API test result: FAIL")
        # }

        # THF properties file path.
        #thf_properties_file='/home/toolguy/tsa/thf/tieredharvest.properties'

        # Remove the document from DB
        #db_obj= DbConnection(thf_properties_file)
        #db_obj.remove_mongodb_doc(normalized_url)
        mongo_obj = MongoWrapthfDB("tieroneurl")

        mongo_obj.thf_remove_normalized_url(normalized_url)
        logging.info('Removed document from DB.')

        harvesterEventsList = document["harvesterEvents"]
        harvesterEvent = harvesterEventsList[0]

        metadata = harvesterEvent["rawMetadata"]

        dailySeenDateCount = document["dailySeenDateCount"]

        # Current date for comparing the dailySeenDateCount in schema 
        currentDate = date.today().strftime("%m-%d-%Y")
        #currentDate = datetime.utcnow().strftime("%m-%d-%Y")
        logging.info("currentDate")
        logging.info(currentDate)

        #Compare all fields in the document with input data.
        #eventType is new and dailySeenDateCount is 1 for current date.

        if (not original_url in document["originalUrls"]):
            # {
            raise AssertionError("Core write API test result: FAIL, Original url not found in the original urls list.")
        # }

        self.assertEqual(document["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document["canonicalizedDomain"], "testdefaultrule.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")

        self.assertEqual(harvesterEvent["sourceId"], "APWG",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata["date_added"], "2013-01-22 05:32:44",
                         "Core write API test result: FAIL, Metadata- date_added field mismatch.")
        self.assertEqual(metadata["harvester_name"], "APWG",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(metadata["score"], "100", "Core write API test result: FAIL, Metadata- score field mismatch.")
        self.assertEqual(metadata["target"], "EBAY",
                         "Core write API test result: FAIL, Metadata- target field mismatch.")
        self.assertEqual(metadata["url_encoded"], "http%3A%2F%2Ftestdefaultrule.com",
                         "Core write API test result: FAIL, Metadata- url_encoded field mismatch.")
        self.assertEqual(metadata["type"], "URL", "Core write API test result: FAIL, Metadata- type field mismatch.")
        self.assertEqual(metadata["url"], original_url,
                         "Core write API test result: FAIL, Metadata- url field mismatch.")

        self.assertEqual(dailySeenDateCount[currentDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")

        logging.info("dailySeenDateCount is")
        logging.info(dailySeenDateCount)

        logging.info("currentDate is")
        logging.info(currentDate)

        logging.info('Core write API test result - %s: PASS' % tcid)


    def test_corewrite_api_02(self):
        """
        TS-947:Tiered Harvester - URL persistance & de-duplication for synchronous Write(existing url)
        To test Tiered Harvester - URL persistance & de-duplication for synchronous Write
        with an existing url(inserted on current date) from an existing source(3rd party harvester) with same metadata
        """
        tcid = 'C2'

        logging.info("Starting Testcase : " + tcid)

        # Create harvetser object.
        hcon = HarvesterAPWG()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        # Run the harvester.
        run_result = hobj.run_harvester('thf/C2.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        normalized_url = 'http://miketest8.com/testpath'
        original_url = 'http://miketest8.com/testpath'

        document = self.__corewriteAPI_base(tcid, normalized_url)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        #Re-running harvester
        run_result = hobj.run_harvester('thf/C2.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        document = self.__corewriteAPI_base(tcid, normalized_url)

        # Check whether the document is null.
        if document is None:
            # {
            logging.error('Document not found in DB- Test result - %s: FAIL' % tcid)
            raise AssertionError("Core write API test result: FAIL")
        # }

        # THF properties file path.
        #thf_properties_file='/home/toolguy/tsa/thf/tieredharvest.properties'

        # Remove the document from DB
        #db_obj= DbConnection(thf_properties_file)
        #db_obj.remove_mongodb_doc(normalized_url)

        mongo_obj = MongoWrapthfDB("tieroneurl")

        mongo_obj.thf_remove_normalized_url(normalized_url)
        logging.info('Removed document from DB.')

        harvesterEventsList = document["harvesterEvents"]
        harvesterEvent = harvesterEventsList[0]
        metadata = harvesterEvent["rawMetadata"]
        dailySeenDateCount = document["dailySeenDateCount"]
        logging.info("dailySeenDateCount is")
        logging.info(dailySeenDateCount)
        # Current date for comparing the dailySeenDateCount in schema 
        currentDate = date.today().strftime("%m-%d-%Y")
        #currentDate = datetime.utcnow().strftime("%m-%d-%Y")
        logging.info("currentDate is")
        logging.info(currentDate)

        """
                Compare all fields in the document with input data.
                eventType is new even for the second run since it is a 3rd party harvester,
                and dailySeenDateCount is 1 for current date.
        """

        if (not original_url in document["originalUrls"]):
            # {
            raise AssertionError("Core write API test result: FAIL, Original url not found in the original urls list.")
        # }

        self.assertEqual(document["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document["canonicalizedDomain"], "miketest8.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")

        self.assertEqual(harvesterEvent["sourceId"], "APWG",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata["date_added"], "2013-01-22 05:32:44",
                         "Core write API test result: FAIL, Metadata- date_added field mismatch.")
        self.assertEqual(metadata["harvester_name"], "APWG",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(metadata["score"], "100", "Core write API test result: FAIL, Metadata- score field mismatch.")
        self.assertEqual(metadata["target"], "EBAY",
                         "Core write API test result: FAIL, Metadata- target field mismatch.")
        self.assertEqual(metadata["url_encoded"], "http%3A%2F%2Fmiketest8.com%2Ftestpath",
                         "Core write API test result: FAIL, Metadata- url_encoded field mismatch.")
        self.assertEqual(metadata["type"], "URL", "Core write API test result: FAIL, Metadata- type field mismatch.")
        self.assertEqual(metadata["url"], original_url,
                         "Core write API test result: FAIL, Metadata- url field mismatch.")

        self.assertEqual(dailySeenDateCount[currentDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")

        logging.info('Core write API test result - %s: PASS' % tcid)


    def test_corewrite_api_03(self):
        """
        TS-948:Tiered Harvester - URL persistance & de-duplication for synchronous Write(existing url-previous date).
        To test Tiered Harvester - URL persistance & de-duplication for synchronous Write
        with an existing url(inserted on previous date) from an existing source(3rd party harvester) with same metadata
        """
        tcid = 'C3'

        logging.info("Starting Testcase : " + tcid)

        # Create harvester object.
        hcon = HarvesterAPWG()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        # Run the harvester.
        run_result = hobj.run_harvester('thf/C3.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        normalized_url = 'http://miketest8.com/testpath123'
        original_url = 'http://miketest8.com/testpath123'

        document = self.__corewriteAPI_base(tcid, normalized_url)

        dailySeenDateCount = document["dailySeenDateCount"]

        # Current date for comparing the dailySeenDateCount in schema 
        currentDate = date.today().strftime("%m-%d-%Y")
        #currentDate = datetime.utcnow().strftime("%m-%d-%Y")
        logging.info("currentDate")
        logging.info(currentDate)

        # Previous date for comparing the dailySeenDateCount in schema 
        previousDate = (date.today() - timedelta(1)).strftime("%m-%d-%Y")
        #previousDate = (datetime.utcnow()-timedelta(1)).strftime("%m-%d-%Y")
        dailySeenDateCount = {previousDate: 1}
        document["dailySeenDateCount"] = dailySeenDateCount
        logging.info("previousDate")
        logging.info(previousDate)

        # THF properties file path.
        #thf_properties_file='/home/toolguy/tsa/thf/tieredharvest.properties'

        #db_obj= DbConnection(thf_properties_file)

        # Update dailySeenDateCount with previous date and count 1.
        #id_returned=db_obj.update_mongodb_doc(document)
        mongo_obj = MongoWrapthfDB("tieroneurl")
        id_returned = mongo_obj.save_document(document)


        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        #Re-running harvester
        run_result = hobj.run_harvester('thf/C2.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        document = self.__corewriteAPI_base(tcid, normalized_url)

        # Check whether the document is null.
        if document is None:
            # {
            logging.error('Document not found in DB- Test result - %s: FAIL' % tcid)
            raise AssertionError("Core write API test result: FAIL")
        # }

        # Remove the document from DB
        #db_obj= DbConnection(thf_properties_file)
        #db_obj.remove_mongodb_doc(normalized_url)

        mongo_obj = MongoWrapthfDB("tieroneurl")

        mongo_obj.thf_remove_normalized_url(normalized_url)
        logging.info('Removed document from DB.')

        harvesterEventsList = document["harvesterEvents"]
        harvesterEvent = harvesterEventsList[0]
        metadata = harvesterEvent["rawMetadata"]

        """
                Compare all fields in the document with input data.
                eventType is new even for the second run since it is a 3rd party harvester,
                and dailySeenDateCount is 1 for previous date(no entry for current date).
        """

        if (not original_url in document["originalUrls"]):
            # {
            raise AssertionError("Core write API test result: FAIL, Original url not found in the original urls list.")
        # }

        self.assertEqual(document["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document["canonicalizedDomain"], "miketest8.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")

        self.assertEqual(harvesterEvent["sourceId"], "APWG",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata["date_added"], "2013-01-22 05:32:44",
                         "Core write API test result: FAIL, Metadata- date_added field mismatch.")
        self.assertEqual(metadata["harvester_name"], "APWG",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(metadata["score"], "100", "Core write API test result: FAIL, Metadata- score field mismatch.")
        self.assertEqual(metadata["target"], "EBAY",
                         "Core write API test result: FAIL, Metadata- target field mismatch.")
        self.assertEqual(metadata["url_encoded"], "http%3A%2F%2Fmiketest8.com%2Ftestpath123",
                         "Core write API test result: FAIL, Metadata- url_encoded field mismatch.")
        self.assertEqual(metadata["type"], "URL", "Core write API test result: FAIL, Metadata- type field mismatch.")
        self.assertEqual(metadata["url"], original_url,
                         "Core write API test result: FAIL, Metadata- url field mismatch.")

        self.assertEqual(dailySeenDateCount[previousDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")
        self.assertTrue(currentDate not in dailySeenDateCount)

        logging.info("dailySeenDateCount is")
        logging.info(dailySeenDateCount)

        logging.info("currentDate is")
        logging.info(currentDate)

        logging.info('Core write API test result - %s: PASS' % tcid)


    def test_corewrite_api_04(self):
        """
        TS-949:Tiered Harvester - URL persistance & de-duplication for synchronous Write(existing url)- different metadata.
        To test Tiered Harvester - URL persistance & de-duplication for synchronous Write
        with an existing url (inserted on current date) from an existing source(3rd party harvester) with different metadata
        """
        tcid = 'C4'

        logging.info("Starting Testcase : " + tcid)

        # Create harvester object.
        hcon = HarvesterAPWG()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        #Run the harvester.
        run_result = hobj.run_harvester('thf/C4a.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        normalized_url = 'http://shoeten82bank.com/testing/asahibank/testpath'
        original_url = 'http://shoeten82bank.com/testing/asahibank/testpath'
        document = self.__corewriteAPI_base(tcid, normalized_url)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        #Re-running harvester
        run_result = hobj.run_harvester('thf/C4b.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        document = self.__corewriteAPI_base(tcid, normalized_url)

        # Check whether the document is null.
        if document is None:
            # {
            logging.error('Document not found in DB- Test result - %s: FAIL' % tcid)
            raise AssertionError("Core write API test result: FAIL")
        # }

        # THF properties file path.
        #thf_properties_file='/home/toolguy/tsa/thf/tieredharvest.properties'

        # Remove the document from DB
        #db_obj= DbConnection(thf_properties_file)
        #db_obj.remove_mongodb_doc(normalized_url)

        mongo_obj = MongoWrapthfDB("tieroneurl")

        mongo_obj.thf_remove_normalized_url(normalized_url)
        logging.info('Removed document from DB.')

        harvesterEventsList = document["harvesterEvents"]
        harvesterEvent1 = harvesterEventsList[0]
        harvesterEvent2 = harvesterEventsList[1]

        metadata1 = harvesterEvent1["rawMetadata"]
        metadata2 = harvesterEvent2["rawMetadata"]

        # Set metadata based on the order of harvester events in the document.
        if metadata2["date_added"] == "2013-01-22 05:32:44":
            # {
            metadata2 = harvesterEvent1["rawMetadata"]
            metadata1 = harvesterEvent2["rawMetadata"]
        # }

        dailySeenDateCount = document["dailySeenDateCount"]

        logging.info("dailySeenDateCount is")
        logging.info(dailySeenDateCount)

        # Current date for comparing the dailySeenDateCount in schema 
        currentDate = date.today().strftime("%m-%d-%Y")
        #currentDate = datetime.utcnow().strftime("%m-%d-%Y")

        logging.info("currentDate is")
        logging.info(currentDate)

        """
                Compare all fields in the document with input data.
                New harvester event is added since metadata is different.
                eventType is new even for both the harvester events,
                and dailySeenDateCount is 2 for current date.
        """

        if (not original_url in document["originalUrls"]):
            # {
            raise AssertionError("Core write API test result: FAIL, Original url not found in the original urls list.")
        # }

        self.assertEqual(document["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document["canonicalizedDomain"], "shoeten82bank.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")

        self.assertEqual(harvesterEvent1["sourceId"], "APWG",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent1["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata1["date_added"], "2013-01-22 05:32:44",
                         "Core write API test result: FAIL, Metadata- date_added field mismatch.")
        self.assertEqual(metadata1["harvester_name"], "APWG",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(metadata1["score"], "50", "Core write API test result: FAIL, Metadata- score field mismatch.")
        self.assertEqual(metadata1["target"], "EBAY",
                         "Core write API test result: FAIL, Metadata- target field mismatch.")
        self.assertEqual(metadata1["url_encoded"], "http%3A%2F%2Fshoeten82bank.com%2Ftesting%2Fasahibank%2Ftestpath",
                         "Core write API test result: FAIL, Metadata- url_encoded field mismatch.")
        self.assertEqual(metadata1["type"], "URL", "Core write API test result: FAIL, Metadata- type field mismatch.")
        self.assertEqual(metadata1["url"], original_url,
                         "Core write API test result: FAIL, Metadata- url field mismatch.")

        self.assertEqual(harvesterEvent2["sourceId"], "APWG",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent2["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata2["date_added"], "2013-01-20 08:02:02",
                         "Core write API test result: FAIL, Metadata- date_added field mismatch.")
        self.assertEqual(metadata2["harvester_name"], "APWG",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(metadata2["score"], "50", "Core write API test result: FAIL, Metadata- score field mismatch.")
        self.assertEqual(metadata2["target"], "firstmerit",
                         "Core write API test result: FAIL, Metadata- target field mismatch.")
        self.assertEqual(metadata2["url_encoded"], "http%3A%2F%2Fshoeten82bank.com%2Ftesting%2Fasahibank%2Ftestpath",
                         "Core write API test result: FAIL, Metadata- url_encoded field mismatch.")
        self.assertEqual(metadata2["type"], "URL", "Core write API test result: FAIL, Metadata- type field mismatch.")
        self.assertEqual(metadata2["url"], original_url,
                         "Core write API test result: FAIL, Metadata- url field mismatch.")

        self.assertEqual(dailySeenDateCount[currentDate], 2,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")

        logging.info('Core write API test result - %s: PASS' % tcid)


    def test_corewrite_api_05(self):
        """
        TS-950:Tiered Harvester - URL persistance & de-duplication for synchronous Write(existing url)-different metadata.
        To test Tiered Harvester - URL persistance & de-duplication for synchronous Write
        with an existing url (inserted on previous date) from an existing source(3rd party harvester) with different metadata
        """
        tcid = 'C5'

        logging.info("Starting Testcase : " + tcid)

        #Create harvester object.
        hcon = HarvesterAPWG()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        # Run the harvester.
        run_result = hobj.run_harvester('thf/C5a.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        normalized_url = 'http://shoeten82bank.com/testing'
        original_url = 'http://shoeten82bank.com/testing'
        document = self.__corewriteAPI_base(tcid, normalized_url)

        # Current date for comparing the dailySeenDateCount in schema
        currentDate = date.today().strftime("%m-%d-%Y")
        #currentDate = datetime.utcnow().strftime("%m-%d-%Y")
        logging.info("currentDate")
        logging.info(currentDate)

        # Previous date for comparing the dailySeenDateCount in schema
        previousDate = (date.today() - timedelta(1)).strftime("%m-%d-%Y")
        #previousDate = (datetime.utcnow()-timedelta(1)).strftime("%m-%d-%Y")
        logging.info("previousDate")
        logging.info(previousDate)
        dailySeenDateCount = {previousDate: 1}
        document["dailySeenDateCount"] = dailySeenDateCount

        # THF properties file path.
        #thf_properties_file='/home/toolguy/tsa/thf/tieredharvest.properties'

        #db_obj= DbConnection(thf_properties_file)

        # Update dailySeenDateCount with previous date and count 1.
        #id_returned=db_obj.update_mongodb_doc(document)
        mongo_obj = MongoWrapthfDB("tieroneurl")
        id_returned = mongo_obj.save_document(document)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        #Re-running harvester
        run_result = hobj.run_harvester('thf/C5b.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        document = self.__corewriteAPI_base(tcid, normalized_url)

        # Check whether the document is null.
        if document is None:
            # {
            logging.error('Document not found in DB- Test result - %s: FAIL' % tcid)
            raise AssertionError("Core write API test result: FAIL")
        # }

        # Remove the document from DB
        #db_obj= DbConnection(thf_properties_file)
        #db_obj.remove_mongodb_doc(normalized_url)

        mongo_obj = MongoWrapthfDB("tieroneurl")

        mongo_obj.thf_remove_normalized_url(normalized_url)
        logging.info('Removed document from DB.')

        harvesterEventsList = document["harvesterEvents"]
        harvesterEvent1 = harvesterEventsList[0]
        harvesterEvent2 = harvesterEventsList[1]

        metadata1 = harvesterEvent1["rawMetadata"]
        metadata2 = harvesterEvent2["rawMetadata"]

        # Set metadata based on the order of harvester events in the document.
        if metadata2["date_added"] == "2013-01-22 05:32:44":
            # {
            metadata2 = harvesterEvent1["rawMetadata"]
            metadata1 = harvesterEvent2["rawMetadata"]
        # }


        dailySeenDateCount = document["dailySeenDateCount"]

        """
                Compare all fields in the document with input data.
                New harvester event is added since metadata is different.
                eventType is new even for both the harvester events,
                and dailySeenDateCount is 1 each for previous and current date.
        """

        if (not original_url in document["originalUrls"]):
            # {
            raise AssertionError("Core write API test result: FAIL, Original url not found in the original urls list.")
        # }

        self.assertEqual(document["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document["canonicalizedDomain"], "shoeten82bank.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")

        self.assertEqual(harvesterEvent1["sourceId"], "APWG",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent1["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata1["date_added"], "2013-01-22 05:32:44",
                         "Core write API test result: FAIL, Metadata- date_added field mismatch.")
        self.assertEqual(metadata1["harvester_name"], "APWG",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(metadata1["score"], "50", "Core write API test result: FAIL, Metadata- score field mismatch.")
        self.assertEqual(metadata1["target"], "EBAY",
                         "Core write API test result: FAIL, Metadata- target field mismatch.")
        self.assertEqual(metadata1["url_encoded"], "http%3A%2F%2Fshoeten82bank.com%2Ftesting",
                         "Core write API test result: FAIL, Metadata- url_encoded field mismatch.")
        self.assertEqual(metadata1["type"], "URL", "Core write API test result: FAIL, Metadata- type field mismatch.")
        self.assertEqual(metadata1["url"], original_url,
                         "Core write API test result: FAIL, Metadata- url field mismatch.")

        self.assertEqual(harvesterEvent2["sourceId"], "APWG",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent2["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata2["date_added"], "2013-01-20 08:02:02",
                         "Core write API test result: FAIL, Metadata- date_added field mismatch.")
        self.assertEqual(metadata2["harvester_name"], "APWG",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(metadata2["score"], "50", "Core write API test result: FAIL, Metadata- score field mismatch.")
        self.assertEqual(metadata2["target"], "firstmerit",
                         "Core write API test result: FAIL, Metadata- target field mismatch.")
        self.assertEqual(metadata2["url_encoded"], "http%3A%2F%2Fshoeten82bank.com%2Ftesting",
                         "Core write API test result: FAIL, Metadata- url_encoded field mismatch.")
        self.assertEqual(metadata2["type"], "URL", "Core write API test result: FAIL, Metadata- type field mismatch.")
        self.assertEqual(metadata2["url"], original_url,
                         "Core write API test result: FAIL, Metadata- url field mismatch.")

        self.assertEqual(dailySeenDateCount[previousDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")
        self.assertEqual(dailySeenDateCount[currentDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")

        logging.info("dailySeenDateCount is")
        logging.info(dailySeenDateCount)

        logging.info("currentDate is")
        logging.info(currentDate)

        logging.info('Core write API test result - %s: PASS' % tcid)


    def test_corewrite_api_06(self):
        """
        TS-951:Tiered Harvester - URL persistance & de-duplication for synchronous Write(existing url)-different source.
        To test Tiered Harvester - URL persistance & de-duplication for 3rd party harvester synchronous Write
        with an existing url(inserted on current date), a different source id & different metadata
        """
        tcid = 'C6'

        logging.info("Starting Testcase : " + tcid)

        # Create harvester object.
        hcon = HarvesterAPWG()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        # Run the harvester.
        run_result = hobj.run_harvester('thf/C6a.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        normalized_url = 'http://update.sinkpop.com/d1/cb.exe'
        original_url = 'http://update.sinkpop.com/d1/cb.exe'
        document = self.__corewriteAPI_base(tcid, normalized_url)

        # Create harvester object.
        hcon = HarvesterMRTUF()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        #Re-running harvester
        run_result = hobj.run_harvester('thf/Hashes-C6b.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        document = self.__corewriteAPI_base(tcid, normalized_url)

        # Check whether the document is null.
        if document is None:
            # {
            logging.error('Document not found in DB- Test result - %s: FAIL' % tcid)
            raise AssertionError("Core write API test result: FAIL")
        # }

        # THF properties file path.
        #thf_properties_file='/home/toolguy/tsa/thf/tieredharvest.properties'

        # Remove the document from DB
        #db_obj= DbConnection(thf_properties_file)
        #db_obj.remove_mongodb_doc(normalized_url)



        mongo_obj = MongoWrapthfDB("tieroneurl")

        mongo_obj.thf_remove_normalized_url(normalized_url)
        logging.info('Removed document from DB.')

        harvesterEventsList = document["harvesterEvents"]
        harvesterEvent1 = harvesterEventsList[0]
        harvesterEvent2 = harvesterEventsList[1]

        # Set metadata based on the order of harvester events in the document.
        if harvesterEvent1["sourceId"] == "APWG":
            # {
            harvesterEvent1 = harvesterEventsList[0]
            harvesterEvent2 = harvesterEventsList[1]
        # }
        elif harvesterEvent1["sourceId"] == "MRTUF":
            # {
            harvesterEvent1 = harvesterEventsList[1]
            harvesterEvent2 = harvesterEventsList[0]
        # }

        metadata1 = harvesterEvent1["rawMetadata"]
        metadata2 = harvesterEvent2["rawMetadata"]

        dailySeenDateCount = document["dailySeenDateCount"]

        # Current date for comparing the dailySeenDateCount in schema
        currentDate = date.today().strftime("%m-%d-%Y")
        #currentDate = datetime.utcnow().strftime("%m-%d-%Y")
        logging.info("currentDate")
        logging.info(currentDate)

        """
                Compare all fields in the document with input data.
                New harvester event is added since the source is different.
                eventType is new even for both the harvester events,
                and dailySeenDateCount is 2 for current date.
        """

        if (not original_url in document["originalUrls"]):
            # {
            raise AssertionError("Core write API test result: FAIL, Original url not found in the original urls list.")
        # }

        self.assertEqual(document["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document["canonicalizedDomain"], "update.sinkpop.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")

        self.assertEqual(harvesterEvent1["sourceId"], "APWG",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent1["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata1["date_added"], "2013-01-21 14:42:07",
                         "Core write API test result: FAIL, Metadata- date_added field mismatch.")
        self.assertEqual(metadata1["harvester_name"], "APWG",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(metadata1["score"], "50", "Core write API test result: FAIL, Metadata- score field mismatch.")
        self.assertEqual(metadata1["target"], "ato.gov.au",
                         "Core write API test result: FAIL, Metadata- target field mismatch.")
        self.assertEqual(metadata1["url_encoded"], "http%3A%2F%2Fupdate.sinkpop.com%2Fd1%2Fcb.exe",
                         "Core write API test result: FAIL, Metadata- url_encoded field mismatch.")
        self.assertEqual(metadata1["type"], "URL", "Core write API test result: FAIL, Metadata- type field mismatch.")
        self.assertEqual(metadata1["url"], original_url,
                         "Core write API test result: FAIL, Metadata- url field mismatch.")

        self.assertEqual(harvesterEvent2["sourceId"], "MRTUF",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent2["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata2["date_added"], "10/24/2011 5:54:45 AM",
                         "Core write API test result: FAIL, Metadata- date_added field mismatch.")
        self.assertEqual(metadata2["harvester_name"], "MRTUF",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(metadata2["id"], "17140942", "Core write API test result: FAIL, Metadata- id field mismatch.")
        self.assertEqual(metadata2["content_classification_type"], "clean",
                         "Core write API test result: FAIL, Metadata- content_classification_type field mismatch.")
        self.assertEqual(metadata2["content_md5"], "99B612C3399DC74E09E1C4517115A783",
                         "Core write API test result: FAIL, Metadata- content_md5 field mismatch.")
        self.assertEqual(metadata2["change_type"], "A",
                         "Core write API test result: FAIL, Metadata- change_type field mismatch.")
        self.assertEqual(metadata2["url"], original_url,
                         "Core write API test result: FAIL, Metadata- url field mismatch.")

        self.assertEqual(dailySeenDateCount[currentDate], 2,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")

        logging.info("dailySeenDateCount is")
        logging.info(dailySeenDateCount)

        logging.info("currentDate is")
        logging.info(currentDate)

        logging.info('Core write API test result - %s: PASS' % tcid)


    def test_corewrite_api_07(self):
        """
        TS-952:Tiered Harvester - URL persistance & de-duplication for synchronous Write(existing url- previous date) - different source.
        To test Tiered Harvester - URL persistance & de-duplication for 3rd party harvester synchronous Write
        with an existing url(inserted on previous date), a different source id & different metadata
        """
        tcid = 'C7'

        logging.info("Starting Testcase : " + tcid)

        # Create harvester object.
        hcon = HarvesterAPWG()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        # Run the harvester.
        run_result = hobj.run_harvester('thf/C7a.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        normalized_url = 'http://update.sinkpop.com/d1/cba.exe'
        original_url = 'http://update.sinkpop.com/d1/cba.exe'

        document = self.__corewriteAPI_base(tcid, normalized_url)

        # Current date for comparing the dailySeenDateCount in schema
        currentDate = date.today().strftime("%m-%d-%Y")
        #currentDate = datetime.utcnow().strftime("%m-%d-%Y")
        logging.info("currentDate")
        logging.info(currentDate)

        # Previous date for comparing the dailySeenDateCount in schema
        previousDate = (date.today() - timedelta(1)).strftime("%m-%d-%Y")
        #previousDate = (datetime.utcnow()-timedelta(1)).strftime("%m-%d-%Y")
        logging.info("previousDate")
        logging.info(previousDate)
        dailySeenDateCount = {previousDate: 1}
        document["dailySeenDateCount"] = dailySeenDateCount

        # THF properties file path.
        #thf_properties_file='/home/toolguy/tsa/thf/tieredharvest.properties'

        #db_obj= DbConnection(thf_properties_file)

        # Update dailySeenDateCount with previous date and count 1.
        #id_returned=db_obj.update_mongodb_doc(document)



        mongo_obj = MongoWrapthfDB("tieroneurl")
        id_returned = mongo_obj.save_document(document)




        # Create harvester object.
        hcon = HarvesterMRTUF()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        # Re-running harvester.
        run_result = hobj.run_harvester('thf/Hashes-C7b.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        document = self.__corewriteAPI_base(tcid, normalized_url)

        # Check whether the document is null.
        if document is None:
            # {
            logging.error('Document not found in DB- Test result - %s: FAIL' % tcid)
            raise AssertionError("Core write API test result: FAIL")
        # }

        # Remove the document from DB
        #db_obj= DbConnection(thf_properties_file)
        #db_obj.remove_mongodb_doc(normalized_url)
        mongo_obj = MongoWrapthfDB("tieroneurl")

        mongo_obj.thf_remove_normalized_url(normalized_url)
        logging.info('Removed document from DB.')

        harvesterEventsList = document["harvesterEvents"]
        harvesterEvent1 = harvesterEventsList[0]
        harvesterEvent2 = harvesterEventsList[1]

        # Set metadata based on the order of harvester events in the document.
        if harvesterEvent1["sourceId"] == "APWG":
            # {
            harvesterEvent1 = harvesterEventsList[0]
            harvesterEvent2 = harvesterEventsList[1]
        # }
        elif harvesterEvent1["sourceId"] == "MRTUF":
            # {
            harvesterEvent1 = harvesterEventsList[1]
            harvesterEvent2 = harvesterEventsList[0]
        # }

        metadata1 = harvesterEvent1["rawMetadata"]
        metadata2 = harvesterEvent2["rawMetadata"]

        dailySeenDateCount = document["dailySeenDateCount"]

        """
                Compare all fields in the document with input data.
                New harvester event is added since the source is different.
                eventType is new even for both the harvester events,
                and dailySeenDateCount is 1 for both previous and current date.
        """

        if (not original_url in document["originalUrls"]):
            # {
            raise AssertionError("Core write API test result: FAIL, Original url not found in the original urls list.")
        # }

        self.assertEqual(document["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document["canonicalizedDomain"], "update.sinkpop.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")

        self.assertEqual(harvesterEvent1["sourceId"], "APWG",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent1["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata1["date_added"], "2013-01-21 14:42:07",
                         "Core write API test result: FAIL, Metadata- date_added field mismatch.")
        self.assertEqual(metadata1["harvester_name"], "APWG",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(metadata1["score"], "50", "Core write API test result: FAIL, Metadata- score field mismatch.")
        self.assertEqual(metadata1["target"], "ato.gov.au",
                         "Core write API test result: FAIL, Metadata- target field mismatch.")
        self.assertEqual(metadata1["url_encoded"], "http%3A%2F%2Fupdate.sinkpop.com%2Fd1%2Fcba.exe",
                         "Core write API test result: FAIL, Metadata- url_encoded field mismatch.")
        self.assertEqual(metadata1["type"], "URL", "Core write API test result: FAIL, Metadata- type field mismatch.")
        self.assertEqual(metadata1["url"], original_url,
                         "Core write API test result: FAIL, Metadata- url field mismatch.")

        self.assertEqual(harvesterEvent2["sourceId"], "MRTUF",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent2["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata2["date_added"], "10/24/2011 5:54:45 AM",
                         "Core write API test result: FAIL, Metadata- date_added field mismatch.")
        self.assertEqual(metadata2["harvester_name"], "MRTUF",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(metadata2["id"], "17140942", "Core write API test result: FAIL, Metadata- id field mismatch.")
        self.assertEqual(metadata2["content_classification_type"], "clean",
                         "Core write API test result: FAIL, Metadata- content_classification_type field mismatch.")
        self.assertEqual(metadata2["content_md5"], "99B612C3399DC74E09E1C4517115A783",
                         "Core write API test result: FAIL, Metadata- content_md5 field mismatch.")
        self.assertEqual(metadata2["change_type"], "A",
                         "Core write API test result: FAIL, Metadata- change_type field mismatch.")
        self.assertEqual(metadata2["url"], original_url,
                         "Core write API test result: FAIL, Metadata- url field mismatch.")

        self.assertEqual(dailySeenDateCount[previousDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")
        self.assertEqual(dailySeenDateCount[currentDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")

        logging.info("dailySeenDateCount is")
        logging.info(dailySeenDateCount)

        logging.info("currentDate is")
        logging.info(currentDate)

        logging.info('Core write API test result - %s: PASS' % tcid)


    def test_corewrite_api_08(self):
        """
        TS-953:Tiered Harvester - URL persistance & de-duplication for Asynchronous Write (new url).
        To test Tiered Harvester -URL persistance & de-duplication for Asynchronous Write
        with a new url with metadata from a Customer Logs harvester
        """
        tcid = 'C8'

        logging.info("Starting Testcase : " + tcid)

        # Create harvester object.
        hcon = HarvesterRepper()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        # Run the harvester.
        run_result = hobj.run_harvester('thf/repper-C8.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        normalized_url = 'http://www.regtestqa4.com/'
        original_url = 'http://www.regTESTQa4.com'

        document = self.__corewriteAPI_base(tcid, normalized_url)

        # Check whether the document is null.
        if document is None:
            # {
            logging.error('Document not found in DB- Test result - %s: FAIL' % tcid)
            raise AssertionError("Core write API test result: FAIL")
        # }

        # THF properties file path.
        #thf_properties_file='/home/toolguy/tsa/thf/tieredharvest.properties'

        # Remove the document from DB
        #db_obj= DbConnection(thf_properties_file)
        #db_obj.remove_mongodb_doc(normalized_url)
        mongo_obj = MongoWrapthfDB("tieroneurl")

        mongo_obj.thf_remove_normalized_url(normalized_url)
        logging.info('Removed document from DB.')

        harvesterEventsList = document["harvesterEvents"]
        harvesterEvent = harvesterEventsList[0]

        metadata = harvesterEvent["rawMetadata"]
        dailySeenDateCount = document["dailySeenDateCount"]

        # Current date for comparing the dailySeenDateCount in schema
        currentDate = date.today().strftime("%m-%d-%Y")
        #currentDate = datetime.utcnow().strftime("%m-%d-%Y")
        logging.info("currentDate")
        logging.info(currentDate)

        """
                Compare all fields in the document with input data.
                eventType is new, and dailySeenDateCount is 1 for current date.
        """

        if (not original_url in document["originalUrls"]):
            # {
            raise AssertionError("Core write API test result: FAIL, Original url not found in the original urls list.")
        # }

        self.assertEqual(document["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document["canonicalizedDomain"], "regtestqa4.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")

        self.assertEqual(harvesterEvent["sourceId"], "Repper",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata["harvester_name"], "Repper",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(dailySeenDateCount[currentDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")

        logging.info("dailySeenDateCount is")
        logging.info(dailySeenDateCount)

        logging.info("currentDate is")
        logging.info(currentDate)

        logging.info('Core write API test result - %s: PASS' % tcid)


    def test_corewrite_api_09(self):
        """
        TS-954:Tiered Harvester - URL persistance & de-duplication for Asynchronous Write(existing url).
        To test Tiered Harvester - URL persistance & de-duplication for Asynchronous Write
        with an existing url (inserted on current date) from an existing source(Customer Logs) with same metadata.
        """
        tcid = 'C9'

        logging.info("Starting Testcase : " + tcid)

        # Create harvester object.
        hcon = HarvesterRepper()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        # Run the harvester.
        run_result = hobj.run_harvester('thf/repper-C9.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        normalized_url = 'http://excellentweightloss-solution.com/'
        original_url = 'http://excellentweightloss-solution.com/'

        document1 = self.__corewriteAPI_base(tcid, normalized_url)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        #Re-running harvester
        run_result = hobj.run_harvester('thf/repper-C9.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        document2 = self.__corewriteAPI_base(tcid, normalized_url)

        # Check whether the document is null.
        if document1 is None or document2 is None:
            # {
            logging.error('Document not found in DB- Test result - %s: FAIL' % tcid)
            raise AssertionError("Core write API test result: FAIL")
        # }

        # THF properties file path.
        #thf_properties_file='/home/toolguy/tsa/thf/tieredharvest.properties'

        # Remove the document from DB
        #db_obj= DbConnection(thf_properties_file)
        #db_obj.remove_mongodb_doc(normalized_url)
        mongo_obj = MongoWrapthfDB("tieroneurl")

        mongo_obj.thf_remove_normalized_url(normalized_url)
        logging.info('Removed document from DB.')

        harvesterEventsList1 = document1["harvesterEvents"]
        harvesterEvent1 = harvesterEventsList1[0]

        metadata1 = harvesterEvent1["rawMetadata"]
        dailySeenDateCount1 = document1["dailySeenDateCount"]

        # Current date for comparing the dailySeenDateCount in schema
        currentDate = date.today().strftime("%m-%d-%Y")
        #currentDate = datetime.utcnow().strftime("%m-%d-%Y")
        logging.info("currentDate")
        logging.info(currentDate)

        harvesterEventsList2 = document2["harvesterEvents"]
        harvesterEvent2 = harvesterEventsList2[0]

        metadata2 = harvesterEvent2["rawMetadata"]
        dailySeenDateCount2 = document2["dailySeenDateCount"]

        """
                Compare all fields in the document with input data.
                eventType is new, and dailySeenDateCount is 1 for current date for the first run.
                eventType is Update, and dailySeenDateCount is 2 for current date for the second run.
        """

        if (not original_url in document1["originalUrls"] or not original_url in document2["originalUrls"]):
            # {
            raise AssertionError("Core write API test result: FAIL, Original url not found in the original urls list.")
        # }

        self.assertEqual(document1["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document1["canonicalizedDomain"], "excellentweightloss-solution.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")
        self.assertEqual(harvesterEvent1["sourceId"], "Repper",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent1["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata1["harvester_name"], "Repper",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(dailySeenDateCount1[currentDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")

        self.assertEqual(document2["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document2["canonicalizedDomain"], "excellentweightloss-solution.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")
        self.assertEqual(harvesterEvent2["sourceId"], "Repper",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent2["eventType"], "Update",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata2["harvester_name"], "Repper",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(dailySeenDateCount2[currentDate], 2,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")

        logging.info("dailySeenDateCount1 is")
        logging.info(dailySeenDateCount1)

        logging.info("dailySeenDateCount2 is")
        logging.info(dailySeenDateCount2)

        logging.info("currentDate is")
        logging.info(currentDate)

        logging.info('Core write API test result - %s: PASS' % tcid)


    def test_corewrite_api_10(self):
        """
        TS-955:Tiered Harvester - URL persistance & de-duplication for Asynchronous Write(existing url-previous date).
        To test Tiered Harvester - URL persistance & de-duplication for Asynchronous Write
        with an existing url (inserted on previous date) from an existing source(Customer Logs) with same metadata
        """
        tcid = 'C10'

        logging.info("Starting Testcase : " + tcid)

        # Create the harvester object.
        hcon = HarvesterRepper()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        # Run the harvester.
        run_result = hobj.run_harvester('thf/repper-C10.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        normalized_url = 'http://excellentweightloss-solution.com/'
        original_url = 'http://excellentweightloss-solution.com/'

        document1 = self.__corewriteAPI_base(tcid, normalized_url)

        # Current date for comparing the dailySeenDateCount in schema
        currentDate = date.today().strftime("%m-%d-%Y")
        #currentDate = datetime.utcnow().strftime("%m-%d-%Y")
        logging.info("currentDate")
        logging.info(currentDate)

        # Previous date for comparing the dailySeenDateCount in schema
        previousDate = (date.today() - timedelta(1)).strftime("%m-%d-%Y")
        #previousDate = (datetime.utcnow()-timedelta(1)).strftime("%m-%d-%Y")
        logging.info("previousDate")
        logging.info(previousDate)
        dailySeenDateCount = {previousDate: 1}
        document1["dailySeenDateCount"] = dailySeenDateCount

        # THF properties file path.
        #thf_properties_file='/home/toolguy/tsa/thf/tieredharvest.properties'

        #db_obj= DbConnection(thf_properties_file)

        # Update dailySeenDateCount with previous date and count 1.
        #id_returned=db_obj.update_mongodb_doc(document1)
        mongo_obj = MongoWrapthfDB("tieroneurl")
        id_returned = mongo_obj.save_document(document1)


        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        #Re-running harvester
        run_result = hobj.run_harvester('thf/repper-C10.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        document2 = self.__corewriteAPI_base(tcid, normalized_url)

        # Check whether the document is null.
        if document1 is None or document2 is None:
            # {
            logging.error('Document not found in DB- Test result - %s: FAIL' % tcid)
            raise AssertionError("Core write API test result: FAIL")
        # }

        # Remove the document from DB
        #db_obj= DbConnection(thf_properties_file)
        #db_obj.remove_mongodb_doc(normalized_url)

        mongo_obj = MongoWrapthfDB("tieroneurl")

        mongo_obj.thf_remove_normalized_url(normalized_url)
        logging.info('Removed document from DB.')

        harvesterEventsList1 = document1["harvesterEvents"]
        harvesterEvent1 = harvesterEventsList1[0]
        metadata1 = harvesterEvent1["rawMetadata"]
        dailySeenDateCount = document2["dailySeenDateCount"]

        harvesterEventsList2 = document2["harvesterEvents"]
        harvesterEvent2 = harvesterEventsList2[0]
        metadata2 = harvesterEvent2["rawMetadata"]

        """
                Compare all fields in the document with input data.
                eventType is new, and dailySeenDateCount is 1 for previous date for the first run.
                eventType is Update, and dailySeenDateCount is 1 for both previous and current date for the second run.
        """

        if (not original_url in document1["originalUrls"] or not original_url in document2["originalUrls"]):
            # {
            raise AssertionError("Core write API test result: FAIL, Original url not found in the original urls list.")
        # }

        self.assertEqual(document1["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document1["canonicalizedDomain"], "excellentweightloss-solution.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")
        self.assertEqual(harvesterEvent1["sourceId"], "Repper",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent1["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata1["harvester_name"], "Repper",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")

        self.assertEqual(document2["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document2["canonicalizedDomain"], "excellentweightloss-solution.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")
        self.assertEqual(harvesterEvent2["sourceId"], "Repper",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent2["eventType"], "Update",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata2["harvester_name"], "Repper",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")

        self.assertEqual(dailySeenDateCount[previousDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")
        self.assertEqual(dailySeenDateCount[currentDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")

        logging.info("dailySeenDateCount is")
        logging.info(dailySeenDateCount)

        logging.info("currentDate is")
        logging.info(currentDate)

        logging.info('Core write API test result - %s: PASS' % tcid)


    def test_corewrite_api_11(self):
        """
        TS-956:Tiered Harvester - URL persistance & de-duplication for Asynchronous Write(existing url)-different source.
        To test Tiered Harvester - URL persistance & de-duplication for Asynchronous Write
        with an existing url (inserted on current date) from a different source(Customer Logs)
        """
        tcid = 'C11'

        logging.info("Starting Testcase : " + tcid)

        # Create the harvester object.
        hcon = HarvesterWWUncat()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        # Run the harvester.
        run_result = hobj.run_harvester('thf/wwuncat-C11a.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        normalized_url = 'http://google.com/'
        original_url = 'http://google.com'

        document1 = self.__corewriteAPI_base(tcid, normalized_url)

        # Create the harvester object.
        hcon = HarvesterRepper()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        # Re-running the harvester.
        run_result = hobj.run_harvester('thf/repper-C11b.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        document2 = self.__corewriteAPI_base(tcid, normalized_url)

        # Check whether the document is null.
        if document1 is None or document2 is None:
            # {
            logging.error('Document not found in DB- Test result - %s: FAIL' % tcid)
            raise AssertionError("Core write API test result: FAIL")
        # }

        # THF properties file path.
        #thf_properties_file='/home/toolguy/tsa/thf/tieredharvest.properties'

        # Remove the document from DB
        #db_obj= DbConnection(thf_properties_file)
        #db_obj.remove_mongodb_doc(normalized_url)



        mongo_obj = MongoWrapthfDB("tieroneurl")

        mongo_obj.thf_remove_normalized_url(normalized_url)
        logging.info('Removed document from DB.')

        # Current date for comparing the dailySeenDateCount in schema
        currentDate = date.today().strftime("%m-%d-%Y")
        #currentDate = datetime.utcnow().strftime("%m-%d-%Y")
        logging.info("currentDate")
        logging.info(currentDate)
        harvesterEventsList1 = document1["harvesterEvents"]
        harvesterEvent1 = harvesterEventsList1[0]
        metadata = harvesterEvent1["rawMetadata"]

        dailySeenDateCount1 = document1["dailySeenDateCount"]
        dailySeenDateCount2 = document2["dailySeenDateCount"]

        harvesterEventsList2 = document2["harvesterEvents"]
        harvesterEvent21 = harvesterEventsList2[0]
        harvesterEvent22 = harvesterEventsList2[1]

        # Set metadata based on the order of harvester events in the document.
        if harvesterEvent21["sourceId"] == "WWUncat":
            # {
            harvesterEvent21 = harvesterEventsList2[0]
            harvesterEvent22 = harvesterEventsList2[1]
        # }
        elif harvesterEvent21["sourceId"] == "Repper":
            # {
            harvesterEvent21 = harvesterEventsList2[1]
            harvesterEvent22 = harvesterEventsList2[0]
        # }

        metadata1 = harvesterEvent21["rawMetadata"]
        metadata2 = harvesterEvent22["rawMetadata"]

        """
                Compare all fields in the document with input data.
                New harvester event is added since the source is different.
                eventType is new for both the harveszter events,
                and dailySeenDateCount is 1 for current date for the first run and 2 for second run.
        """

        if (not original_url in document1["originalUrls"] or not original_url in document2["originalUrls"]):
            # {
            raise AssertionError("Core write API test result: FAIL, Original url not found in the original urls list.")
        # }

        self.assertEqual(document1["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document1["canonicalizedDomain"], "google.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")
        self.assertEqual(harvesterEvent1["sourceId"], "WWUncat",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent1["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata["harvester_name"], "WWUncat",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(dailySeenDateCount1[currentDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")

        self.assertEqual(document2["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document2["canonicalizedDomain"], "google.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")
        self.assertEqual(harvesterEvent21["sourceId"], "WWUncat",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent21["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata1["harvester_name"], "WWUncat",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(harvesterEvent22["sourceId"], "Repper",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent22["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata2["harvester_name"], "Repper",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(dailySeenDateCount2[currentDate], 2,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")

        logging.info("dailySeenDateCount1 is")
        logging.info(dailySeenDateCount1)

        logging.info("dailySeenDateCount2 is")
        logging.info(dailySeenDateCount2)

        logging.info("currentDate is")
        logging.info(currentDate)

        logging.info('Core write API test result - %s: PASS' % tcid)


    def test_corewrite_api_12(self):
        """
        TS-957:Tiered Harvester - URL persistance & de-duplication for Asynchronous Write(existing url- previous date) - different source.
        To test Tiered Harvester - URL persistance & de-duplication for Asynchronous Write
        with an existing url (inserted on previous date) from a different source(Customer Logs)
        """
        tcid = 'C12'

        logging.info("Starting Testcase : " + tcid)

        # Create the harvester object.
        hcon = HarvesterWWUncat()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        # Run the harvester.
        run_result = hobj.run_harvester('thf/wwuncat-C12a.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # })

        normalized_url = 'http://google.com/'
        original_url = 'http://google.com'

        document1 = self.__corewriteAPI_base(tcid, normalized_url)

        # Current date for comparing the dailySeenDateCount in schema
        currentDate = date.today().strftime("%m-%d-%Y")
        #currentDate = datetime.utcnow().strftime("%m-%d-%Y")
        logging.info("currentDate")
        logging.info(currentDate)

        # Previous date for comparing the dailySeenDateCount in schema
        previousDate = (date.today() - timedelta(1)).strftime("%m-%d-%Y")
        #previousDate = (datetime.utcnow()-timedelta(1)).strftime("%m-%d-%Y")
        logging.info("previousDate")
        logging.info(previousDate)
        dailySeenDateCount = {previousDate: 1}
        document1["dailySeenDateCount"] = dailySeenDateCount

        # THF properties file path.
        #thf_properties_file='/home/toolguy/tsa/thf/tieredharvest.properties'

        #db_obj= DbConnection(thf_properties_file)

        # Update dailySeenDateCount with previous date and count 1.
        #id_returned=db_obj.update_mongodb_doc(document1)
        mongo_obj = MongoWrapthfDB("tieroneurl")
        id_returned = mongo_obj.save_document(document1)


        # Create the harvester object.
        hcon = HarvesterRepper()
        hobj = Harvester(hcon)

        # Clean working directory before running harvester.
        hobj.clean_working_dir()

        #Re-running harvester.
        run_result = hobj.run_harvester('thf/repper-C12b.txt')

        if run_result:
            # {
            logging.info('Harvester Test Result -%s: PASS' % tcid)
        # }
        else:
            # {
            logging.error('Harvester Test Result -%s: FAIL' % tcid)
            raise AssertionError("Harvester Test Result: FAIL")
        # }

        document2 = self.__corewriteAPI_base(tcid, normalized_url)

        # Check whether the document is null.
        if document1 is None or document2 is None:
            # {
            logging.error('Document not found in DB- Test result - %s: FAIL' % tcid)
            raise AssertionError("Core write API test result: FAIL")
        # }

        # Remove the document from DB
        #db_obj= DbConnection(thf_properties_file)
        #db_obj.remove_mongodb_doc(normalized_url)

        mongo_obj = MongoWrapthfDB("tieroneurl")

        mongo_obj.thf_remove_normalized_url(normalized_url)
        logging.info('Removed document from DB.')

        harvesterEventsList1 = document1["harvesterEvents"]
        harvesterEvent1 = harvesterEventsList1[0]
        metadata = harvesterEvent1["rawMetadata"]

        dailySeenDateCount1 = document1["dailySeenDateCount"]
        dailySeenDateCount2 = document2["dailySeenDateCount"]

        harvesterEventsList2 = document2["harvesterEvents"]
        harvesterEvent21 = harvesterEventsList2[0]
        harvesterEvent22 = harvesterEventsList2[1]

        # Set metadata based on the order of harvester events in the document.
        if harvesterEvent21["sourceId"] == "WWUncat":
            # {
            harvesterEvent21 = harvesterEventsList2[0]
            harvesterEvent22 = harvesterEventsList2[1]
        # }
        elif harvesterEvent21["sourceId"] == "Repper":
            # {
            harvesterEvent21 = harvesterEventsList2[1]
            harvesterEvent22 = harvesterEventsList2[0]
        # }

        metadata1 = harvesterEvent21["rawMetadata"]
        metadata2 = harvesterEvent22["rawMetadata"]

        """
                Compare all fields in the document with input data.
                New harvester event is added since the source is different.
                eventType is new for both the harveszter events,
                and dailySeenDateCount is 1 for previous date for the first run, and
                1 for both previous and current date for the second run.
        """

        if (not original_url in document1["originalUrls"] or not original_url in document2["originalUrls"]):
            # {
            raise AssertionError("Core write API test result: FAIL, Original url not found in the original urls list.")
        # }

        self.assertEqual(document1["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document1["canonicalizedDomain"], "google.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")
        self.assertEqual(harvesterEvent1["sourceId"], "WWUncat",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent1["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata["harvester_name"], "WWUncat",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(dailySeenDateCount1[previousDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")

        self.assertEqual(document2["className"], "com.mcafee.gti.thf.TierOneURL",
                         "Core write API test result: FAIL, Class name mismatch.")
        self.assertEqual(document2["canonicalizedDomain"], "google.com",
                         "Core write API test result: FAIL, Canonicalized domain mismatch.")
        self.assertEqual(harvesterEvent21["sourceId"], "WWUncat",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent21["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata1["harvester_name"], "WWUncat",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")
        self.assertEqual(harvesterEvent22["sourceId"], "Repper",
                         "Core write API test result: FAIL, Harvester Event Source ID mismatch.")
        self.assertEqual(harvesterEvent22["eventType"], "New",
                         "Core write API test result: FAIL, Harvester Event type mismatch.")
        self.assertEqual(metadata2["harvester_name"], "Repper",
                         "Core write API test result: FAIL, Metadata- harvester_name field mismatch.")

        self.assertEqual(dailySeenDateCount2[previousDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")
        self.assertEqual(dailySeenDateCount2[currentDate], 1,
                         "Core write API test result: FAIL, dailySeenDateCount mismatch.")

        logging.info("dailySeenDateCount is")
        logging.info(dailySeenDateCount)

        logging.info("currentDate is")
        logging.info(currentDate)

        logging.info('Core write API test result - %s: PASS' % tcid)


