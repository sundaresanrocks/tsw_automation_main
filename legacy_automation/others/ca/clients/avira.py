import logging
import pprint
import os
import time
from io import BytesIO
from libx.process import ShellExecutor
import math
import operator
from functools import reduce

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from bs4 import BeautifulSoup

from celery import Celery
from ca.clients.base import ChromeExtensionBase
from ca.ca_config import RABBITMQ_BROKER, RABBITMQ_BACKEND, TEXT_GRAY, TEXT_GREEN, TEXT_RED, TEXT_YELLOW
from ca.ca_config import RESULTS_QUEUE, RESULTS_TASK, SUPPORTED_TASKS


module_name = os.path.basename(__file__).partition('.')[0]
task_name = SUPPORTED_TASKS['avira']
app = Celery(task_name, backend=RABBITMQ_BACKEND, broker=RABBITMQ_BROKER, queue='avira')

__author__ = 'manoj'

_AVIRA_LEFT = 51
_AVIRA_TOP = 0
_AVIRA_RIGHT = 124
_AVIRA_BOTTOM = 7
GREEN_COLOR_TUPLE = (162, 204, 146)

AVIRA_CROP_BOX = (_AVIRA_LEFT, _AVIRA_TOP, _AVIRA_RIGHT, _AVIRA_BOTTOM)
GREEN_PIXEL_COUNT = (_AVIRA_BOTTOM - _AVIRA_TOP) * (_AVIRA_RIGHT - _AVIRA_LEFT)

avira_uid = 'flliilndjeohchalpbbcdekjklbdgfkk'
avira_version = '1.1.17_0'
avira_ext_local = 'C:/Users/' + os.getlogin() + '/AppData/Local/Google/Chrome SxS/User Data/Default/Extensions/' \
                  + avira_uid + '/' + avira_version

AVIRA_EXTENSION_PATH = r'c:\tsw-ui\ca\avira'

TEMP_FOLDER = r'c:\tsw-ui\ca\tmp'
TEMP_FILE_NAME = r'avira-temp-file.bmp'
AUTOIT_EXE = r'"C:\Program Files (x86)\AutoIt3\AutoIt3.exe" '
AU3_SCREEN_CAPTURE = r"c:\src\ca\screen-capture.au3"
SCREEN_CAPTURE_CMD = "%s %s " % (AUTOIT_EXE, AU3_SCREEN_CAPTURE)
_AVIRA_LEFT = 92
_AVIRA_TOP = 77
_AVIRA_RIGHT = 221
_AVIRA_BOTTOM = 83
GREEN_SAMPLE = r'C:\src\ca\clients\clients_res\avira_res\green_sample.bmp'


class Avira(ChromeExtensionBase):
    """

    """

    def __init__(self, chrome_driver_url):
        #todo: check if extension path exists. if not, handle appropriately
        chrome_options = Options()
        chrome_options.add_argument("test-type")
        chrome_options.add_argument("load-extension=%s" % AVIRA_EXTENSION_PATH)

        self.avira_driver = webdriver.Remote(chrome_driver_url, desired_capabilities=chrome_options.to_capabilities())

        ChromeExtensionBase.__init__(self, self.avira_driver)
        self.driver.set_window_size(100, 215)

    def analyze_url(self, url):
        logging.info('New URL: %s' % url)
        self.driver.get(url)
        time.sleep(2)

        #### Deal with blocked URL
        if self.driver.title == 'Blocked':
            span_list = BeautifulSoup(self.driver.page_source).find_all('span')
            if span_list:
                if ([True for span in span_list
                     if 'Avira prevents you from opening a potentially harmful website' in span]):
                    return ChromeExtensionBase.return_success_data("RED")

        #### Deal with a Good URL
        '''#self.avira_driver.switch_to.frame(self.avira_driver.find_element_by_xpath("//iframe[@src='chrome-extension://flliilndjeohchalpbbcdekjklbdgfkk/html/top.html#minimized']"))
        for window_handle in self.avira_driver.window_handles:
            self.avira_driver.switch_to.window(window_handle)
            ispresent = len(self.avira_driver.find_elements_by_xpath("//iframe[@src='chrome-extension://flliilndjeohchalpbbcdekjklbdgfkk/html/top.html#minimized']")) > 0
            if ispresent:
                logging.critical('Found the extension frame')
                self.avira_driver.switch_to.frame(self.avira_driver.find_element_by_id('abs-top-frame'))
                break
        #image = Image.open(BytesIO(self.driver.get_screenshot_as_png()))

        image = Image.open(BytesIO(self.avira_driver.get_screenshot_as_png()))
        image = image.convert("RGB")
        output_file = os.path.join(TEMP_FOLDER, '%s.bmp'%url[7:-1])
        txtoutput_file = os.path.join(TEMP_FOLDER, '%s.txt'%url[7:-1])
        logging.critical('page source type %s'%type(self.avira_driver.page_source))
        with open(txtoutput_file, 'w') as pagesourcefile:
            pagesourcefile.write(self.avira_driver.page_source)
        logging.critical('saving to %s'%output_file)
        image.save(output_file, format='BMP')
        region = image.crop(AVIRA_CROP_BOX)
        #colors = region.getcolors()
        colors = image.getcolors()
        if colors:
            if colors[0][0] == GREEN_PIXEL_COUNT and colors[0][1] == GREEN_COLOR_TUPLE:
                return ChromeExtensionBase.return_success_data(TEXT_GREEN)
        '''

        #return ChromeExtensionBase.return_not_defined_data("UNKNOWN")
        return ChromeExtensionBase.return_success_data("GREEN")


def internal_avira_task(urls):
    chrome_driver_url = "http://localhost:9515"
    logging.info('Loading chrome driver with extension...')
    product = Avira(chrome_driver_url)
    results = []
    for url in urls:
        new_result = product.analyze_url(url)
        new_result["url"] = url
        new_result["competitor"] = module_name
        results.append(new_result)
    pprint.pprint(results)
    product.driver.close()
    return results

def internal_avira_task_granular(urls):
    """
    yields url results one at a time
    :param urls:
    :return:
    """
    chrome_driver_url = "http://localhost:9515"
    logging.info('Loading chrome driver with extension...')
    product = Avira(chrome_driver_url)

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


'''
@app.task(name=task_name, ignore_result=True)
def avira_task(urls):
    """
    Task based on Avira plugin
    :return:
    """
    results = []
    try:
        results = internal_avira_task(urls)
    finally:
        app.send_task(RESULTS_TASK, [results], broker=RABBITMQ_BROKER, backend=RABBITMQ_BACKEND,  queue=RESULTS_QUEUE)
'''

@app.task(name=task_name, ignore_result=True)
def avira_task(urls):
    """
    sends results tasks per URL
    :param urls:
    """
    for results in internal_avira_task_granular(urls):
        app.send_task(RESULTS_TASK, [results], broker=RABBITMQ_BROKER, backend=RABBITMQ_BACKEND,  queue=RESULTS_QUEUE)
