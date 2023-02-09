"""
==================================
Pre Build Execution test steps
==================================
"""
__author__ = 'Anurag'
from lib.exceptions import TestFailure
from lib.sfimport import sfimport


from framework.test import SandboxedTest
from framework.ddt import testgen_data, testgen_file, tsadriver, testdata
import logging
import pprint
import runtime

@tsadriver
class SFImport(SandboxedTest):
    def test_sfimport_01(self):
        data_list = runtime.e2e.csv["sfimport_01"]

        #insert all urls with first category
        for data_item in data_list:
            sfi_obj = sfimport()
            sfi_result = sfi_obj.insert([data_item["url"]], data_item["Category"].split(",")[0], ins_type='new')
            data_item["_url_dict"] = sfi_obj.url_dict()
            if not ((sfi_result["Total_Successful"] == 1) and (sfi_result["Total_Canon_Errors"] == 0)
                    and (sfi_result["Total_Errors"] == 0) and (sfi_result["URLs Added_to_List"] == 1)
                    and (sfi_result["URLs already_OK"] == 0)):
                raise TestFailure('Result Mismatch in SFIMPORT log')


        #append urls with rest of category
        for data_item in data_list:
            tmp_cats = data_item["Category"].split(",")[1:]
            for cat in tmp_cats:
                sfi_result = sfi_obj.append_category([data_item["url"]], cat)
            if not (sfi_result["Total_Successful"] == 1) and (sfi_result["Total_Canon_Errors"] == 0) \
                    and (sfi_result["Total_Errors"] == 0):
                raise TestFailure('Result Mismatch in SFIMPORT log')


        logging.warning(pprint.pformat(data_list))
