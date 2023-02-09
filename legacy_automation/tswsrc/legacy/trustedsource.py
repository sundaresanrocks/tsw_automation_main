# -*- coding: utf-8 -*-
"""
__author__ = "Anurag"
"""
import time
import unittest

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from legacy.ticketlib import TicketingLib
from lib.exceptions import ProcessingError


class Xpath:
    """XPATH COllection for Trusredsource.org"""

    feedback = "//li[2]/a"
    ticketing_system = "//b/a"
    check_single_url = "//p[2]/a"
    product = "//select"
    url = "//tr[4]/td/input"
    check_url_button = "//tr[6]/td/div/a/span"
    submit_button = "//div[3]/div/a/span"

class TrustedSource:

    def __init__(self):
        self.ts_url = 'http://tsqatrustedsource.wsrlab/en/feedback/url'

    def submit_single_url(self,test_url,cats=None,comment=None):
        """"""
        if cats:
            if len(cats)>3:
                raise ProcessingError('Can pass a maximum of 3 cats only')
            #add code that adds optional categories
                pass
        if comment:
            #add code that adds optional comment
            pass
        driver = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.FIREFOX, command_executor=TicketingLib.ui_executor)
        #driver=webdriver.Firefox()
        driver.get(self.ts_url)
        driver.maximize_window()
        time.sleep(2)
        driver.find_element_by_xpath(Xpath.check_single_url).click()
        time.sleep(2)
        driver.find_element_by_xpath(Xpath.product).send_keys('McAfee SmartFilter XL')
        driver.find_element_by_xpath(Xpath.url).send_keys(test_url)
        driver.find_element_by_xpath(Xpath.check_url_button).click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, Xpath.submit_button)))
        driver.find_element_by_xpath(Xpath.submit_button).click()
        time.sleep(2)
        driver.quit()
        return True


class TrustedSourceTests(unittest.TestCase):
    """Unit tests for TrustedSource Class"""
    def testOne(self):
        self.assertTrue(TrustedSource().submit_single_url('http://testurlgivenhere.com'))

def main():
    unittest.main()

if __name__ == '__main__':
    main()