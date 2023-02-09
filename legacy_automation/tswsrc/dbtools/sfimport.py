import time
import logging

from lib.sfimport import sfimport
from lib.exceptions import TestFailure
from framework.test import SandboxedTest
from lib.db.mssql import TsMsSqlWrap
from dbtools.agents import Agents

# from libx.vm import get_snapshot_wrapper
import runtime


class SfimportTestCases(SandboxedTest):
    """
    SFIMPORT TestCases
    """
    @classmethod
    def setUpClass(cls):

        ##  Setting Minimal DB Setting in localhost
        # DB_vm_warp = get_snapshot_wrapper(runtime.DB.vm_name)
        # DB_vm_warp.revert(runtime.DB.vm_snap)

        cls.sql_obj = TsMsSqlWrap('U2')

    #1
    def test_01(self):
        """
        TS-198:SFIMPORT: Insert Requested Urls into the database using sfimport
        """
        url =  "*://" + str(time.time()) + ".COM"
        urls = [url]
        cat = """ms"""
        obj=sfimport()
        sfimportResult = obj.append_category(urls,cat)
        url_dict = obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure('Errors found in log')
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if((url_from_table[0])['url']).lower() !=  url.lower() :
                # logging.warning((url_from_table[0])['url'])
                raise TestFailure('URL %s  not present URLs table' % (url_from_table[0])['url'] )
     #2
    def test_02(self):
        """
        TS-1399:SFIMPORT:Update category of urls in text file from ms to ph
        """
        url =  "*://" + str(time.time()) + ".COM"
        urls = [url]
        cat = """ms"""
        new_cat = """ph"""
        obj=sfimport()
        sfimportResult = obj.append_category(urls,cat)
        url_dict = obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure('Errors found in log')
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if ((url_from_table[0])['url']).lower() !=  url.lower():
                logging.error((url_from_table[0])['url'])
                raise TestFailure('URL %s  not present URLs table' % (url_from_table[0])['url'] )

        up_sfimportResult = obj.modify(urls,new_cat)
        logging.debug("Total_Successful :  %s"%(up_sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(up_sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(up_sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not (up_sfimportResult["Total_Successful"] == len(urls)) and (up_sfimportResult["Total_Canon_Errors"] == 0) and (up_sfimportResult["Total_Errors"] == 0):
            raise TestFailure('Errors found in log')
        for key in list(url_dict.keys()):
            url_cat = self.sql_obj.get_select_data('select * from u2.dbo.categories where url_id='+key)
            if ((url_cat[0])['cat_short']) !=  'ph' :
                raise TestFailure('URL category is not "ph" ')

     #3
    def test_03(self):
        """
        TS-1400:SFIMPORT:Delete URLs from database by delete option
        """
        url =  "*://" + str(time.time()) + ".COM"
        urls = [url]
        cat = """ms"""
        obj=sfimport()
        sfimportResult = obj.append_category(urls,cat)
        url_dict = obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not (sfimportResult["Total_Successful"] == len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure('Errors found in log')
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            self.sql_obj.execute_sql_commit('update u2.dbo.queue set priority=99999 where url_id='+key)
            if ((url_from_table[0])['url']).lower() !=  url.lower():
                logging.error((url_from_table[0])['url'])
                raise TestFailure('URL %s  not present URLs table' % (url_from_table[0])['url'] )

        del_sfimportResult = obj.delete_category(urls)
        logging.debug("Total_Successful :  %s"%(del_sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(del_sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(del_sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not (del_sfimportResult["Total_Successful"] == len(urls)) and (del_sfimportResult["Total_Canon_Errors"] == 0) and (del_sfimportResult["Total_Errors"] == 0):
            raise TestFailure
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -n 10 -D",output_file='anurag.txt')
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if len(url_from_table) != 0:
                logging.error(url_from_table)
                raise TestFailure('URLs not removed from DB even after TMAN run')

    def test_04(self):
        """
        TS-414:SFIMPORT : Import CHAMP format file for appending new category to a URL.
        """
        cat = """ms"""
        test_file = runtime.data_path+'/sfimport/sfimport_CHAMP_format_file.txt'
        obj=sfimport(file_type='c')
        sfimportResult = obj.append_category(test_file,cat)
        url_dict = obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        if not (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if ((url_from_table[0])['url']).lower() !=  '*://spamdavid.com' and ((url_from_table[0])['url']).lower() != '*://spamkohn.com' and ((url_from_table[0])['url']).lower() != '*://spamalan.com' and ((url_from_table[0])['url']).lower() != '*://spamderhaag.com':
                logging.error((url_from_table[0])['url'])
                raise TestFailure('URL %s  not present URLs table' % (url_from_table[0])['url'] )
        #5
    def test_05(self):
        """
        TS-416:SFIMPORT : Import CHAMP format file for removing old categories and append new categories to a url.
        """
        cat = """ph"""
        test_file = runtime.data_path+'/sfimport/sfimport_CHAMP_format_file.txt'
        obj=sfimport(file_type='c')

        sfimportResult = obj.modify(test_file,cat)
        url_dict = obj.url_dict()
        if sfimportResult is None:
                raise TestFailure
        else:
            logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
            logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
            logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
            if not (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
                logging.error ("Error in processing atleast one URL in the file")
                raise TestFailure
        for key in list(url_dict.keys()):
            url_cat = self.sql_obj.get_select_data('select * from u2.dbo.categories where url_id='+key)
            if ((url_cat[0])['cat_short']) !=  'ph' :
                raise TestFailure('URL category is not "ph" ')
          #6
    def test_06(self):
        """
        TS-415:SFIMPORT : Import CHAMP format file for deleting categories and url from database.
        """
        test_file = runtime.data_path+'/sfimport/sfimport_CHAMP_format_file.txt'
        sfimport_obj=sfimport(file_type='c')
        sfimportResult = sfimport_obj.delete_category(test_file)
        url_dict = sfimport_obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        if not (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -n 10 -D",output_file='anurag.txt')
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if len(url_from_table) != 0:
                logging.error(url_from_table)
                raise TestFailure('URLs not removed from DB even after TMAN run')
       #7
    def test_07(self):
        """
        TS-417:SFIMPORT : Import sites format file for appending new category to a URL.
        """
        cat = """ms"""
        test_file = runtime.data_path+'/sfimport/sfimport_SITES_format_file.txt'
        sfimport_obj=sfimport(file_type='s')
        sfimportResult = sfimport_obj.append_category(test_file,cat)
        url_dict = sfimport_obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        if not (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if ((url_from_table[0])['url']).lower() !=  '*://angelfire.com' and ((url_from_table[0])['url']).lower() != '*://about.com' and ((url_from_table[0])['url']).lower() != '*://altavista.com':
                logging.error((url_from_table[0])['url'])
                raise TestFailure('URL %s  not present URLs table' % (url_from_table[0])['url'] )
       #8
    def test_08(self):
        """
        TS-419:SFIMPORT : Import sites format file for removing old categories and append new categroies to a url.
        """
        cat = """ps"""
        test_file = runtime.data_path+'/sfimport/sfimport_SITES_format_file.txt'
        sfimport_obj=sfimport(file_type='s')
        sfimportResult = sfimport_obj.modify(test_file,cat)
        url_dict = sfimport_obj.url_dict()
        if sfimportResult is None:
            logging.error("updateCategorySFImport_file function is unable to update category of URLs")
            raise TestFailure
        else:
            logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
            logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
            logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
            if not (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
                raise TestFailure
        for key in list(url_dict.keys()):
            url_cat = self.sql_obj.get_select_data('select * from u2.dbo.categories where url_id='+key)
            if ((url_cat[0])['cat_short']) !=  'ps' :
                raise TestFailure('URL category is not "ps" ')
      #9
    def test_09(self):
        """
        TS-418:SFIMPORT : Import sites format file for deleting categories and url from database.
        """
        test_file = runtime.data_path+'/sfimport/sfimport_SITES_format_file.txt'
        sfimport_obj=sfimport(file_type='s')
        sfimportResult = sfimport_obj.delete_category(test_file)
        url_dict = sfimport_obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        if not (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -n 10 -D",output_file='anurag.txt')
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if len(url_from_table) != 0:
                logging.error(url_from_table)
                raise TestFailure('URLs not removed from DB even after TMAN run')
      #10
    def test_10(self):
        """
        TS-420:SFIMPORT : Import urls format file for appending new category to a URL.
        """
        cat = """ms"""
        test_file = runtime.data_path+'/sfimport/sfimport_URLS_format_file.txt'
        sfimport_obj=sfimport(file_type='u')
        sfimportResult = sfimport_obj.append_category(test_file,cat)
        url_dict = sfimport_obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        if not (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if ((url_from_table[0])['url']).lower() !=  '*://dave.com' and ((url_from_table[0])['url']).lower() != '*://lisaj.ca' and ((url_from_table[0])['url']).lower() != '*://nowhere.com':
                logging.error((url_from_table[0])['url'])
                raise TestFailure('URL %s  not present URLs table' % (url_from_table[0])['url'] )
       #11
    def test_11(self):
        """
        TS-422:SFIMPORT : Import urls format file for removing old categories and append new categroies to a url.
        """
        cat = """ms"""
        test_file = runtime.data_path+'/sfimport/sfimport_URLS_format_file.txt'
        sfimport_obj=sfimport(file_type='u')
        sfimportResult = sfimport_obj.modify(test_file,cat)
        url_dict = sfimport_obj.url_dict()
        if sfimportResult is None:
            logging.error("updateCategorySFImport_file function is unable to update category of URLs")
            raise TestFailure
        else:
            logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
            logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
            logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
            if not (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
                raise TestFailure
            for key in list(url_dict.keys()):
                url_cat = self.sql_obj.get_select_data('select * from u2.dbo.categories where url_id='+key+' order by set_on DESC')
                if ((url_cat[0])['cat_short']) !=  'ms' :
                    raise TestFailure('URL category is not "ms" ')

    #12
    def test_12(self):
        """
        TS-421:SFIMPORT : Import urls format file for deleting categories and url from database.
        """
        test_file = runtime.data_path+'/sfimport/sfimport_URLS_format_file.txt'
        sfimport_obj=sfimport(file_type='u')
        sfimportResult = sfimport_obj.delete_category(test_file)
        url_dict = sfimport_obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        if not (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -n 10 -D",output_file='anurag.txt')
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if len(url_from_table) != 0:
                logging.error(url_from_table)
                raise TestFailure('URLs not removed from DB even after TMAN run')
        #13
    def test_13(self):
        """
        TS-411:SFIMPORT: Import XML format file for appending new category to a URL.
        """
        cat = '''ms'''
        test_file = runtime.data_path+'/sfimport/sfimport_XML_format_file.txt'
        sfimport_obj=sfimport(file_type='x')
        sfimportResult = sfimport_obj.append_category(test_file,cat)
        url_dict = sfimport_obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        if not (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if ((url_from_table[0])['url']).lower() !=  '*://reallygreatsite.com/iloveit2' and ((url_from_table[0])['url']).lower() != '*://chem.umn.edu' and ((url_from_table[0])['url']).lower() != '*://aol2.com':
                logging.error((url_from_table[0])['url'])
                raise TestFailure('URL %s  not present URLs table' % (url_from_table[0])['url'] )

        #14
    def test_14(self):
        """
        TS-413:SFIMPORT : Import XML format file for removing old categories and append new categroies to a url.
        """
        cat = 'ph'
        test_file = runtime.data_path+'/sfimport/sfimport_XML_format_file.txt'
        sfimport_obj=sfimport(file_type='x')
        sfimportResult = sfimport_obj.modify(test_file,cat)
        url_dict = sfimport_obj.url_dict()
        if sfimportResult is None:
            logging.error("updateCategorySFImport_file function is unable to update category of URLs")
            raise TestFailure
        else:
            logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
            logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
            logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))

            if not (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
                raise TestFailure
            for key in list(url_dict.keys()):
                url_cat = self.sql_obj.get_select_data('select * from u2.dbo.categories where url_id='+key+' order by set_on DESC')
                if ((url_cat[0])['cat_short']) !=  'ph' :
                    raise TestFailure('URL category is not "ph" ')
        #15
    def test_15(self):
        """
        TS-412:SFIMPORT : Import XML format file for deleting categories and url from database.
        """
        test_file = runtime.data_path+'/sfimport/sfimport_XML_format_file.txt'
        sfimport_obj=sfimport(file_type='x')
        sfimportResult = sfimport_obj.delete_category(test_file)
        url_dict = sfimport_obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        if not (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            raise TestFailure
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -n 10 -D",output_file='anurag.txt')
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if len(url_from_table) != 0:
                logging.error(url_from_table)
                raise TestFailure('URLs not removed from DB even after TMAN run')
        #16
    def test_16(self):
        """
        TS-425:SFIMPORT : Verify that only new urls are added in the database using sfimport
        """
        url = "*://" + str(time.time()) + ".COM"
        url1 = "*://1"+str(time.time()) + ".COM"
        urls = ['''www.google.com''', url1, url]
        cat = """sx"""
        obj=sfimport()
        sfimportResult = obj.insert(urls,cat,ins_type='new')
        url_dict = obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ((sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0) and (sfimportResult["URLs Added_to_List"] == 2) and (sfimportResult["URLs already_OK"] == 1)):
            raise TestFailure
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if ((url_from_table[0])['url']) !=  url and ((url_from_table[0])['url']) != url1:
                logging.info((url_from_table[0])['url'])
                if 'GOOGLE.COM' in (url_from_table[0]['url']):
                    pass
                else:
                    raise TestFailure('URL %s  not present URLs table' % (url_from_table[0])['url'] )
      #17
    def test_17(self):
        """
        TS-426:SFIMPORT : Insert urls in U2 database using sfimport
        """
        url = "*://" + str(time.time())+ ".COM"
        urls = [url]
        cat = """ms"""
        obj=sfimport()
        sfimportResult = obj.insert(urls,cat)
        url_dict = obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ((sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0) and (sfimportResult["URLs Added_to_List"] == 1)):
            raise TestFailure
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if ((url_from_table[0])['url']) !=  url:
                logging.error((url_from_table[0])['url'])
                raise TestFailure('URL %s  not present URLs table' % url)

    #18
    def test_18(self):
        """
        TS-424:SFIMPORT : Queue urls with cgi parameters for deletion of categories.
        """
        url = "*://" + str(time.time()) + ".COM"
        logging.info(url)
        urls = [url]
        cat = """ms"""
        obj=sfimport()
        sfimportResult = obj.insert(urls,cat)
        url_dict = obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ( (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0) and (sfimportResult["URLs Added_to_List"] == 1)):
            raise TestFailure
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if ((url_from_table[0])['url']) !=  url:
                logging.error((url_from_table[0])['url'])
                raise TestFailure('URL %s  not present URLs table' % url)
        urls = [url]
        sfimportResult = obj.delete_category(urls)
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ((sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0) and (sfimportResult["URLs_Deleted"] == 1)):
            raise TestFailure
        agent_obj = Agents('tman')
        agent_obj.run_agent(agent_args="-d -i -s -n 10 -D",output_file='anurag.txt')
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if len(url_from_table) != 0:
                logging.error(url_from_table)
                raise TestFailure('URLs not removed from DB even after TMAN run')

     #Try to remove a non existent URL.Check for field that it is already removed
        url = "http://" + str(time.time()) + ".com"
        urls = [url]
        sfimportResult = obj.delete_category(urls)
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ((sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0) and (sfimportResult["URLs_Already_Removed"] == 1)):
            raise TestFailure
    #19
    def test_19(self):
        """
        TS-200:SFIMPORT:Insert a URL with cgi parameters
        """
        url = "http://myurl.com/?param1=value1&param2=value2"
        urls = [url]
        cat = """ms"""
        obj=sfimport()
        sfimportResult = obj.insert(urls,cat)
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ( (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0)):
            raise TestFailure

    #20
    def test_20(self):
        """
        TS-201:SFIMPORT:Exclude IPs by using -x option
        """
        urls = ["172.168.1.100", "anurag.com"]
        cat = """ms"""
        obj=sfimport(exclude_ip='yes')
        sfimportResult = obj.insert(urls,cat)
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ( (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0) and (sfimportResult["skipped_exclude_ip"] == 1) ):
            raise TestFailure
        #21
    def test_21(self):
        """
        TS-202:SFIMPORT:Insert URLs with categories into the U2 db and the priority
        """

        url = "http://" + str(time.time()) + ".com"
        urls = [url]
        cat = """ms"""
        obj=sfimport(priority='9999')
        sfimportResult = obj.insert(urls,cat)
        url_dict = obj.url_dict()
        logging.error(len(url_dict))
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ( (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0)  ):
            raise TestFailure
        for key in list(url_dict.keys()):
            pri = self.sql_obj.get_select_data('select * from u2.dbo.queue where url_id='+key)
            logging.info("Inserted onto queue " + str((pri[0])['priority']))
            if (pri[0])['priority'] != 9999:
                raise TestFailure('URL not concatenated to domian only in URLs table')

    #22
    def test_22(self):
        """
        TS-205:SFIMPORT:Attempt to run sfimport with -t option to shorten URL to domain name
        """
        url = "*://" + str(time.time()) + ".COM"
        path = "/path/query"
        total_url = url+path
        cat = """ms"""
        urls=[total_url]
        obj=sfimport(domain_only='yes')
        sfimportResult = obj.insert(urls,cat)
        url_dict = obj.url_dict()
        logging.error(len(url_dict))
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ( (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0)  ):
            raise TestFailure
        for key in list(url_dict.keys()):
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            logging.info("Inserted onto queue " + str((url_from_table[0])['url']))
            if (url_from_table[0])['url'] != url:
                raise TestFailure('URL not concatenated to domian only in URLs table')
            if (url_dict[key])[0] != url :
                logging.error((url_dict[key])[0])
                logging.error(url)
                raise TestFailure('Error in shortening the URL to domain name only')
     #23
    def test_23(self):
        """
        TS-199:SFIMPORT: Insert URLs into the "Chinese" queue.
        """
        url = "*://" + str(time.time()) + ".COM"
        cat = """ms"""
        urls=[url]
        obj=sfimport(queue_name='Chinese')
        sfimportResult = obj.queue(urls)
        url_dict = obj.url_dict()
        logging.info(len(url_dict))
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ( (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0)  ):
            raise TestFailure
        for key in list(url_dict.keys()):
            queues = self.sql_obj.get_select_data('select * from u2.dbo.queue where url_id='+key)
            logging.info("Inserted onto queue " + str((queues[0])['queue']))
            if (queues[0])['queue'] != 18:
                raise TestFailure('URL not inserted into queue 18')
            if (url_dict[key])[2] != '18' :
                logging.error((url_dict[key])[2])
                logging.error(url)
                raise TestFailure('Error in Queuing to Queue 18')


    # 24
    def test_24(self):
        """
        TS-203:SFIMPORT:Insert URLs into the Queue without removing the protocol information
        """
        url = "HTTP://" + str(time.time()) + ".COM"
        cat = """ms"""
        urls=[url]
        obj=sfimport(keep_protocol='yes')
        sfimportResult = obj.append_category(urls,cat)
        url_dict = obj.url_dict()
        logging.warning(len(url_dict))
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ( (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0)  ):
            raise TestFailure
        for key in list(url_dict.keys()):
            if (url_dict[key])[0] != url :
                raise TestFailure('Error in keeping the protocol of URL')
            url_from_table = self.sql_obj.get_select_data('select * from u2.dbo.urls where url_id='+key)
            if (url_from_table[0])['url'] != url:
                raise TestFailure('In DB , the URL is stored without the protocol')
    #25
    def test_25(self):
        """
        TS-1398:SFIMPORT: Attempt to remove categories and langauge by -R option.
        """
        url = "HTTP://" + str(time.time()) + ".COM"
        cat = """ms"""
        urls=[url]
        obj=sfimport()
        sfimportResult = obj.append_category(urls,cat)
        url_dict = obj.url_dict()
        logging.warning(len(url_dict))
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ( (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0) and (sfimportResult["URLs Language/Categories_appended"] == 1) ):
            raise TestFailure
        for key in url_dict:
            cats = self.sql_obj.get_select_data('select * from u2.dbo.categories where url_id='+key)
            logging.info((cats[0])['cat_short'])
            if (cats[0])['cat_short'] != 'ms':
                raise TestFailure('Cat Short in categories table doesnot match to "ms" ')
        sfimportResult = obj.remove(urls,cat)
        logging.warning(len(url_dict))
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ( (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0) and (sfimportResult['URLs_Deleted'] == 1) ):
            raise TestFailure
        for key in url_dict:
            cats = self.sql_obj.get_select_data('select * from u2.dbo.categories where url_id='+key)
            if len(cats) != 0:
                raise TestFailure('Category of the URL is not removed ')
      #26
    def test_26(self):
        """
        TS-204:SFIMPORT:Attempt to run sfimport with the modify option to update categories and language
        """
        #Inserting a new URL with cat 'ms'
        url = "*://" + str(time.time()) + ".COM"
        cat = """ms"""

        urls=[url]
        obj=sfimport()
        sfimportResult = obj.insert(urls,cat)
        url_dict = obj.url_dict()
        logging.warning(len(url_dict))
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ( (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0) and (sfimportResult["URLs Added_to_List"] == 1) ):
            raise TestFailure
        for key in url_dict:
            cats = self.sql_obj.get_select_data('select * from u2.dbo.categories where url_id='+key)
            logging.info((cats[0])['cat_short'])
            if (cats[0])['cat_short'] != 'ms':
                raise TestFailure('Cat Short in categories table doesnot match to "ms" ')
        #modify URL category to 'sx'
        cat = """sx"""
        sfimportResult = obj.modify(urls,cat)
        url_dict = obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ( (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0) and (sfimportResult["URLs Language/Categories_modified"] == 1) ):
            raise TestFailure
        for key in url_dict:
            cats = self.sql_obj.get_select_data('select * from u2.dbo.categories where url_id='+key)
            logging.info((cats[0])['cat_short'])
            if (cats[0])['cat_short'] != 'sx':
                raise TestFailure('Cat Short in categories table doesnot match to "sx" ')

        # modify again but skipped because cats are same
        cat = """sx"""
        sfimportResult = obj.modify(urls,cat)
        url_dict = obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ( (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0) and (sfimportResult["URLs already_OK"] == 1) ):
            raise TestFailure

    #27
    def test_27(self):
        """
        TS-1401:SFIMPORT: Remove URLs from specified queue using -u option
        """
        url = "testurl" + str(time.time()) + ".COM"
        cat = """ms"""
        urls=[url]

        obj=sfimport(queue_name='Chinese')
        sfimportResult = obj.queue(urls)
        url_dict = obj.url_dict()
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ( (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0)  ):
            raise TestFailure
        for key in list(url_dict.keys()):
            queues = self.sql_obj.get_select_data('select * from u2.dbo.queue where url_id='+key)
            logging.info("Inserted onto queue " + str((queues[0])['queue']))
            if (queues[0])['queue'] != 18:
                raise TestFailure('URL not inserted into queue 18')
            if (url_dict[key])[2] != '18' :
                logging.info((url_dict[key])[2])
                logging.warning(url)
                raise TestFailure('Error in Queuing to Queue 18')


        obj=sfimport(queue_name='Chinese')
        sfimportResult = obj.queue(urls,opt='remove')
        logging.debug("Total_Successful :  %s"%(sfimportResult["Total_Successful"]))
        logging.debug("Total_Canon_Errors :  %s"%(sfimportResult["Total_Canon_Errors"]))
        logging.debug("Total_Errors :  %s"%(sfimportResult["Total_Errors"]))
        logging.debug("Total Number of URLS  : %s"%(len(urls)))
        if not ( (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0) and (sfimportResult["URLs_Deleted"] == 1) ):
            raise TestFailure('Log verification failed')
        for key in list(url_dict.keys()):
            queues = self.sql_obj.get_select_data('select * from u2.dbo.queue where url_id='+key)
            if len(queues) != 0:
                raise TestFailure('URL whose only queue is removed is not removed from database')

