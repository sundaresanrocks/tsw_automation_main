# coding=utf-8
"""
=====================================
URL expander  test cases
=====================================
"""

__author__ = 'sumeet'

import json
import unittest
from runtime import data_path
from urldb.urlexpander_lib import URLExpander
from conf.properties import set_prop_application
from conf.files import LOG
from conf.files import PROP
from conf.files import DIR
import re
from lib.db.mssql import TsMsSqlWrap
import logging


class TestUrlExpander(unittest.TestCase):


    def setUp(self):
        """
        setup for any common initialization before each test case
        """
        self.urlexpander=URLExpander()
        self.u2_con = TsMsSqlWrap('U2')


    def test_expanded_url_defaultvalue(self):
        """
        verify whether shortened urls are being expanded by default.
        """

        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 1 where url_shortener = 'bit.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 1 where url_shortener = 'bit.ly'")


        self.stdo,self.stde= self.urlexpander.run_urlexpander_agent('http://bit.ly/1bdDlXc')
        b=re.findall(r'expandedURL.*',self.stdo)
        assert("google.com" in b[0])

        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 0 where url_shortener = 'bit.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 0 where url_shortener = 'bit.ly'")


    def test_enabledset_0(self):
        """
        verify whether shortened urls are not being expanded when is_enabled is set to 0 .
        """

        logging.info("updating  u2.dbo.url_shorteners and setting enabled = 0 where url_shortener = 'bit.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set enabled = 0 where url_shortener = 'bit.ly'")

        self.stdo,self.stde= self.urlexpander.run_urlexpander_agent('http://bit.ly/1bdDlXc')
        b=re.findall(r'expandedURL.*',self.stdo)
        assert("google.com" not in b[0])
        assert("bit.ly/1bdDlXc" in b[0])
        logging.info(" shortned url is not expanded as expected ")

        logging.info("updating  u2.dbo.url_shorteners and setting enabled = 1 where url_shortener = 'bit.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set enabled = 1 where url_shortener = 'bit.ly'")


    def test_enabled1_isredirect0(self):
        """
        verify whether shortened urls are not being expanded when is_enabled is set to 1 and isredirect to 0 .
        """
        logging.info("updating  u2.dbo.url_shorteners and setting enabled = 1 and is_redirect=0 where url_shortener = 'bit.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set enabled = 1 , is_redirect = 0 where url_shortener = 'bit.ly'")

        self.stdo,self.stde= self.urlexpander.run_urlexpander_agent('http://bit.ly/1bdDlXc')
        assert("Error with client: exception=Shortening service is currently unsupported" in self.stdo)
        logging.info(" shortned url is not expanded as expected ")

        logging.info("updating  u2.dbo.url_shorteners and setting enabled = 1 and is_redirect = 0 where url_shortener = 'bit.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set enabled = 1 , is_redirect = 0 where url_shortener = 'bit.ly'")


    def test_enabled1_isredirect1(self):
        """
        verify whether shortened urls are  being expanded when is_enabled is set to 1 and isredirect to 1 .
        """
        logging.info("updating  u2.dbo.url_shorteners and setting enabled = 0 and is_redirect=0 where url_shortener = 'bit.ly' ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set enabled = 1 , is_redirect = 1 where url_shortener = 'bit.ly'")

        self.stdo,self.stde= self.urlexpander.run_urlexpander_agent('http://bit.ly/1bdDlXc')
        b=re.findall(r'expandedURL.*',self.stdo)
        assert("google.com" in b[0])
        logging.info(" shortned url is expanded as expected ")

        logging.info("updating  u2.dbo.url_shorteners and setting enabled = 1 and is_redirect = 0 where url_shortener = 'bit.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set enabled = 1 , is_redirect = 0 where url_shortener = 'bit.ly'")




    def test_expanded_url_goo_gl(self):
        """
        tests whether Urls are getting expanded correctly or not
        """
        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 1 where url_shortener = 'goo.gl'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 1 where url_shortener = 'goo.gl'")

        self.stdo,self.stde= self.urlexpander.run_urlexpander_agent('http://goo.gl/XnqAgq')
        b=re.findall(r'expandedURL.*',self.stdo)
        assert("facebook.com" in b[0])

        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 0 where url_shortener = 'goo.gl'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 0 where url_shortener = 'goo.gl'")


    def test_expanded_url_goo_gl_negativeflow(self):
        """
        tests whether Urls are getting expanded correctly or not
        """
        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 1 where url_shortener = 'goo.gl'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 1 where url_shortener = 'goo.gl'")

        ##### for negitve flow  we are passing the URL shortened with bit.do which is not a supported service ! ####
        self.stdo,self.stde= self.urlexpander.run_urlexpander_agent('http://bit.do/b8Vrb')
        b=re.findall(r'expandedURL.*',self.stdo)
        assert("facebook.com" not in b[0])
        assert("bit.do/b8Vrb" in b[0])
        logging.info("unsupported shortned url is not expanded as expected ")

        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 0 where url_shortener = 'goo.gl'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 0 where url_shortener = 'goo.gl'")





    def test_expand_url_tinyurl(self):
        """
        tests whether Urls are getting expanded correctly or not using tinyurl service
        """
        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 1 where url_shortener = 'tinyurl.com'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 1 where url_shortener = 'tinyurl.com'")

        self.stdo,self.stde= self.urlexpander.run_urlexpander_agent('http://tinyurl.com/zhj983p')
        b=re.findall(r'expandedURL.*',self.stdo)
        assert("tsqatestlink.wsrlab/index.php" in b[0])

        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 0 where url_shortener = 'tinyurl.com'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 0 where url_shortener = 'tinyurl.com'")


    def test_expand_url_tinyurl_negativeflow(self):
        """
        tests whether Urls are getting expanded correctly or not using tinyurl service
        """
        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 1 where url_shortener = 'tinyurl.com'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 1 where url_shortener = 'tinyurl.com'")

        ##### for negitve flow  we are passing the URL shortened with bit.do which is not a supported service ! ####
        self.stdo,self.stde= self.urlexpander.run_urlexpander_agent('http://bit.do/b8Vrb')
        b=re.findall(r'expandedURL.*',self.stdo)
        assert("facebook.com" not in b[0])
        assert("bit.do/b8Vrb" in b[0])
        logging.info("unsupported shortned url is not expanded as expected ")

        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 0 where url_shortener = 'tinyurl.com'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 0 where url_shortener = 'tinyurl.com'")


    def test_expand_url_bit_ly(self):
        """
        tests whether Urls are getting expanded correctly or not using tinyurl service
        """
        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 1 where url_shortener = 'bit.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 1 where url_shortener = 'bit.ly'")


        self.stdo,self.stde= self.urlexpander.run_urlexpander_agent('http://bit.ly/1UwRRP9')
        b=re.findall(r'expandedURL.*',self.stdo)
        assert("tsqatestlink.wsrlab/index.php" in b[0])

        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 0 where url_shortener = 'bit.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 0 where url_shortener = 'bit.ly'")

    def test_expand_url_bit_ly_negativeflow(self):
        """
        tests whether Urls are getting expanded correctly or not using tinyurl service
        """
        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 1 where url_shortener = 'bit.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 1 where url_shortener = 'bit.ly'")

        ##### for negitve flow  we are passing the URL shortened with bit.do which is not a supported service ! ####
        self.stdo,self.stde= self.urlexpander.run_urlexpander_agent('http://bit.do/b8Vrb')
        b=re.findall(r'expandedURL.*',self.stdo)
        assert("facebook.com" not in b[0])
        assert("bit.do/b8Vrb" in b[0])
        logging.info("unsupported shortned url is not expanded as expected ")

        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 0 where url_shortener = 'bit.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 0 where url_shortener = 'bit.ly'")


    def test_expand_url_ow_ly(self):
        """
        tests whether Urls are getting expanded correctly or not using tinyurl service
        """
        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 1 where url_shortener = 'ow.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 1 where url_shortener = 'ow.ly'")

        self.stdo,self.stde= self.urlexpander.run_urlexpander_agent('http://ow.ly/L8Ts300SuAn')
        b=re.findall(r'expandedURL.*',self.stdo)
        assert("webreference.com/html/tutorial2/2.html" in b[0])

        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 0 where url_shortener = 'ow.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 0 where url_shortener = 'ow.ly'")

    def test_expand_url_ow_ly_negativeflow(self):
        """
        tests whether Urls are getting expanded correctly or not using tinyurl service
        """
        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 1 where url_shortener = 'ow.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 1 where url_shortener = 'ow.ly'")

        ##### for negitve flow  we are passing the URL shortened with bit.do which is not a supported service ! ####
        self.stdo,self.stde= self.urlexpander.run_urlexpander_agent('http://bit.do/b8Vrb')
        b=re.findall(r'expandedURL.*',self.stdo)
        assert("facebook.com" not in b[0])
        assert("bit.do/b8Vrb" in b[0])
        logging.info("unsupported shortned url is not expanded as expected ")

        logging.info("updating  u2.dbo.url_shorteners and setting is_redirect = 0 where url_shortener = 'ow.ly'  ")
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 0 where url_shortener = 'ow.ly'")

    def test_unsupported_service(self):
        """
        test whether shortened url is not getting expanded for the unsupported services

        """
        self.stdo,self.stde= self.urlexpander.run_urlexpander_agent('http://bit.do/b8Vrb')
        b=re.findall(r'expandedURL.*',self.stdo)
        assert("facebook.com" not in b[0])
        assert("bit.do/b8Vrb" in b[0])
        logging.info("unsupported service shortned url is not expanded as expected ")

















