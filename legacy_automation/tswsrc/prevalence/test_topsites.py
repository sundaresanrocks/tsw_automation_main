"""
Top Sites Tests
***************
"""
from prevalence.lib.topsites import new_top_site_collection_with_index, create_top_sites_application_properties, \
    get_default_popular_url_scrapper_properties, get_top_sites_mongo_wrap_obj

__author__ = 'manoj'

import os
import pprint
import logging
import unittest
import datetime

import runtime
from framework.test import SandboxedTest
from libx.process import ShellExecutor
from lib.exceptions import TestFailure
from lib.canon import canon_in_batch
import conf.files

BIN_ALEXA_PERSIST = conf.files.SH.run_alexa_persist
BIN_TOPSITES_CLIENT = conf.files.SH.top_sites_client
BIN_POPULAR_URL_SCRAPPER = conf.files.SH.popular_url_scrapper

PROP_POPULAR_URL_SCRAPPER = '/opt/sftools/conf/PopularSitesUrlScraper.properties'

mongo_obj = get_top_sites_mongo_wrap_obj()

class SandboxedTopSites(SandboxedTest):

    def setUp(self):
        """ Deletes agents file """
        #SandboxedTest.setUp(self)
#        self.sandbox.delete_file()

    def tearDown(self):
        """Copies required files back to sandbox"""
        ####
#        self.sandbox.copy_file_to_sandbox(LOG_FILE_AGENT)
#        self.sandbox.copy_file_to_sandbox(LOCAL_AGENT_PROP_FILE)
        # self.sandbox.copy_modified_files()

        #SandboxedTest.tearDown(self)

    def run_alexa_persist(self, file_name):
        """
        Run top sites client and check in the stdout
        :param file_name:
        :return:
        """
        if not isinstance(file_name, str):
            raise TypeError('input_string must be str')
        return ShellExecutor.run_wait_standalone(BIN_ALEXA_PERSIST + ' ' + file_name)

    def run_top_sites_client(self, input_string):
        """
        Run top sites client and check in the stdout
        :param input_string:
        :return:
        """
        if not isinstance(input_string, str):
            raise TypeError('input_string must be str')
        return ShellExecutor.run_wait_standalone(BIN_TOPSITES_CLIENT + ' ' + input_string)

    def top_site_stdoe_check(self, input_string, stdoe_check_str=''):
        """
        Run top sites client and check in the stdout
        :param input_string:
        :return:
        """
        stdo, stde = self.run_top_sites_client(input_string)
        if stdoe_check_str in stdo+stde:
            return True
        return False

    def is_top_site_via_topsites_client(self, input_string):
        """
        Run True if input is a top site
        :param input_string:
        :return:
        """
        stdo, stde = self.run_top_sites_client(input_string)
        stdoe = stdo + stde
        logging.info('is top site:' + stdo.strip()[-1])
        return True if stdo.strip()[-1] == 'Y' else False

    def create_test_file(self, data_list, file_name='test.txt'):
        with open(file_name, 'w') as fpw:
            first_line = True
            for line in data_list:
                if not first_line:
                    fpw.write('\n')
                fpw.write(line)
                first_line = False

    def get_valid_top_site_dict(self, url):
        if not isinstance(url, str):
            raise TypeError('url must be string, found:%s' % type(url))
        temp_file_name = 'for_canon.txt'
        with open(temp_file_name, 'w') as fpw:
            fpw.write(url)
        url_d = canon_in_batch(temp_file_name)[url][0]
        doc = mongo_obj.query_one('{"_id":"%s"}' % url_d['sha-256'])
        return doc, url_d

    def raise_if_not_topsite(self, url):
        doc, url_d = self.get_valid_top_site_dict(url)

        if not doc:
            raise TestFailure('Hash:%s' % url_d['sha-256'] + ' not found in mongo db for url %s' % url)
        logging.info('Hash:%s' % url_d['sha-256'] + ' is in mongo db for url %s' % url)
        return doc, url_d

    def validate_alexa_data(self, doc, alexa_rank=None, alexa_tld=None, alexa_first=None, alexa_last=None,
                            first_delta_days=1, last_delta=60):
        #input value checks
        if alexa_rank:
            if not alexa_tld:
                raise ValueError('alexa_tld not set. Both alexa_rank and alexa_tld must be set.')

        #check in database
        logging.error(pprint.pformat(doc))
        if 'list_data' not in doc:
            raise TestFailure('list_data not found in mongodb doc %s' % doc)
        if alexa_rank:
            if 'in_alexa' not in doc:
                raise TestFailure('Mongo DB document "in_alexa" field %s' % doc)
            if not doc['in_alexa']:
                raise TestFailure('Mongo DB document "in_alexa" field is set to false. %s' % doc)

            list_match_b = False
            for item in doc['list_data']:
                if item['name'] == alexa_tld and item['source'] == 'alexa':
                    logging.debug('Source and Name found in list_data')
                    if item['ranking'] != alexa_rank:
                        raise ValueError('Alexa rank mismatch: Actual rank %s' % item['ranking'] +
                                         ' was not expected: %s' % alexa_rank)
                    if alexa_last:
                        if abs(item['last_seen'] - alexa_last).seconds < last_delta:
                            logging.info('actual date: %s' % item['last_seen'] + 'Expected: %s' % alexa_last +
                                         ' is within time_delta: %s' % last_delta)
                        else:
                            raise TestFailure('Last Seen delta mismatch. ' +
                                              'actual date: %s' % item['last_seen'] + 'Expected: %s' % alexa_last)

                    if alexa_first:
                        logging.warning((item['first_seen'] - alexa_first).days)
                        if abs(item['first_seen'] - alexa_first).days < first_delta_days:
                            logging.info('actual date: %s' % item['first_seen'] + 'Expected: %s' % alexa_first +
                                         ' is within time_delta: %s' % first_delta_days)
                        else:
                            raise TestFailure('First Seen delta mismatch. ' +
                                              'actual date: %s' % item['first_seen'] + 'Expected: %s' % alexa_first)
                    list_match_b = True
                break
            if not list_match_b:
                raise TestFailure('Unable to validate the list data')


    def validate_quant_data(self, doc, quant_rank=None, quant_tld=None, quant_first=None, quant_last=None,
                            first_delta_days=1, last_delta=60):
        #input validation checks
        if quant_rank:
            if not quant_tld:
                raise ValueError('quant_tld not set. Both quant_rank and quant_tld must be set.')

        #check in database
        if 'list_data' not in doc:
            raise TestFailure('list_data not found in mongodb doc %s' % doc)

        if quant_rank:
            if 'in_quant' not in doc:
                raise TestFailure('Mongo DB document "in_quant" field %s' % doc)
            if not doc['in_quant']:
                raise TestFailure('Mongo DB document "in_quant" field is set to false. %s' % doc)

            list_match_b = False
            for item in doc['list_data']:
                if item['name'] == quant_tld and item['source'] == 'quant':
                    if item['ranking'] != quant_rank:
                        raise ValueError('Alexa rank mismatch: Actual rank %s' % item['ranking'] +
                                         ' was not expected: %s' % quant_rank)
                    if quant_last:
                        if abs(item['last_seen'] - quant_last).seconds < last_delta:
                            logging.info('actual date: %s' % item['last_seen'] + 'Expected: %s' % quant_last +
                                         ' is within time_delta: %s' % last_delta)
                        else:
                            raise TestFailure('Last Seen delta mismatch. ' +
                                              'actual date: %s' % item['last_seen'] + 'Expected: %s' % quant_last)

                    if quant_first:
                        if abs(item['first_seen'] - quant_first).days < first_delta_days:
                            logging.info('actual date: %s' % item['first_seen'] + 'Expected: %s' % quant_first +
                                         ' is within time_delta: %s' % first_delta_days)
                        else:
                            raise TestFailure('First Seen delta mismatch. ' +
                                              'actual date: %s' % item['first_seen'] + 'Expected: %s' % quant_first)
                    list_match_b = True
                break
            if not list_match_b:
                raise TestFailure('Unable to validate the list data')

    def validate_tld(self, tld):
        alexa_file_name, quant_file_name = get_tld_file_name(tld)
        quant_d = canon_in_batch(quant_file_name)
        if not quant_d:
            raise TestFailure('Empty Quantcast file.')
        # logging.info(pprint.pformat(quant_d))
        for rank, url in enumerate(quant_d):
            # logging.info(rank)
            # logging.info(url)
            self.validate_quant_data(rank+1, quant_d[url][0]['sha-256'])

        alexa_d = canon_in_batch(alexa_file_name)
        if not alexa_d:
            raise TestFailure('Empty Quantcast file.')



class AlexaTop1m(SandboxedTopSites):

    @classmethod
    def setUpClass(cls):
        pass
        new_top_site_collection_with_index()

    def test_01(self):
        """AlexaTop1M: Private class A address"""
        self.create_test_file(['1,10.10.10.10'])
        stdo, stde = self.run_alexa_persist('test.txt')
        self.assertTrue('ERROR' in stdo)
        self.assertTrue('private IP' in stde)

    def test_02(self):
        """AlexaTop1M: Private class B address"""
        self.create_test_file(['1,172.16.10.10'])
        stdo, stde = self.run_alexa_persist('test.txt')
        self.assertTrue('ERROR' in stdo)
        self.assertTrue('private IP' in stde)

    def test_03(self):
        """AlexaTop1M: Private class C address"""
        self.create_test_file(['1,192.168.10.10'])
        stdo, stde = self.run_alexa_persist('test.txt')
        self.assertTrue('ERROR' in stdo)
        self.assertTrue('private IP' in stde)

    def test_04(self):
        """AlexaTop1M: Loopback address"""
        self.create_test_file(['1,localhost'])
        stdo, stde = self.run_alexa_persist('test.txt')
        self.assertTrue('ERROR' in stdo)
        self.assertTrue('unrecognized TLD' in stde)

    def test_05(self):
        """AlexaTop1M: Short valid domains"""
        data_l = ['1,www1.de', '2,www3.jp']
        self.create_test_file(data_l)
        stdo, stde = self.run_alexa_persist('test.txt')
        self.assertFalse('ERROR' in stdo)
        # self.assertTrue('unrecognized TLD' in stde)
        self.raise_if_not_topsite('www1.de')
        self.raise_if_not_topsite('www3.jp')

    def test_06(self):
        """AlexaTop1M: Valid IP address in csv file"""
        data_l = ['1,http://123.123.123.123/']
        self.create_test_file(data_l)
        stdo, stde = self.run_alexa_persist('test.txt')
        self.assertFalse('ERROR' in stdo)
        # self.assertTrue('unrecognized TLD' in stde)
        self.raise_if_not_topsite('http://123.123.123.123/')

    def test_07(self):
        """AlexaTop1M: Invalid IP address in csv file"""
        data_l = ['1,235.148.125.357']
        self.create_test_file(data_l)
        stdo, stde = self.run_alexa_persist('test.txt')
        self.assertTrue('ERROR' in stdo)
        logging.error(stde)
        self.assertTrue('Invalid domain name' in stde)

    def test_08(self):
        """Sanity: Check alexa start process shell script"""
        self.failIf(not os.path.isfile(BIN_ALEXA_PERSIST))

    def test_09(self):
        """Alexa: Top 1 million URLs on empty DB"""
        raise unittest.SkipTest('Takes long time. See separate script.')

    def test_10(self):
        """Sanity: alexa empty arguments"""
        stdo, stde = self.run_alexa_persist('')
        self.assertTrue('must specify alexa input file' in stdo)

    def test_11(self):
        """
        Alexa check in mongo db
        :return:
        """
        now = datetime.datetime.utcnow()
        data_l = ['1,google.com', '2,yahoo.com', '3,three.com', '4,four.com', '5,five.com']
        self.create_test_file(data_l)
        stdo, stde = self.run_alexa_persist('test.txt')
        self.assertFalse('ERROR' in stdo)

        data = ['google.com', 'yahoo.com']
        logging.warning(now)
        for rank, url in enumerate(data, 1):
            doc, url_d = self.raise_if_not_topsite(url)
            self.validate_alexa_data(doc, alexa_rank=rank, alexa_tld='top_1m', alexa_first=now, alexa_last=now)

    def test_12(self):
        """
        Alexa top 1m: Update rank on existing URL
        :return:
        """
        data_l = ['100,google-100.com']
        self.create_test_file(data_l, '100.txt')
        stdo, stde = self.run_alexa_persist('100.txt')
        self.assertFalse('ERROR' in stdo)

        data_l = ['10,google-100.com']
        self.create_test_file(data_l, '10.txt')
        stdo, stde = self.run_alexa_persist('10.txt')
        self.assertFalse('ERROR' in stdo)

        url = 'google-100.com'
        doc, url_d = self.raise_if_not_topsite(url)
        self.validate_alexa_data(doc, alexa_rank=10, alexa_tld='top_1m')

    def test_13(self):
        """
        Alexa top 1m: Update date on existing URL. Last seen must be updated with new one.
        :return:
        """
        ## Run the alexa process for current date
        url = 'old-date.com'
        old_date_delta = 10
        data_l = ['1,%s' % url]
        self.create_test_file(data_l, 'old-date.txt')
        stdo, stde = self.run_alexa_persist('old-date.txt')
        self.assertFalse('ERROR' in stdo)

        ## Modify the date with old date and update the mongo database
        doc, url_d = self.get_valid_top_site_dict(url)
        old_date = datetime.datetime.utcnow() - datetime.timedelta(old_date_delta)
        doc['list_data'][0]['last_seen'] = old_date
        doc['list_data'][0]['first_seen'] = old_date
        doc['alexa_first_seen'] = old_date
        doc['alexa_last_seen'] = old_date
        logging.critical(pprint.pformat(doc))
        mongo_obj.get_collection_obj().update({'_id': url_d['sha-256']}, doc, True)

        ## Rerun the alexa process
        stdo, stde = self.run_alexa_persist('old-date.txt')
        self.assertFalse('ERROR' in stdo)
        new_doc, url_d = self.get_valid_top_site_dict(url)

        ## validate for current date. Must throw error
        logging.debug(pprint.pformat(new_doc))
        now = datetime.datetime.utcnow()
        self.validate_alexa_data(doc, alexa_rank=1, alexa_tld='top_1m', alexa_first=now,
                                 first_delta_days=old_date_delta+2)
        logging.warning((new_doc['list_data'][0]['first_seen'] - old_date).seconds)
        logging.critical((new_doc['list_data'][0]['last_seen'] - old_date).seconds != 0)
        if (new_doc['list_data'][0]['first_seen'] - old_date).seconds != 0 or \
            (new_doc['list_data'][0]['last_seen'] - old_date).seconds != 0 :
            raise TestFailure('Error with first seen dates')
        if new_doc['alexa_last_seen'] - old_date == 0 or new_doc['list_data'][0]['last_seen'] - old_date == 0:
            raise TestFailure('Error with last seen dates')

    def test_14(self):
        """
        Alexa top 1m: Check alexa_first_seen and alexa_last_seen dates
        :return:
        """
        ## Run the alexa process for current date
        url = 'old-date.com'
        old_date_delta = 10
        data_l = ['1,%s' % url]
        self.create_test_file(data_l, 'old-date.txt')
        stdo, stde = self.run_alexa_persist('old-date.txt')
        self.assertFalse('ERROR' in stdo)

        ## Modify the date with old date and update the mongo database
        doc, url_d = self.get_valid_top_site_dict(url)
        old_date = datetime.datetime.utcnow() - datetime.timedelta(old_date_delta)
        doc['alexa_first_seen'] = old_date
        doc['alexa_last_seen'] = old_date
        logging.debug(pprint.pformat(doc))
        mongo_obj.get_collection_obj().update({'_id': url_d['sha-256']}, doc, True)

        ## Rerun the alexa process
        stdo, stde = self.run_alexa_persist('old-date.txt')
        self.assertFalse('ERROR' in stdo)
        new_doc, url_d = self.get_valid_top_site_dict(url)

        ## validate for current date. Must throw error
        logging.debug(pprint.pformat(new_doc))
        now = datetime.datetime.utcnow()
        self.validate_alexa_data(doc, alexa_rank=1, alexa_tld='top_1m', alexa_first=now,
                                 first_delta_days=old_date_delta+2)
        if new_doc['alexa_first_seen'] - old_date == 0:
            raise TestFailure('Error with first seen dates')
        if new_doc['alexa_last_seen'] - old_date == 0:
            raise TestFailure('Error with last seen dates')


class PopularUrlScrapper(SandboxedTopSites):
    """Tests relating to Popular URL Scrapper"""

    @classmethod
    def setUpClass(cls):
        tld_list = ['lu']
        create_top_sites_application_properties(True)
        collection_obj = new_top_site_collection_with_index()
        prop = get_default_popular_url_scrapper_properties(tld_list, 'PopularUrlScrapper.properties')

        run_pop_url_scrapper(tld_list)

        for tld in tld_list:
            SandboxedTopSites.validate_tld(tld)



    def test_01(self):
        """Sanity: Check quancast shell script"""
        self.failIf(not os.path.isfile(BIN_POPULAR_URL_SCRAPPER))

    def test_02(self):
        """Check in_alexa field"""
        pop_url_prop = get_default_popular_url_scrapper_properties()
        with open(PROP_POPULAR_URL_SCRAPPER, 'w') as fpw:
            pop_url_prop.store(fpw)


    def test_03(self):
        """Check in_Quancast field"""
        raise NotImplementedError

    def test_04(self):
        """PopularSites: valid tlds"""
        raise NotImplementedError

    def test_05(self):
        """PopularSites: invalid tlds"""
        raise NotImplementedError

    def test_06(self):
        """PopularSites: No tlds"""
        raise NotImplementedError

    def test_07(self):
        """PopularSites: Too much tlds"""
        raise unittest.SkipTest('NA')

    def test_08(self):
        """PopularSites: run PSUS with writeToMongo=true"""
        raise NotImplementedError

    def test_09(self):
        """PopularSites: run PSUS with writeToMongo=false"""
        tld_list = ['lu']
        create_top_sites_application_properties(write_file_bool=True)
        collection_obj = new_top_site_collection_with_index()

        prop = get_default_popular_url_scrapper_properties(tld_list)
        # prop[write]
        with open('PopularUrlScrapper.properties', 'w') as fpw:
            prop.store(fpw)
        run_pop_url_scrapper(tld_list)

        for tld in tld_list:
            self.validate_tld(tld)

    def test_10(self):
        """PopularSites: alexa/quantcast_first_seen: data updating properly"""
        tld_list = ['lu']
        create_top_sites_application_properties(write_file_bool=True)
        collection_obj = new_top_site_collection_with_index()

        prop = get_default_popular_url_scrapper_properties(tld_list)
        # prop[write]
        with open('PopularUrlScrapper.properties', 'w') as fpw:
            prop.store(fpw)
        run_pop_url_scrapper(tld_list)

        for tld in tld_list:
            self.validate_tld(tld)


    def test_11(self):
        """PopularSites: alexa/quantcast_last_seen: data updating properly"""
        raise NotImplementedError

    def test_12(self):
        """PopularSites: Run for all TLDs"""
        raise NotImplementedError


class TopSitesClient(SandboxedTopSites):
    """Tests relating to Top Sites client"""

    @classmethod
    def setUpClass(cls):
        """Intialize top sites client database setup"""
        new_top_site_collection_with_index()
        urls = ['google.com', 'amazon.com', 'Schloß.com', 'http://www.w3schools.com/tags/ref_urlencode.asp',
                'http://παράδειγμα.δοκιμή','http://пример.испытание', 'dummy.com']
        cls.create_test_file(None, ['%s,%s' % (numb, url) for numb, url in enumerate(urls, 1)])
        create_top_sites_application_properties(True)
        cls.run_alexa_persist(None, 'test.txt')


    def test_01(self):
        """TopSiteClient: No Arguments"""
        bool_value = self.top_site_stdoe_check('', 'Please provide a file, a url, or cl hash to look up.')
        self.assertTrue(bool_value)

    def test_02(self):
        """TopSiteClient: correct CL Hash"""
        bool_value = self.is_top_site_via_topsites_client('0X012E8C6AFCD2FD3FADF669A6')
        self.assertTrue(bool_value)

    def test_03(self):
        """TopSiteClient: wrong CL Hash"""
        bool_value = self.is_top_site_via_topsites_client('0X012E8C6AFCD2FD3FADF669A2')
        self.assertFalse(bool_value)

    def test_04(self):
        """TopSiteClient: Very Long CL Hash"""
        bool_value = self.is_top_site_via_topsites_client('0X012E8C6AFCD2FD3FADF669A20012E8C6AFCD2FD3FADF669A2')
        self.assertFalse(bool_value)

    def test_05(self):
        """TopSiteClient: correct URL"""
        bool_value = self.is_top_site_via_topsites_client('www.google.com')
        self.assertTrue(bool_value)

    def test_06(self):
        """TopSiteClient: wrong URL"""
        bool_value = self.is_top_site_via_topsites_client('http://naskfjiasdofnsdk.com')
        self.assertFalse(bool_value)

    def test_07(self):
        """TopSiteClient: very big URL"""
        bool_value = self.is_top_site_via_topsites_client('http://dbcjdscudscjsdnhciosdnckdsnvcpoidncvkdsnvkdsnkicxjviosdvfksdnkdsn')
        self.assertFalse(bool_value)

    def test_08(self):
        """TopSiteClient: URL in other language"""
        bool_value = self.is_top_site_via_topsites_client('http://παράδειγμα.δοκιμή')
        self.assertTrue(bool_value)

    def test_09(self):
        """TopSiteClient: subdomains for same domain"""
        data = ["http://google.com", "http://www.google.com", "www.google.com", "google.com/", "google.com"]
        err_bool = False
        for url in data:
            if not self.is_top_site_via_topsites_client(url):
                err_bool = True

        self.assertFalse(err_bool)

    def test_10(self):
        """TopSiteClient: URL in other encoading"""
        raise unittest.SkipTest('NA')

    def test_11(self):
        """TopSiteClient: URL with querystring and fragments"""
        bool_value = self.is_top_site_via_topsites_client('http://www.w3schools.com/tags/ref_urlencode.asp')
        logging.error('Return value = %s' % str(bool_value))
        self.assertTrue(bool_value)

    def test_12(self):
        """TopSiteClient: some correct and incorrfect urls in File"""
        with open('test.txt', 'w') as fpw:
            fpw.write('google.com\nnotxxadsfadfafadsfadf.com\namazon.com')
        self.run_top_sites_client('test.txt > ./stdo.log')
        result = None
        with open('stdo.log') as fpr:
            lines = fpr.readlines()
            logging.warning(lines)
            if lines[1].strip()[-1] == 'Y' and lines[2].strip()[-1] == 'N' and lines[3].strip()[-1] == 'Y':
                result = True
        self.assertTrue(result)

    def test_13(self):
        """TopSiteClient: urls in File with gaps"""
        with open('test.txt', 'w') as fpw:
            fpw.write('google.com\n\namazon.com')
        result = self.top_site_stdoe_check('test.txt', 'Error with client')
        self.assertTrue(result)

    def test_14(self):
        """TopSiteClient: too many urls/clhashes in File (stress>10k)"""
        data_file = runtime.data_path + '/tsw/prevalence/10k_urls.txt'
        logging.info('Data File: %s' % data_file)
        self.run_top_sites_client(data_file + ' > ./stdo.log')
        result = None
        with open('stdo.log') as fpr:
            lines = len(fpr.readlines())
            logging.info('Total lines: %s' % lines)
            if lines == 10001:
                result = True
        self.assertTrue(result)


def run_pop_url_scrapper(tld_list, prop_file='PopularUrlScrapper.properties'):
    stdo, stde = ShellExecutor.run_wait_standalone(BIN_POPULAR_URL_SCRAPPER + ' ' + prop_file)
    if len(stde) != 0:
        if 'ERROR' in stde or 'Exception' in stde:
            raise Exception(stde)
    errors = []
    for tld in tld_list:
        alexa_file_name, quant_file_name = get_tld_file_name(tld)
        if not os.path.isfile(quant_file_name):
            errors.append('%s is not created after Scrapper run' % quant_file_name)
        if not os.path.isfile(alexa_file_name):
            errors.append('%s is not created after Scrapper run' % alexa_file_name)
    if errors:
        raise TestFailure('Errors: %s' % '\n'.join(errors))

def check_quantcast_url(rank, sha_256):
    err_no_url = []
    # mongo_obj = get_top_sites_mongo_wrap_obj()
    doc = mongo_obj.query_one('{"_id":"%s"}' % sha_256)

    if not doc:
        raise TestFailure('URL not found for hash %s' % sha_256)

    key = 'in_quantcast'
    has_key = key in doc
    if not (key in doc and doc[key]):
        raise TestFailure('Key in_quantcast not found')


def get_tld_file_name(tld, cur_date=datetime.datetime.now()):
    quant_file_name = ''
    alexa_file_name = ''
    year = str(cur_date.year)
    month = str(cur_date.month)
    if len(month) == 1:
        month = '0' + month
    day = str(cur_date.day)
    if len(day) == 1:
        day = '0' + day

    quant_file_name = year+month+day + '_' + tld + '_quantcast.txt'
    alexa_file_name = year+month+day + '_' + tld + '_alexatopnation.txt'

    return alexa_file_name, quant_file_name


def test_prop():
    tld_list = ['lu']
    create_top_sites_application_properties(True)
    collection_obj = new_top_site_collection_with_index()
    prop = get_default_popular_url_scrapper_properties(tld_list)
    with open('PoplarUrlScrapper.properties', 'w') as fpw:
        prop.store(fpw)

    with open('PoplarUrlScrapper.properties', 'w') as fpw:
        prop.store(fpw)

    # run_pop_url_scrapper(tld_list)

    for tld in tld_list:
        SandboxedTopSites.validate_tld(tld)

        # logging.error(q_dict)
        # logging.error(a_dict)

# logging.error(pprint.pformat(canon_in_batch('luq1')))
# test_prop()
