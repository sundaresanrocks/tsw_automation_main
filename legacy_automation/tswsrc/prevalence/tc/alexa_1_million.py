"""
Tests for Alexa 1 Million Top Sites
"""

import logging

import runtime
from framework.test import SandboxedTest
from lib.db.mongowrap import MongoWrap
from lib.exceptions import TestFailure
from lib.exceptions import ExecutionError
from lib.properties.sshprop import SSHProperties
from prevalence.lib.topsite_parser import TopSiteParser


#TODO: Please move below assignments to envcon at later point of time
bin_dir = '/opt/sftools/bin/'
conf_dir = '/opt/sftools/conf/'
start_alexa_process = bin_dir + 'start_alexa_process.sh'
mongo_db = 'db_top_site'
mongo_collection = 'top_site'
data_location = runtime.data_path + '/tsw/prevalence/'
host = 'tsqaap04.wsrlab'

'''
====================
Sanity Test Suite
====================
'''
class Alexa1MillionSanity(SandboxedTest):

    @classmethod
    def setUpClass(cls):
        """
        Creates ssh and mongo connections that can be used by all tests
        """
        cls.ssh_obj = runtime.get_ssh(host,'toolguy')
        cls.mongo_obj = MongoWrap(collection=mongo_collection,dbname=mongo_db)

    def test_01(self):
        """Check if application.properties has db and mongo host specified as properties"""
        err_list = []
        prop_obj = SSHProperties(self.ssh_obj, conf_dir + 'application.properties')
        expected_prop = "mongodb.topsite.host"
        expected_value = runtime.Mongo.host
        if expected_value.endswith('.wsrlab'):
            expected_value = expected_value.strip('.wsrlab')
        if prop_obj.pobj[expected_prop] != expected_value:
            err_list.append('Property mismatch.Expected: %s - Actual: %s ' % (expected_value, prop_obj.pobj[expected_prop]))
        if prop_obj.pobj['mongodb.topsite.database'] != mongo_db:
            err_list.append('Property mismatch.Expected: %s - Actual: %s ' % (mongo_db, prop_obj.pobj['mongodb.topsite.database']))
        if len(err_list) != 0:
            raise TestFailure('\n'.join(err_list))

    def test_02(self):
        """Check if specified DB and collection exist in Mongo"""
        err_list = []
        if not self.mongo_obj.db_exists():
            err_list.append('%s DB does not exist in %s' %(mongo_db,runtime.Mongo.host))
        if not self.mongo_obj.collection_exists():
            err_list.append('%s Collection does not exist in %s DB' % (mongo_collection,mongo_db))
        if len(err_list) != 0:
            raise TestFailure('\n'.join(err_list))

    def test_03(self):
        """Check if all scripts and directories related to ALexa top 1 million exist"""
        if not self.ssh_obj._file_exists(start_alexa_process):
            raise TestFailure('%s executable does not exist on host %s' % (start_alexa_process,host))
'''
=======================
Functional Test Suite
=======================
'''
class Alexa1MillionFunc(SandboxedTest):

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
        """Check for insertion of new URLs"""
        lib_obj = TopSiteParser(mongo_db, mongo_collection)
        self.ssh_obj.put(localpath=data_location + 'test_01/alexa_top_1000000.txt',remotepath='/data/harvesters/alexa/alexa_top_1000000.txt')
        self.ssh_obj.put(localpath=data_location + 'test_01/alexa_top_1000000_old.txt',remotepath='/data/harvesters/alexa/alexa_top_1000000_old.txt')
        stdout,stderr = self.ssh_obj.execute(start_alexa_process)
        logging.info(stdout)
        if len(stderr) != 0:
            if 'ERROR' in stderr or 'Exception' in stderr:
                raise ExecutionError(stderr)
        mongo_docs    = lib_obj.topsite_dict_from_mongo()
        expected_docs = lib_obj.topsite_dict_from_csv(data_location + 'test_01/test_01.csv')
        lib_obj.compare_topsite_dicts(mongo_docs,expected_docs)

    def test_02(self):
        """
        Check if URLS in mongo gets appended to the original List
        """
        lib_obj = TopSiteParser(mongo_db, mongo_collection)
        self.ssh_obj.put(localpath=data_location + 'test_01/alexa_top_1000000.txt',remotepath='/data/harvesters/alexa/alexa_top_1000000.txt')
        self.ssh_obj.put(localpath=data_location + 'test_01/alexa_top_1000000_old.txt',remotepath='/data/harvesters/alexa/alexa_top_1000000_old.txt')
        stdout,stderr = self.ssh_obj.execute(start_alexa_process)
        logging.info(stdout)
        if len(stderr) != 0:
            if 'ERROR' in stderr or 'Exception' in stderr:
                raise ExecutionError(stderr)
        mongo_docs    = lib_obj.topsite_dict_from_mongo()
        expected_docs = lib_obj.topsite_dict_from_csv(data_location + 'test_01/test_01.csv')
        lib_obj.compare_topsite_dicts(mongo_docs,expected_docs)
        # add a 3rd URL check if it in in mongoDB
        self.ssh_obj.put(localpath=data_location + 'test_02/alexa_top_1000000.txt',remotepath='/data/harvesters/alexa/alexa_top_1000000.txt')
        stdout,stderr = self.ssh_obj.execute(start_alexa_process)
        logging.info(stdout)
        if len(stderr) != 0:
            if 'ERROR' in stderr or 'Exception' in stderr:
                raise ExecutionError(stderr)
        mongo_docs    = lib_obj.topsite_dict_from_mongo()
        expected_docs = lib_obj.topsite_dict_from_csv(data_location + 'test_02/test_02.csv')
        lib_obj.compare_topsite_dicts(mongo_docs,expected_docs)

    def test_03(self):
        """
        Check if the Rank in Mongo gets updated if it is changed in the file
        """
        lib_obj = TopSiteParser(mongo_db, mongo_collection)
        self.ssh_obj.put(localpath=data_location + 'test_01/alexa_top_1000000.txt',remotepath='/data/harvesters/alexa/alexa_top_1000000.txt')
        self.ssh_obj.put(localpath=data_location + 'test_01/alexa_top_1000000_old.txt',remotepath='/data/harvesters/alexa/alexa_top_1000000_old.txt')
        stdout,stderr = self.ssh_obj.execute(start_alexa_process)
        logging.info(stdout)
        if len(stderr) != 0:
            if 'ERROR' in stderr or 'Exception' in stderr:
                raise ExecutionError(stderr)
        mongo_docs    = lib_obj.topsite_dict_from_mongo()
        expected_docs = lib_obj.topsite_dict_from_csv(data_location + 'test_01/test_01.csv')
        lib_obj.compare_topsite_dicts(mongo_docs,expected_docs)
        #Change rank of URLS and run alexa_process
        self.ssh_obj.put(localpath=data_location + 'test_03/alexa_top_1000000.txt',remotepath='/data/harvesters/alexa/alexa_top_1000000.txt')
        stdout,stderr = self.ssh_obj.execute(start_alexa_process)
        logging.info(stdout)
        if len(stderr) != 0:
            if 'ERROR' in stderr or 'Exception' in stderr:
                raise ExecutionError(stderr)
        mongo_docs    = lib_obj.topsite_dict_from_mongo()
        expected_docs = lib_obj.topsite_dict_from_csv(data_location + 'test_03/test_03.csv')
        lib_obj.compare_topsite_dicts(mongo_docs,expected_docs)

    def test_04(self):
        """
        Checks if dates in mongo are as expected
        """
        lib_obj = TopSiteParser(mongo_db, mongo_collection)
        self.ssh_obj.put(localpath=data_location + 'test_01/alexa_top_1000000.txt',remotepath='/data/harvesters/alexa/alexa_top_1000000.txt')
        self.ssh_obj.put(localpath=data_location + 'test_01/alexa_top_1000000_old.txt',remotepath='/data/harvesters/alexa/alexa_top_1000000_old.txt')
        stdout,stderr = self.ssh_obj.execute(start_alexa_process)
        logging.info(stdout)
        if len(stderr) != 0:
            if 'ERROR' in stderr or 'Exception' in stderr:
                raise ExecutionError(stderr)
        lib_obj.dates_check('alexa_first_seen')
