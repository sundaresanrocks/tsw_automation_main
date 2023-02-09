"""
=====================================
Assertion Checks for end to end tests
=====================================

Various checks for end to end test cases
* U2 database checks
* D2 database checks
* SFv4 checks
"""

import logging

from framework.test import SandboxedTest
from framework.ddt import testgen_data, tsadriver
from lib.sfv4 import SFV4CheckURL
from lib.exceptions import TestFailure, ProcessingError
from lib.db.u2_urls import U2Urls
from lib.db.d2_tables import D2
from lib.db.u2_categories import U2Categories


def u2_url_check(url, cat_short):
    #check in URLs table
    if type(cat_short) == type('str'):
        tmp = [cat_short]
        cat_short = tmp
    u2_urls = U2Urls()
    url_id = u2_urls.get_id_from_url(url)
    logging.info(url_id)
    if url_id is not None:
        u2_cat = U2Categories(urlid=url_id, u2_con=None)
        cat_from_table = u2_cat.get_cat_by_url_id()
        logging.error(cat_from_table)
        logging.error(cat_short)
        for cat in cat_short:
            for i in cat_from_table:
                if cat in i['cat_short']:
            #if cat != cat_from_table[0]['cat_short'] :
                    logging.error('Mismatch for category. Expected : %s, Found : %s ' % (cat_short, cat_from_table))


def d2_url_check(url):
    d2_obj = D2(url)
    #check in build table
    url_id = d2_obj.check_build_table()
    logging.info('%s : %s on D2.dbo.build ' % (url, url_id))
    #check in urltree table
    d2_obj.check_urltree_table()
    #check in dwaqueue table
    #d2_obj.check_dwaqueue_table()



def sfv4_url_check(url, cat_short, database):
    err_list = []
    if type(cat_short) == type('str'):
        tmp = [cat_short]
        cat_short = tmp
    elif type(cat_short) == type([]):
        for i in cat_short:
            if type(i) != type('str'):
                raise Exception('Please pass a String or a list of string for categories')
    else:
        raise Exception('Please pass a String or a list of string for categories')

    if database == 'xl':
        sfv4_obj = SFV4CheckURL('/usr2/smartfilter/build/staging/xl/sfcontrol')
    if database == 'ts':
        sfv4_obj = SFV4CheckURL('/usr2/smartfilter/build/staging/ts/tsdatabase')
    result = sfv4_obj.check_urls(url)
    if ',' in result[url]['Category']:
        cats_from_sfv4 = result[url]['Category'].split(',')
    for i in cats_from_sfv4:
        if i not in cat_short:
            err_list.append('Misatch ar category %s ' % i)
    if len(err_list) != 0:
        raise TestFailure('\n'.join(err_list))


@tsadriver
class U2DBCheck(SandboxedTest):
    """
    ==================================
    Pre Agent Execution checks
    ==================================
    U2 database is checked before Agents are executed.
    """
    @testgen_data(runtime.e2e.csv)
    def test(self, data_list):
        err_list = []
        for data_url in data_list:
            try:
                u2_url_check(data_url["url"], data_url["Category"].split(','))
            except ProcessingError as e:
                err_list.append(e.args[0])
                continue
        if err_list:
            raise TestFailure('\n'.join(err_list))



@tsadriver
class D2DBCheck(SandboxedTest):
    """
    ==================================
    Post Agent Execution checks
    ==================================
    D2 database is checked after Agents are executed.
    """
    @testgen_data(runtime.e2e.csv)
    def test(self, data_list):
        err_list = []
        for data_url in data_list:
            try:
                d2_url_check(data_url["url"])
            except ProcessingError as e:
                err_list.append(e.args[0])
        if err_list:
            raise TestFailure('\n'.join(err_list))


@tsadriver
class SFv4Check(SandboxedTest):
    """
    ==================================
    Post build assertions
    ==================================
    sfcontorl and tsdatabase file are asserted after the build process is complete
    """
    @testgen_data(runtime.e2e.csv)
    def test(self, data_list):
        err_list = []
        for data_url in data_list:
            try:
                pass
                #sfv4 chek must be added
            except ProcessingError as e:
                err_list.append(e.args[0])
        if err_list:
            raise TestFailure('\n'.join(err_list))



if __name__ == '__main__':
    __url = 'google.com'
    sfv4_url_check(__url,'sa')
    d2_url_check(__url)
    u2_url_check(__url,'sa')
