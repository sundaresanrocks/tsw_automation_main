"""
Tests for Alexa and Quantcast Top Sites based on TLD
__author__ : "Anurag"
"""

import logging
import datetime

import runtime
from framework.test import SandboxedTest
from lib.db.mongowrap import MongoWrap
from lib.exceptions import TestFailure
from lib.exceptions import ExecutionError
from lib.properties.sshprop import SSHProperties
from prevalence.lib.topsite_parser import TopSiteParser


#TODO: Move these to envcon once the env for prevalence is decided.
bin_dir = '/opt/sftools/bin/'
conf_dir = '/opt/sftools/conf/'
start_popular_scrapper = bin_dir + 'run_PopularSitesUrlScraper.sh'
scraper_prop = conf_dir + 'PopularSitesUrlScraper.properties'
mongo_db = 'db_top_site'
mongo_collection = 'top_site'
data_location = runtime.data_path + '/tsw/prevalence/'
host = 'tsqaap04.wsrlab'

#Sanity Tests
'''
1. Check if run_PopularSitesUrlScraper.sh exists
2. Check in properties file for data location property
3. Check if the data_location exists
4. Check if writetomongo property is true
'''
class TLDTopSitesSanity(SandboxedTest):

    @classmethod
    def setUpClass(cls):
        """
        Creates ssh and mongo connections that can be used by all tests
        """
        cls.ssh_obj = runtime.get_ssh(host,'toolguy')
        cls.mongo_obj = MongoWrap(collection=mongo_collection,dbname=mongo_db)

    def test_01(self):
        """
        Checks if popular URL scrapper executable exists
        """
        if not self.ssh_obj._file_exists(start_popular_scrapper):
            raise TestFailure('%s does not exist' % start_popular_scrapper)

    def test_02(self):
        """Check if specified DB and collection exist in Mongo"""
        err_list = []
        if not self.mongo_obj.db_exists():
            err_list.append('%s DB does not exist in %s' % (mongo_db, runtime.Mongo.host))
        if not self.mongo_obj.collection_exists():
            err_list.append('%s Collection does not exist in %s DB' % (mongo_collection,mongo_db))
        if len(err_list) != 0:
            raise TestFailure('\n'.join(err_list))

    def test_03(self):
        """
        Checks if all valid properties exists in Scrapper properties file
        """
        err_list = []
        prop_obj = SSHProperties(self.ssh_obj, scraper_prop)
        if "TLD" not in prop_obj.pobj:
            err_list.append('Property TLD does not exist in %s' % scraper_prop)
        if "outputdir" not in prop_obj.pobj:
            err_list.append('Property Output Directory does not exist in %s' % scraper_prop)
        if "writeToMongo" not in prop_obj.pobj:
            err_list.append('Property writeToMongo does not exist in %s' % scraper_prop)
        if "writeToMongo" in prop_obj.pobj:
            if prop_obj.pobj["writeToMongo"] == 'false':
                logging.error('Write to Mongo is set to False.Please enable it')
        if len(err_list) != 0:
            raise TestFailure('\n'.join(err_list))

"""
====================
Functional Tests
====================
"""
class TLDTopSitesFunc(SandboxedTest):

    @classmethod
    def setUpClass(cls):
        """
        Creates ssh and Mongo connections that can be used by all tests
        """
        cls.ssh_obj = runtime.get_ssh(host,'toolguy')
        cls.mongo_obj = MongoWrap(collection=mongo_collection,dbname=mongo_db)

    def setUp(self):
        """
        setUp must call Parent's setUp first.
        Empties Mongo collection for every test
        """
        SandboxedTest.setUp(self)
        logging.info("Clearing the mongoDB")
        self.mongo_obj.delete_all_data_in_collection()

    def test_01(self):
        """Scrapper for URLs both in alexa and quantcast"""
        _id = 'e65af7bec55ab7e7ffab20752f70496414bb6bb4e555382e431b882687e02b90' # url = *://XE.COM
        run_scrapper = '%s %s' % (start_popular_scrapper, data_location+'/tld_01/PopularUrlScrapper.properties')
        stdout, stderr = self.ssh_obj.execute(run_scrapper)
        logging.info(stdout)
        if len(stderr) != 0:
            if 'ERROR' in stderr or 'Exception' in stderr:
                raise ExecutionError(stderr)
        lib_obj = TopSiteParser(mongo_db, mongo_collection)
        expected_docs = lib_obj.topsite_dict_from_csv(data_location+'tld_01/test_lu.csv')
        mongo_docs    = lib_obj.topsite_dict_from_mongo()
        for key in list(mongo_docs.keys()):
            if key != _id:
                mongo_docs.pop(key)
        lib_obj.compare_topsite_dicts(mongo_docs,expected_docs)

    def test_02(self):
        """
        Check if scrapper creates a file for lu
        Test case need to be changed if file names are changed
        """
        err_list = []
        #forming alexa and quancast file name
        tld = 'lu'
        cur_date = datetime.datetime.now()
        year = str(cur_date.year)
        month = str(cur_date.month)
        if len(month) == 1:
            month = '0' + month
        day = str(cur_date.day)
        if len(day) == 1:
            day = '0' + day
        # get location from properties file
        prop_obj = SSHProperties(self.ssh_obj, data_location+'/tld_01/PopularUrlScrapper.properties')
        tld_data_location = prop_obj['outputdir']
        quant_file_name = tld_data_location + '/' + year+month+day+ '_' + tld + '_quantcast.txt'
        alexa_file_name = tld_data_location + '/' + year+month+day + '_' + tld + '_alexatopnation.txt'
        run_scrapper = '%s %s' % (start_popular_scrapper, data_location+'/tld_01/PopularUrlScrapper.properties')
        stdout, stderr = self.ssh_obj.execute(run_scrapper)
        logging.info(stdout)
        if len(stderr) != 0:
            if 'ERROR' in stderr or 'Exception' in stderr:
                raise ExecutionError(stderr)
        if not self.ssh_obj._file_exists(alexa_file_name):
            err_list.append('%s is not created after Scrapper run' % alexa_file_name)
        if not self.ssh_obj._file_exists(quant_file_name):
            err_list.append('%s is not created after Scrapper run' % quant_file_name)
        if len(err_list) != 0:
            raise TestFailure('\n'.join(err_list))