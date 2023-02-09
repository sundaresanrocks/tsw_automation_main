import time
import unittest

from selenium import webdriver

from tests.concat.bulk.xpathbulk import XpathCollection
from legacy.ticketlib import TicketingLib
import logging


class Bulk:
    bulk_url = "http://tsqa32aswaui.wsrlab:8080/coreui/"

    def __init__(self):
        pass

    def login(self, username, password, option='waui'):
        """Logs into Bulk UI"""
        driver = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.FIREFOX,
                                  command_executor=TicketingLib.ui_executor)
        driver.get(self.bulk_url)
        time.sleep(3)
        uname = driver.find_element_by_class_name(XpathCollection.user)
        uname.send_keys(username)
        pwd = driver.find_element_by_class_name(XpathCollection.pwd)
        pwd.send_keys(password)
        waui = driver.find_element_by_class_name(XpathCollection.login_list)
        waui.send_keys("waui")
        login = driver.find_element_by_class_name(XpathCollection.login)
        login.click()
        logging.info('Logged into BULK UI')
        time.sleep(3)
        self.driver = driver
        return driver

    def number_of_urls(self, number):
        """Selects number of URLs to be displayed in a Page[10,25,50,100,125,150,250,500]"""
        if number not in [10, 25, 50, 100, 125, 150, 250, 500]:
            raise Exception("Please enter a valid number for the list")
        pp_list = self.driver.find_element_by_xpath(XpathCollection.per_page_list)
        for option in pp_list.find_elements_by_tag_name('option'):
            if option.text == str(number):
                option.click()

    def categorize_and_comment(self, cats, comment, action='Add'):
        """Categorizes a URL , adds a given comment and submits it"""
        if (len(cats) > 2):
            raise Exception("Maximum of 2 categories are accepted for a URL")
        if len(cats) == 2:
            self.driver.find_element_by_xpath(XpathCollection.cat1).send_keys(cats[0])
            self.driver.find_element_by_xpath(XpathCollection.cat2).send_keys(cats[1])
        if len(cats) == 1:
            self.driver.find_element_by_xpath(XpathCollection.cat1).send_keys(cats[0])

        self.driver.find_element_by_xpath(XpathCollection.comment_box).send_keys(comment)
        self.driver.find_element_by_xpath(XpathCollection.bulk_action).send_keys(action)
        self.driver.find_element_by_xpath(XpathCollection.submit).click()


class BulkTests(unittest.TestCase):
    """Unit tests for TrustedSource Class"""

    def testOne(self):
        obj = Bulk()
        self.assertTrue(obj.login('user2', 'smartfilter'))


def main():
    unittest.main()


if __name__ == '__main__':
    main()