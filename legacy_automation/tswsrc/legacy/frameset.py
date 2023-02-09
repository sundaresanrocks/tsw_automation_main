"""
==========================================
Frameset Utils
==========================================
"""
__author__ = 'Anurag'

import unittest
import time
import logging

from selenium import webdriver

from lib.exceptions import DriverError
from legacy.ticketlib import TicketingLib


class Frameset:
    """
    Frameset utilities
    """
    frameset_url = "http://kmark:12secure@172.22.81.102/cgi-bin/tools/sf_frameset?url_id=-1&level=-1&act=l&rowcol=rows&agent_id=11&Priority_Class=A&Queue_Level=-1&From_Queue=1&url=*%3A%2F%2FXZUAMD.PE&view_url=&framerows=430&xinfo=&Memo=&lang=Unspecified&Ignore_Children=on&Send_To_Queue=1&manualWhichList=No"
    user_name = "kmark"
    password = "12secure"
    
    
    class Xpath:
        """
        Lists Frameset elements by XPATH
        """
        do_not_load = "//input[@name='Do_Not_Load_Url']"
        url = "//input[@name='url']"
        submit = "//input[@value='LoadNew']"
        categorize = "//td/table/tbody/tr/td/div/b/input"
    
    class Name:
        """
        Lists Frameset elements by NAME
        """
        top_frame = "sfcgi"
        botton_frame = "dsiplay"
           
    def categorize(self,driver,cats_list):
        """
        Takes the driver as parameter
        selects specified categories and clicks the categorize button
        """
        if driver is None:
            raise DriverError("Please provide UI Driver")
        for i in cats_list:
            cat = "c_" + i
            driver.find_element_by_name(cat).click()
        driver.find_element_by_css_selector("td > table > tbody > tr > td > div > b.n > input[type=\"button\"]").click()    

class FramesetTests(unittest.TestCase):
    """Unit tests for TrustedSource Class"""
    def testOne(self):
        try:
            self.assertTrue(Frameset().categorize('driver',['ms']))
        except AttributeError:
            logging.info('Expected the exception')

    def testTwo(self):
        driver = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.FIREFOX, command_executor=TicketingLib.ui_executor)
        driver.get(Frameset.frameset_url)
        time.sleep(6)
        driver.switch_to_frame(Frameset.Name.top_frame)
        time.sleep(1)
        driver.find_element_by_xpath(Frameset.Xpath.do_not_load).click()
        driver.find_element_by_xpath(Frameset.Xpath.url).clear()
        driver.find_element_by_xpath(Frameset.Xpath.url).send_keys('http://testurl.com')
        driver.find_element_by_xpath(Frameset.Xpath.submit).click()
        time.sleep(6)
        driver.switch_to_frame(Frameset.Name.top_frame)
        Frameset().categorize(driver,['ac','gm'])

def main():
    unittest.main()

if __name__ == '__main__':
    main()