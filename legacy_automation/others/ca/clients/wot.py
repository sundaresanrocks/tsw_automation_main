import logging
import pprint
from bs4 import BeautifulSoup
from ca.clients.base import ChromeExtensionBase
from ca.clients.base import SCREEN_CAPTURE_CMD
from libx.process import ShellExecutor
import math
import operator
from functools import reduce
import datetime

__author__ = 'abhijeet'

import os
import time
from io import BytesIO

from selenium import webdriver, selenium
from selenium.webdriver.chrome.options import Options
from PIL import Image

from celery import Celery
from ca.clients.base import ChromeExtensionBase
from ca.ca_config import RABBITMQ_BROKER, RABBITMQ_BACKEND, TEXT_GRAY, TEXT_GREEN, TEXT_RED, TEXT_YELLOW
from ca.ca_config import RESULTS_QUEUE, RESULTS_TASK, SUPPORTED_TASKS

_WOT_LEFT = 537
_WOT_TOP = 57
_WOT_RIGHT = 555
_WOT_BOTTOM = 67
GREEN_COLOR_TUPLE = (162, 204, 146)

WOT_CROP_BOX = (_WOT_LEFT, _WOT_TOP, _WOT_RIGHT, _WOT_BOTTOM)
#GREEN_PIXEL_COUNT = (_WOT_BOTTOM - _WOT_TOP) * (_WOT_RIGHT - _WOT_LEFT)

wot_uid = 'cfnpidifppmenkapgihekkeednfoenal'
wot_version = '0.2.19_0'
wot_ext_local = 'C:/Users/' + os.getlogin() + '/AppData/Local/Google/Chrome SxS/User Data/Default/Extensions/' \
            + wot_uid + '/' + wot_version

WOT_EXTENSION_PATH = r'c:\tsw-ui\ca\wot'
# logging.info(wot_ext_local)
TEMP_FOLDER = r'c:\tsw-ui\ca\tmp'
TEMP_FILE_NAME = "wot-temp-file.bmp"
GREEN_SAMPLE1 = r'C:\src\ca\clients\clients_res\wot_res\green1.bmp'
GREEN_SAMPLE2 = r'C:\src\ca\clients\clients_res\wot_res\green2.bmp'
RED_SAMPLE1 = r'C:\src\ca\clients\clients_res\wot_res\red1.bmp'
RED_SAMPLE2 = r'C:\src\ca\clients\clients_res\wot_res\red2.bmp'
GRAY_SAMPLE = r'C:\src\ca\clients\clients_res\wot_res\gray.bmp'
YELLOW_SAMPLE = r'C:\src\ca\clients\clients_res\wot_res\yellow.bmp'

module_name = os.path.basename(__file__).partition('.')[0]
task_name = SUPPORTED_TASKS['wot']
app = Celery(task_name, backend=RABBITMQ_BACKEND, broker=RABBITMQ_BROKER, queue='wot')



class Wot(ChromeExtensionBase):
    """
    wot script
    """

    def __init__(self, chrome_driver_url):
        #todo: check if extension path exists. if not, handle appropriately
        chrome_options = Options()
        chrome_options.add_argument("test-type")
        chrome_options.add_argument("load-extension=%s" % WOT_EXTENSION_PATH)

        self.wot_driver = webdriver.Remote(chrome_driver_url, desired_capabilities=chrome_options.to_capabilities())

        ChromeExtensionBase.__init__(self, self.wot_driver)
        #self.driver.set_window_size(600, 600)
        self.wot_driver.set_window_size(600, 600)

        #ensure that there is only one open tab
        original_handle = self.wot_driver.current_window_handle
        for win_handle in self.wot_driver.window_handles:
            if not win_handle == original_handle:
                self.wot_driver.switch_to.window(win_handle)
                self.wot_driver.close()
        self.wot_driver.switch_to.window(original_handle)

    def analyze_url(self, url):
        logging.critical('URL: %s' % url)
        self.driver.get(url)
        time.sleep(2)

        #### Check if plugin response for URL is green or red
        '''
        count = 0
        output_file = os.path.join(TEMP_FOLDER, TEMP_FILE_NAME)
        while os.path.isfile(output_file):
            try:
                os.unlink(output_file)
            except:
                output_file = '%s-' % count + TEMP_FILE_NAME
                count += 1
        logging.critical('Window handle selenium: %s' % self.wot_driver.title)
        window_handle = self.AUTOIT.WinGetHandle(self.wot_driver.title)
        logging.critical('window_handle = %s' % window_handle)
        autoit_cmd = ' '.join([SCREEN_CAPTURE_CMD, output_file, window_handle, str(_WOT_LEFT), str(_WOT_TOP),
                               str(_WOT_RIGHT), str(_WOT_BOTTOM)])
        logging.critical(autoit_cmd)
        ShellExecutor.run_wait_standalone(autoit_cmd, env=False)
        '''
        output_file = self.take_screenshot_autoit(self.wot_driver, _WOT_LEFT, _WOT_TOP, _WOT_RIGHT, _WOT_BOTTOM)


        if not os.path.isfile(output_file):
            raise Exception('output file: %s not found!' % output_file)
            #todo: handle this

        #pass -- image is red
        if self.are_images_identical(RED_SAMPLE1, output_file):
            return ChromeExtensionBase.return_success_data("RED")
        if self.are_images_identical(RED_SAMPLE2, output_file):
            return ChromeExtensionBase.return_success_data("RED")

        #pass -- image is green
        if self.are_images_identical(GREEN_SAMPLE1, output_file):
            return ChromeExtensionBase.return_success_data("GREEN")
        if self.are_images_identical(GREEN_SAMPLE2, output_file):
            return ChromeExtensionBase.return_success_data("GREEN")

        #image is yellow
        if self.are_images_identical(YELLOW_SAMPLE, output_file):
            return ChromeExtensionBase.return_success_data('YELLOW')

        #image is gray
        if self.are_images_identical(GRAY_SAMPLE, output_file):
            return ChromeExtensionBase.return_success_data('GRAY')

        return ChromeExtensionBase.return_not_defined_data("UNKNOWN")


'''
def wot_task(urls):

    chrome_driver_url = "http://localhost:9515"

    logging.info('Loading chrome driver with extension...')

    product = wot(chrome_driver_url)

    results = []
    for url in urls:
        result = product.analyze_url(url)
        result["url"] = url
        results.append(result)

    pprint.pprint(results)
    product.dbcommit(results)
    product.
    product.driver.close()
'''

def internal_wot_task(urls):
    chrome_driver_url = "http://localhost:9515"
    logging.info('Loading chrome driver with extension...')
    product = Wot(chrome_driver_url)

    results = []
    for url in urls:
        try:
            result = product.analyze_url(url)
        except Exception as e:
            result["data"] = 'COMP_A_ERROR'
        result["url"] = url
        result["competitor"] = module_name
        results.append(result)

    pprint.pprint(results)
    product.driver.close()

    return results

def internal_wot_task_granular(urls):
    """
    yields url results one at a time
    :param urls:
    :return:
    """
    chrome_driver_url = "http://localhost:9515"
    logging.info('Loading chrome driver with extension...')
    product = Wot(chrome_driver_url)

    for url in urls:
        results = []
        try:
            result = product.analyze_url(url)
        except Exception as e:
            result["data"] = 'COMP_A_ERROR'
        result["url"] = url
        result["competitor"] = module_name
        results.append(result)
        pprint.pprint(results)
        yield results

    product.driver.close()

    return results

if __name__ == '__main__':
    #results = wot_task(['http://serasaexperian.info/', 'http://amazon.com', 'http://finlawfirm.com/images/j79.exe '])
    results = internal_wot_task_granular(['https://www.hackthissite.org/pages/programs/programs.php?cat=7'])
    logging.error(results)


'''
@app.task(name=task_name, ignore_result=True)
def wot_task(urls):
    """
    Task based on Avira plugin
    :return:
    """
    results = []
    try:
        results = internal_wot_task(urls)
    finally:
        app.send_task(RESULTS_TASK, [results], broker=RABBITMQ_BROKER, backend=RABBITMQ_BACKEND,  queue=RESULTS_QUEUE)
'''

@app.task(name=task_name, ignore_result=True)
def wot_task(urls):
    """
    sends results tasks per URL
    :param urls:
    """
    for results in internal_wot_task_granular(urls):
        app.send_task(RESULTS_TASK, [results], broker=RABBITMQ_BROKER, backend=RABBITMQ_BACKEND,  queue=RESULTS_QUEUE)
