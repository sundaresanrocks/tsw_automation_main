"""
IMPORTANT: This script makes use of the bitdefender trafficlight as it gives more state information on the url state as
compared to bitdefender internet security suite. Also all client scripts with standalone plugins could potentially be
run on the same VM sequentially; using multiple security suites on same VM will make block/pass detection unreliable.
"""
import logging
import pprint
from bs4 import BeautifulSoup
from ca.clients.base import ChromeExtensionBase
from ca.clients.base import SCREEN_CAPTURE_CMD
from libx.process import ShellExecutor
import math
import operator
from functools import reduce

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

_BITDEF_LEFT = 541
_BITDEF_TOP = 55
_BITDEF_RIGHT = 551
_BITDEF_BOTTOM = 61
GREEN_COLOR_TUPLE = (162, 204, 146)

BITDEF_CROP_BOX = (_BITDEF_LEFT, _BITDEF_TOP, _BITDEF_RIGHT, _BITDEF_BOTTOM)
#GREEN_PIXEL_COUNT = (_BITDEF_BOTTOM - _BITDEF_TOP) * (_BITDEF_RIGHT - _BITDEF_LEFT)

bitdef_uid = 'cfnpidifppmenkapgihekkeednfoenal'
bitdef_version = '0.2.19_0'
bitdef_ext_local = 'C:/Users/' + os.getlogin() + '/AppData/Local/Google/Chrome SxS/User Data/Default/Extensions/' \
            + bitdef_uid + '/' + bitdef_version

BITDEF_EXTENSION_PATH = r'c:\tsw-ui\ca\bitdefender'
# logging.info(bitdef_ext_local)
TEMP_FOLDER = r'c:\tsw-ui\ca\tmp'
TEMP_FILE_NAME = "bitdefender-temp-file.bmp"
GREEN_SAMPLE = r'C:\src\ca\clients\clients_res\bitdefender_res\green_sample.bmp'
RED_SAMPLE = r'C:\src\ca\clients\clients_res\bitdefender_res\red_sample.bmp'

module_name = os.path.basename(__file__).partition('.')[0]
task_name = SUPPORTED_TASKS['bitdefender']
app = Celery(task_name, backend=RABBITMQ_BACKEND, broker=RABBITMQ_BROKER, queue='bitdefender')



class Bitdefender(ChromeExtensionBase):
    """
    Bitdefender script
    """

    def __init__(self, chrome_driver_url):
        #todo: check if extension path exists. if not, handle appropriately
        chrome_options = Options()
        chrome_options.add_argument("test-type")
        chrome_options.add_argument("load-extension=%s" % BITDEF_EXTENSION_PATH)

        self.bitdef_driver = webdriver.Remote(chrome_driver_url, desired_capabilities=chrome_options.to_capabilities())

        ChromeExtensionBase.__init__(self, self.bitdef_driver)
        #self.driver.set_window_size(600, 600)
        self.bitdef_driver.set_window_size(600, 600)

        #ensure that there is only one open tab
        original_handle = self.bitdef_driver.current_window_handle
        for win_handle in self.bitdef_driver.window_handles:
            if not win_handle == original_handle:
                self.bitdef_driver.switch_to.window(win_handle)
                self.bitdef_driver.close()
        self.bitdef_driver.switch_to.window(original_handle)

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
        logging.critical('Window handle selenium: %s' % self.bitdef_driver.title)
        window_handle = self.AUTOIT.WinGetHandle(self.bitdef_driver.title)
        logging.critical('window_handle = %s' % window_handle)
        autoit_cmd = ' '.join([SCREEN_CAPTURE_CMD, output_file, window_handle, str(_BITDEF_LEFT), str(_BITDEF_TOP),
                               str(_BITDEF_RIGHT), str(_BITDEF_BOTTOM)])
        logging.critical(autoit_cmd)
        ShellExecutor.run_wait_standalone(autoit_cmd, env=False)
        '''

        output_file = self.take_screenshot_autoit(self.bitdef_driver, _BITDEF_LEFT, _BITDEF_TOP, _BITDEF_RIGHT,
                                                  _BITDEF_BOTTOM)

        if not os.path.isfile(output_file):
            raise Exception('output file: %s not found!' % output_file)
            #todo: handle this

        #pass -- image is red
        if self.are_images_identical(RED_SAMPLE, output_file):
            return ChromeExtensionBase.return_success_data("RED")

        #pass -- image is green
        if self.are_images_identical(GREEN_SAMPLE, output_file):
            return ChromeExtensionBase.return_success_data("GREEN")

        return ChromeExtensionBase.return_not_defined_data("UNKNOWN")

'''
def bitdef_task(urls):

    chrome_driver_url = "http://localhost:9515"

    logging.info('Loading chrome driver with extension...')

    product = Bitdefender(chrome_driver_url)

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

def internal_bitdefender_task(urls):
    chrome_driver_url = "http://localhost:9515"
    logging.info('Loading chrome driver with extension...')
    product = Bitdefender(chrome_driver_url)

    results = []
    for url in urls:
        result = product.analyze_url(url)
        result["url"] = url
        result["competitor"] = module_name
        results.append(result)

    pprint.pprint(results)
    product.driver.close()

    return results

def internal_bitdefender_task_granular(urls):
    """
    yields url results one at a time
    :param urls:
    :return:
    """
    chrome_driver_url = "http://localhost:9515"
    logging.info('Loading chrome driver with extension...')
    product = Bitdefender(chrome_driver_url)

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
    #results = bitdef_task(['http://serasaexperian.info/', 'http://amazon.com', 'http://finlawfirm.com/images/j79.exe '])
    results = internal_bitdefender_task_granular(['http://amazon.com'])
    logging.error(results)


'''@app.task(name=task_name, ignore_result=True)
def bitdefender_task(urls):
    """
    Task based on Avira plugin
    :return:
    """
    results = []
    try:
        results = internal_bitdefender_task(urls)
    finally:
        app.send_task(RESULTS_TASK, [results], broker=RABBITMQ_BROKER, backend=RABBITMQ_BACKEND,  queue=RESULTS_QUEUE)
'''

@app.task(name=task_name, ignore_result=True)
def bitdefender_task(urls):
    """
    sends results tasks per URL
    :param urls:
    """
    for results in internal_bitdefender_task_granular(urls):
        app.send_task(RESULTS_TASK, [results], broker=RABBITMQ_BROKER, backend=RABBITMQ_BACKEND,  queue=RESULTS_QUEUE)
