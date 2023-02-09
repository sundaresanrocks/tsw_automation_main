# -*- coding: utf-8 -*-

import time

from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException

from tests.concat.bulk.xpathbulk import XpathCollection
from lib.sfimport import sfimport
import logging
from lib.exceptions import TestFailure
from framework.test import SandboxedTest
from lib.db.mssql import TsMsSqlWrap
from concat.bulk.libbulk import Bulk as BulkLib
from libx.ssh import SSHConnection


class Bulk(SandboxedTest):
    bulk_url = "http://tsqa32aswaui.wsrlab:8080/coreui/"

    @classmethod
    def setUpClass(cls):
        cls.user_name = 'user2'
        cls.password = 'smartfilter'
        cls.host = 'tsqa32aswaui.wsrlab'
        cls.host_uname = 'toolguy'
        cls.host_pwd = 'xdr5tgb'
        cls.common_log = '/opt/sftools/log/common.log'
        cls.temp_log = '/home/toolguy/anu_log.txt'
        cls.lib_obj = BulkLib()
    def setUp(self):
        SandboxedTest.setUp(self)
        logging.info('Running method setup')
        sql_obj = TsMsSqlWrap('U2')
        del_query = "delete from U2.DBO.RESOURCE_LOCKS"
        logging.info('running ' + del_query)
        sql_obj.execute_sql_commit(del_query)
        self.driver = self.lib_obj.login(self.user_name, self.password)
        self.driver.maximize_window()
        time.sleep(2)

    def tearDown(self):
        SandboxedTest.tearDown(self)
        logging.info('Running method TearDown')
        self.driver.quit()

    def test_01(self):

        try:
            self.driver.find_element_by_name(XpathCollection.pattern_box)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Pattern Box not found")

    def test_02(self):
        """"""
        try:
            self.driver.find_element_by_xpath(XpathCollection.language_list)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Language List not found")

    def test_03(self):
        """"""
        try:
            self.driver.find_element_by_xpath(XpathCollection.queue_list)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Queue List not found")

    def test_04(self):
        """"""
        try:
            self.driver.find_element_by_xpath(XpathCollection.per_page_list)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("per_page_list not found")

    def test_05(self):
        """"""
        try:
            self.driver.find_element_by_xpath(XpathCollection.priority)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("priority Box not found")

    def test_06(self):
        """"""
        try:
            self.driver.find_element_by_xpath(XpathCollection.search)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("search not found")

    def test_07(self):
        """"""
        try:
            self.driver.find_element_by_xpath(XpathCollection.logout)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("logout Box not found")

    def test_08(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            self.assertEqual("URL", self.driver.find_element_by_css_selector("p").text)
            self.assertEqual("Language", self.driver.find_element_by_xpath("//th[3]/p").text)
            self.assertEqual("Covered By", self.driver.find_element_by_xpath("//th[4]/p").text)
            self.assertEqual("Priority", self.driver.find_element_by_xpath("//th[5]/p").text)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("3 Columns not found")

    def test_09(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            self.driver.find_element_by_xpath(XpathCollection.cat1)
            self.driver.find_element_by_xpath(XpathCollection.cat2)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("2 Category Drop Downs not found")

    def test_10(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            if not (self.driver.find_element_by_xpath(XpathCollection.select_all).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.select_all).click()
            self.driver.find_element_by_xpath(XpathCollection.cat2)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("2 Category Drop Downs not found")
        logging.info('SANITY TESTS ARE COMPLETE')

    def test_11(self):
        """dismiss button"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            dismiss = self.driver.find_element_by_xpath(XpathCollection.dismiss)
            i = 2
            while i <= 4:
                self.driver.find_element_by_xpath(XpathCollection.cb_1+str(i)+XpathCollection.cb_2).click()
                i += 1
            dismiss.click()
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("First 3 URLs not dismissed")

    def test_12(self):
        """clear fields"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            self.driver.find_element_by_xpath(XpathCollection.cat1).send_keys('Dating (dp)')
            self.driver.find_element_by_xpath(XpathCollection.cat2).send_keys('Entertainment (et)')
            self.driver.find_element_by_xpath(XpathCollection.comment_box).send_keys('Comment')
            self.driver.find_element_by_xpath(XpathCollection.bulk_action).send_keys('Add')
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            opt1 = Select(self.driver.find_element_by_xpath(XpathCollection.cat1)).first_selected_option.text
            opt2 = Select(self.driver.find_element_by_xpath(XpathCollection.cat2)).first_selected_option.text
            comment = self.driver.find_element_by_xpath(XpathCollection.comment_box).text
            if opt1 != 'Category' and opt2 != 'Category' and comment != '':
                raise TestFailure("Defaults not set")

        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_13(self):
        """"""
        try:
            self.lib_obj.number_of_urls(25)
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys('%org')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            text = self.driver.find_element_by_xpath(XpathCollection.first_url_row).text
            if not text.endswith('ORG'):
                raise TestFailure("Does not end with ORG")
            i = 2
            while i <= 25:
                text = self.driver.find_element_by_xpath(XpathCollection.url_col_1+str(i)+XpathCollection.url_col_2).text
                if not text.endswith('ORG'):
                    raise TestFailure("Does not end with ORG")
                i += 1
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_14(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys('%_org')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            text = self.driver.find_element_by_xpath(XpathCollection.first_url_row).text
            if not text.endswith('ORG'):
                raise TestFailure("Does not end with ORG")
            i = 2
            while i <= 25:
                text = self.driver.find_element_by_xpath(XpathCollection.url_col_1+str(i)+XpathCollection.url_col_2).text
                if not text.endswith('ORG'):
                    raise TestFailure("Does not end with ORG")
                i += 1
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_15(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys('[0-9]%')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            text = self.driver.find_element_by_xpath(XpathCollection.first_url_row).text
            if not text.endswith('ORG'):
                raise TestFailure("Does not end with ORG")
            i = 2
            while i <= 25:
                text = self.driver.find_element_by_xpath(XpathCollection.url_col_1+str(i)+XpathCollection.url_col_2).text
                if not text.endswith('ORG'):
                    raise TestFailure("Does not end with ORG")
                i += 1
        except (NoSuchElementException, ElementNotVisibleException) as e:
            logging.info('Expected empty set')

    def test_16(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys('[^0-9]%')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            self.driver.find_element_by_xpath(XpathCollection.first_url_row).text
            i = 2
            while i <= 25:
                self.driver.find_element_by_xpath(XpathCollection.url_col_1+str(i)+XpathCollection.url_col_2).text
                i += 1
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_17(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys('')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            self.driver.find_element_by_xpath(XpathCollection.first_url_row).text
            i = 2
            while i <= 25:
                self.driver.find_element_by_xpath(XpathCollection.url_col_1+str(i)+XpathCollection.url_col_2).text
                i += 1
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_18(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys('%[a-z]%[0-9]%')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            self.driver.find_element_by_xpath(XpathCollection.first_url_row).text
            i = 2
            while i <= 25:
                self.driver.find_element_by_xpath(XpathCollection.url_col_1+str(i)+XpathCollection.url_col_2).text
                i += 1
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_19(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys('%[%20]%')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            self.driver.find_element_by_xpath(XpathCollection.first_url_row).text
            i = 2
            while i <= 25:
                self.driver.find_element_by_xpath(XpathCollection.url_col_1+str(i)+XpathCollection.url_col_2).text
                i += 1
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_20(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_xpath(XpathCollection.language_list).send_keys('English')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            text = self.driver.find_element_by_xpath(XpathCollection.first_lang_row).text
            if 'English' not in text:
                raise TestFailure('Not all URLs are English')
            i = 2
            while i <= 25:
                text = self.driver.find_element_by_xpath(XpathCollection.lang_col_1+str(i)+XpathCollection.lang_col_2).text
                if 'English' not in text:
                    logging.warning(text)
                    raise TestFailure('Not all URLs are English')
                i += 1
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_21(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            if not (self.driver.find_element_by_xpath(XpathCollection.cb_1+str(i)+XpathCollection.cb_2).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.cb_1+str(i)+XpathCollection.cb_2).click()
            cats = ['Dating (dp)', 'Entertainment (et)']
            self.lib_obj.categorize_and_comment(cats, 'Adding Comment')
            time.sleep(5)
            self.driver.switch_to_default_content

        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_22(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            if not (self.driver.find_element_by_xpath(XpathCollection.cb_1+'3'+XpathCollection.cb_2).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.cb_1+'3'+XpathCollection.cb_2).click()
            cats = ['Dating (dp)', 'Entertainment (et)']
            self.lib_obj.categorize_and_comment(cats, '')
            time.sleep(2)
            alert_text = self.driver.switch_to_alert().text
            if alert_text != "Please add comments for chosen Urls & Categories":
                raise TestFailure('Empty comment message is not shown')
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_23(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            if not (self.driver.find_element_by_xpath(XpathCollection.cb_1+'3'+XpathCollection.cb_2).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.cb_1+'3'+XpathCollection.cb_2).click()
            cats=[]
            self.lib_obj.categorize_and_comment(cats, 'Adding comment')
            time.sleep(2)
            alert_text = self.driver.switch_to_alert().text
            if alert_text != "Please choose at least one category before submitting":
                raise TestFailure('No categories message is not shown')
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_24(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            if not (self.driver.find_element_by_xpath(XpathCollection.cb_1+'3'+XpathCollection.cb_2).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.cb_1+'3'+XpathCollection.cb_2).click()
            cats = ['Dating (dp)', 'Entertainment (et)']
            self.lib_obj.categorize_and_comment(cats, 'Adding comment','Bulk Actions...')
            time.sleep(2)
            alert_text = self.driver.switch_to_alert().text
            if alert_text != "Please choose a valid action before submitting":
                raise TestFailure('No Action message is not shown')
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_25(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            cats = ['Dating (dp)', 'Entertainment (et)']
            self.lib_obj.categorize_and_comment(cats, 'Adding comment')
            time.sleep(2)
            alert_text = self.driver.switch_to_alert().text
            if alert_text != "Please choose at least one Url to proceed to Add Bulk Action":
                raise TestFailure('No categories message is not shown')
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_26(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys('%memo%')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            url = self.driver.find_element_by_xpath(XpathCollection.url_col_1+"3"+XpathCollection.url_col_2).text
            if not (self.driver.find_element_by_xpath(XpathCollection.cb_1+'3'+XpathCollection.cb_2).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.cb_1+'3'+XpathCollection.cb_2).click()
            cats = ['Dating (dp)', 'Entertainment (et)']
            self.lib_obj.categorize_and_comment(cats, 'Adding comment')
            time.sleep(5)
            self.driver.switch_to_default_content
            sql_obj = TsMsSqlWrap('U2')
            query = "select memo from u2.dbo.url_info inf,U2.dbo.urls u(NOLOCK) where u.url like '"+ url +"' and u.url_id = inf.url_id "
            memos = sql_obj.get_select_data(query)
            for memo in memos:
                if 'Bulk update batch' not in memo[0] or 'Adding comment' not in memo[0]:
                    raise TestFailure('Memo not added properly in url_info table')
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_27(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys('%test%')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            url = self.driver.find_element_by_xpath(XpathCollection.url_col_1+"3"+XpathCollection.url_col_2).text
            if not (self.driver.find_element_by_xpath(XpathCollection.cb_1+'3'+XpathCollection.cb_2).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.cb_1+'3'+XpathCollection.cb_2).click()
            cats = ['Dating (dp)', 'Entertainment (et)']
            self.lib_obj.categorize_and_comment(cats, 'Adding comment')
            time.sleep(5)
            self.driver.switch_to_default_content
            sql_obj = TsMsSqlWrap('U2')
            query = "select cat_short from u2.dbo.categories inf,U2.dbo.urls u(NOLOCK) where u.url like '"+ url +"' and u.url_id = inf.url_id "
            cats = sql_obj.get_select_data(query)
            flag = 0
            logging.warning(cats)
            for cat in cats:
                if cat[0] in ['dp','et']:
                    flag += 1
            if flag != 2:
                raise TestFailure('Categories dp/et are not present')
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_28(self):
        """check for lang of sfimport urls"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            sql_obj = TsMsSqlWrap('U2')
            url =  "*://u" + str(time.time()) + ".COM"
            urls = [url]
            obj=sfimport(queue_name='General')
            obj.queue(urls)
            url_dict = obj.url_dict()

            for key in list(url_dict.keys()):
                logging.warning(key)
                update_query = "update u2.dbo.queue set priority = 99999999 where url_id=" + key
                sql_obj.execute_sql_commit(update_query)
            self.driver.find_element_by_xpath(XpathCollection.priority).clear()
            self.driver.find_element_by_xpath(XpathCollection.priority).send_keys('99999999')
            self.driver.find_element_by_xpath(XpathCollection.language_list).send_keys('All')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                    time.sleep(5)
                    logging.info('waited for 5 seconds')
            text = self.driver.find_element_by_xpath(XpathCollection.first_url_row).text
            for key in list(url_dict.keys()):
                logging.warning(key)
                update_query = "update u2.dbo.queue set priority = 900 where url_id=" + key
                sql_obj.execute_sql_commit(update_query)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")


    def test_29(self):
        """check for queue of sfimport urls"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            sql_obj = TsMsSqlWrap('U2')
            url =  "*://u" + str(time.time()) + ".COM"
            urls = [url]
            obj=sfimport(queue_name='Chinese')
            obj.queue(urls)
            url_dict = obj.url_dict()

            for key in list(url_dict.keys()):
                logging.warning(key)
                update_query = "update u2.dbo.queue set priority = 99999 where url_id=" + key
                sql_obj.execute_sql_commit(update_query)
            self.driver.find_element_by_xpath(XpathCollection.priority).clear()
            self.driver.find_element_by_xpath(XpathCollection.priority).send_keys('99999')
            self.driver.find_element_by_xpath(XpathCollection.language_list).send_keys('All')
            self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Chinese')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                    time.sleep(5)
                    logging.info('waited for 5 seconds')
            text = self.driver.find_element_by_xpath(XpathCollection.first_url_row).text
            for key in list(url_dict.keys()):
                logging.warning(key)
                update_query = "update u2.dbo.queue set priority = 9999 where url_id=" + key
                sql_obj.execute_sql_commit(update_query)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_30(self):
        """check for covered by info"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
        except Exception:
            pass

    def test_31(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            flag = 0
            pp_list = self.driver.find_element_by_xpath(XpathCollection.per_page_list)
            for option in pp_list.find_elements_by_tag_name('option'):
                if option.text == '25':
                    option.click()
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            opt1 = self.driver.find_element_by_xpath(XpathCollection.cat1)
            for option in opt1.find_elements_by_tag_name('option'):
                if option.text == "Finance/Banking (fi)":
                    flag = -1
                if option.text == "FinancInfo (fn)":
                    flag += 1
                if option.text == "FinInstitu (fs)":
                    flag += 1
            logging.warning(flag)
            if flag == -1:
                 raise TestFailure("Depreciated category Finance/Banking (fi) is present")
            if flag != 2:
                 raise TestFailure("fn or fs category is not present")
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_33(self):
        """Gets Language list from U2.language"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            db_lang_list= []
            query = "select lang from u2.dbo.language"
            sql_obj = TsMsSqlWrap('U2')
            langs = sql_obj.get_select_data(query)
            for i in langs:
                db_lang_list.append(i['lang'])
            lang_list = self.driver.find_element_by_xpath(XpathCollection.language_list)
            for option in lang_list.find_elements_by_tag_name('option'):
                if option.text != 'All':
                    val = option.text
                    logging.info(val)
                    if val not in db_lang_list:
                        raise TestFailure(option.text+" not found in u2.dbo.language")
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_35(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys('%_[a-z]_%')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            self.driver.find_element_by_xpath(XpathCollection.first_url_row).text
            i = 2
            while i <= 25:
                self.driver.find_element_by_xpath(XpathCollection.url_col_1+str(i)+XpathCollection.url_col_2).text
                i += 1
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_36(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys("%a[a-z]9[0-9]%")
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            self.driver.find_element_by_xpath(XpathCollection.first_url_row).text
            i = 2
            while i <= 25:
                self.driver.find_element_by_xpath(XpathCollection.url_col_1+str(i)+XpathCollection.url_col_2).text
                i += 1
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_37(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys("%%")
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            self.driver.find_element_by_xpath(XpathCollection.first_url_row).text
            i = 2
            while i <= 25:
                self.driver.find_element_by_xpath(XpathCollection.url_col_1+str(i)+XpathCollection.url_col_2).text
                i += 1
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_name(XpathCollection.pattern_box).clear()
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys('anurag')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            text = self.driver.find_element_by_xpath(XpathCollection.no_urls).text
            if text != "No matching urls found":
                raise TestFailure('Empty result set message not shown')
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_38(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            cmd = "tail -200 " + self.common_log +" > " + self.temp_log
            logging.info(cmd)
            rm_cmd = "rm " + self.temp_log
            ssh_obj = SSHConnection(host=self.host,username=self.host_uname,password=self.host_pwd)
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys('test_38')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            ssh_obj.execute(cmd)
            ssh_obj.get(remotepath=self.temp_log)
            fp = open('anu_log.txt','r')
            for line in fp.readlines():
                if "test_38" in line:
                    logging.warning(line)
                    if 'urls AS u WITH(NOLOCK)' not in line or 'queue AS q WITH(NOLOCK)' not in line or 'resource_locks WITH(NOLOCK)' not in line:
                        raise TestFailure('NOLOCK not present')
            ssh_obj.execute(rm_cmd)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_39(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            text = self.driver.find_element_by_xpath(XpathCollection.log_in_user).text
            if text != "Logged in as: User 2":
                raise TestFailure('error in log in user name')
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_40(self):
        """"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            cmd = "tail -200 " + self.common_log +" > " + self.temp_log
            logging.info(cmd)
            rm_cmd = "rm " + self.temp_log
            ssh_obj = SSHConnection(host=self.host,username=self.host_uname,password=self.host_pwd)
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Customer')
            self.driver.find_element_by_name(XpathCollection.pattern_box).send_keys('test_40')
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            ssh_obj.execute(cmd)
            ssh_obj.get(remotepath=self.temp_log)
            fp = open('anu_log.txt','r')
            for line in fp.readlines():
                if "test_40" in line:
                    logging.warning(line)
                    if 'q.queue = 1' not in line:
                        raise TestFailure('Customer Queue has queue_id = 1 and is not in the log file')
            ssh_obj.execute(rm_cmd)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_41(self):
        """TS-1412:Check for accuracy of priority available on the UI for a specific URL"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
                self.driver.find_element_by_xpath(XpathCollection.queue_list).send_keys('Sandbox')
            sql_obj = TsMsSqlWrap('U2')
            self.lib_obj.number_of_urls(25)
            self.driver.find_element_by_xpath(XpathCollection.search).click()
            for i in range(5):
                time.sleep(5)
                logging.info('waited for 5 seconds')
            url = self.driver.find_element_by_xpath(XpathCollection.first_url_row).text
            query = "select q.priority from U2.dbo.queue q, U2.dbo.urls u where u.URL like '" + url + "' and q.url_id=u.url_id"
            logging.info(query)
            priority = sql_obj.get_select_data(query)
            logging.warning('>>> ' + self.driver.find_element_by_xpath(XpathCollection.first_priority_row).text)
            for i in priority:
                logging.warning(i)
                if str(i['priority']) != self.driver.find_element_by_xpath(XpathCollection.first_priority_row).text:
                    raise TestFailure('Priority mismatch in u2.dbo.queue')
            logging.warning(priority)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_32(self):
        """TS-1672:Bulk UI has security Queues only check box"""
        try:
            if not (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
            db_qs_list= []
            query = "select queue_name from u2.dbo.queue_types where security_queue=1"
            sql_obj = TsMsSqlWrap('U2')
            qs = sql_obj.get_select_data(query)
            for i in qs:
                db_qs_list.append(i['queue_name'])
            qs_list = self.driver.find_element_by_xpath(XpathCollection.queue_list)
            for option in qs_list.find_elements_by_tag_name('option'):
                if option.text != 'All Security Queues'.strip():
                    val = option.text
                    logging.info(val)
                    if val not in db_qs_list:
                        raise TestFailure(option.text+" not found in u2.dbo.queue_types")
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

    def test_34(self):
        """TS-1673:If security queues only is not selected , queues list must list all queues other than security"""
        try:
            ui_qs_list= []
            count = 0
            if (self.driver.find_element_by_xpath(XpathCollection.security_queues_only).is_selected()):
                self.driver.find_element_by_xpath(XpathCollection.security_queues_only).click()
            db_qs_list= []
            query = "select queue_name from u2.dbo.queue_types where security_queue!=1"
            sql_obj = TsMsSqlWrap('U2')
            qs = sql_obj.get_select_data(query)
            for i in qs:
                db_qs_list.append(i['queue_name'])
            qs_list = self.driver.find_element_by_xpath(XpathCollection.queue_list)
            for option in qs_list.find_elements_by_tag_name('option'):
                if option.text != 'All Non Security Queues'.strip():
                    val = option.text
                    ui_qs_list.append(val)
                    count += 1
                    if val not in db_qs_list:
                        raise TestFailure(option.text+" not found in u2.dbo.queue_types")
            logging.info('Total of ' + str(count) + 'non security Queues are Listed')
            set1 = set(db_qs_list)
            set2 = set(ui_qs_list)
            diff = set1.symmetric_difference(set2)
            if len(diff) != 0:
                raise TestFailure('Inconsistency in Queue types ' + diff)
        except (NoSuchElementException, ElementNotVisibleException) as e:
            raise TestFailure("Element not found")

