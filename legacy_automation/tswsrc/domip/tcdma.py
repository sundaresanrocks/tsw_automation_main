# import logging

#.domip.confdomip
# from lib.libdma import *
from framework.test import SandboxedTest
from domip.inpdatadma import TestDataDMA
# from libx.process import ShellExecutor
from lib.db.mongowrap import MongoWrap
from libx.utils import DictDiffer

class DMATests(SandboxedTest):
    """
    """
    @classmethod
    def setUpClass(self):
        mwrap = MongoWrap('domainz')
        mwrap.delete_all_data_in_collection()


    def test_01(self):
        """
        Run DMAClient with default configuration
        Test case ID : 	TS-895
        """
        #check if mongo db is up
        #insert data into mongo db

        test_data = TestDataDMA.test01(10)
        data_obj = TestDataDMA()
        data_obj.set_mongo_data(test_data)

        #ShellExecutor.run_wait_standalone(tsa.domip.confdomip.binfile_dma)

        #get data from mongodb
        expected_data = TestDataDMA.test01_expected()
        mwc = MongoWrap('domainz')
        mongo_data = mwc.query_one('''{'_id':'0--1.biz'}''')
        print(mongo_data)

        #verify with expected data
        diff = DictDiffer(expected_data, mongo_data)
        print((diff.partial_match()))

        if not diff.partial_match():
            raise AssertionError('TEST FAIL:')



    def test_02(self):
        """
        Second test case with single IPv4 IP data
        Test case ID : 	TS-903

        """
        #check if mongo db is up
        #insert data into mongo db

        test_data = TestDataDMA.test02(10)
        data_obj = TestDataDMA()
        data_obj.set_mongo_data(test_data)

        #ShellExecutor.run_wait_standalone(tsa.domip.confdomip.binfile_dma)

        #get data from mongodb
        expected_data = TestDataDMA.test02_expected()
        mwc = MongoWrap('domainz')
        mongo_data = mwc.query_one('''{'_id':'0-0-7.biz'}''')
        print(mongo_data)

        #verify with expected data
        diff = DictDiffer(expected_data, mongo_data)
        print((diff.partial_match()))

        if not diff.partial_match():
            raise AssertionError('TEST FAIL:')

    def test_03(self):
        """
        Third test case with single IPv6  IP data
        Test case ID : 	TS-902
        """
        #check if mongo db is up
        #insert data into mongo db

        test_data = TestDataDMA.test03(10)
        data_obj = TestDataDMA()
        data_obj.set_mongo_data(test_data)

        #ShellExecutor.run_wait_standalone(tsa.domip.confdomip.binfile_dma)

        #get data from mongodb
        expected_data = TestDataDMA.test03_expected()
        mwc = MongoWrap('domainz')
        mongo_data = mwc.query_one('''{'_id':'abutip.bi'}''')
        print(mongo_data)

        #verify with expected data
        diff = DictDiffer(expected_data, mongo_data)
        print((diff.partial_match()))

        if not diff.partial_match():
            raise AssertionError('TEST FAIL:')


   
    def test_04(self):
        """
        Fourth  test case with multiple IPv4 and IPv6 address data
        Test case ID : 	TS-906
        """
        #check if mongo db is up
        #insert data into mongo db

        test_data = TestDataDMA.test04(10)
        data_obj = TestDataDMA()
        data_obj.set_mongo_data(test_data)

        #ShellExecutor.run_wait_standalone(tsa.domip.confdomip.binfile_dma)

        #get data from mongodb
        expected_data = TestDataDMA.test04_expected()
        mwc = MongoWrap('domainz')
        mongo_data = mwc.query_one('''{'_id':'zykov.biz'}''')
        print(mongo_data)

        #verify with expected data
        diff = DictDiffer(expected_data, mongo_data)
        print((diff.partial_match()))

        if not diff.partial_match():
            raise AssertionError('TEST FAIL:')

    def test_05(self):
        """
        Fifth  test case with multiple Nameservers data
        Test case ID : 	TS-909
        """
        #check if mongo db is up
        #insert data into mongo db

        test_data = TestDataDMA.test05(10)
        data_obj = TestDataDMA()
        data_obj.set_mongo_data(test_data)

        #ShellExecutor.run_wait_standalone(tsa.domip.confdomip.binfile_dma)

        #get data from mongodb
        expected_data = TestDataDMA.test05_expected()
        mwc = MongoWrap('domainz')
        mongo_data = mwc.query_one('''{'_id':'zurmontmadison.biz'}''')
        print(mongo_data)

        #verify with expected data
        diff = DictDiffer(expected_data, mongo_data)
        print((diff.partial_match()))

        if not diff.partial_match():
            raise AssertionError('TEST FAIL:')