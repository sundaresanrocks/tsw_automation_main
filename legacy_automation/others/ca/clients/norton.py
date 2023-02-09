import logging
import pprint
from bs4 import BeautifulSoup
from ca.clients.base import ChromeExtensionBase, SCREEN_CAPTURE_CMD
from libx.process import ShellExecutor

__author__ = 'manoj'

import os
import time
from io import BytesIO

from selenium import webdriver, selenium
from selenium.webdriver.chrome.options import Options
from PIL import Image
import math
import operator
from functools import reduce

from celery import Celery
from ca.clients.base import ChromeExtensionBase
from ca.ca_config import RABBITMQ_BROKER, RABBITMQ_BACKEND, TEXT_GRAY, TEXT_GREEN, TEXT_RED, TEXT_YELLOW
from ca.ca_config import RESULTS_QUEUE, RESULTS_TASK, SUPPORTED_TASKS


module_name = os.path.basename(__file__).partition('.')[0]
task_name = SUPPORTED_TASKS['norton']
app = Celery(task_name, backend=RABBITMQ_BACKEND, broker=RABBITMQ_BROKER, queue='norton')


_NORTON_LEFT = '537'
_NORTON_TOP = '49'
_NORTON_RIGHT = '555'
_NORTON_BOTTOM = '67'
GREEN_COLOR_TUPLE = (0, 255, 0)
GREEN_PIXEL_COUNT = 38
RED_COLOR_TUPLE = (237, 28, 36)
RED_PIXEL_COUNT = 38
GRAY_COLOR_TUPLE = (204, 204, 204)
GRAY_PIXEL_COUNT = 38

norton_uid = 'nppllibpnmahfaklnpggkibhkapjkeob'
NORTON_EXTENSION_PATH = r'c:\tsw-ui\ca\norton'
#based on extension of file, file type would be determined by auto it
TEMP_FILE_NAME = "norton-temp-file.bmp"
TEMP_FOLDER = r'c:\tsw-ui\ca\tmp'
GREEN_SAMPLE = r'C:\src\ca\clients\clients_res\norton_res\green_sample.bmp'
RED_SAMPLE = r'C:\src\ca\clients\clients_res\norton_res\red_sample.bmp'
YELLOW_SAMPLE = r'C:\src\ca\clients\clients_res\norton_res\yellow_sample.bmp'


class Norton(ChromeExtensionBase):
    """

    """

    def __init__(self, chrome_driver_url):
        #todo: check if extension path exists. if not, handle appropriately
        chrome_options = Options()
        chrome_options.add_argument("test-type")
        chrome_options.add_argument("load-extension=%s" % NORTON_EXTENSION_PATH)

        self.norton_driver = webdriver.Remote(chrome_driver_url, desired_capabilities=chrome_options.to_capabilities(), )

        ChromeExtensionBase.__init__(self, self.norton_driver)
        self.driver.set_window_size(600, 600)
        self.set_capability_custom_download_location(self.norton_driver)

    def analyze_url(self, url):

        window_handle = self.AUTOIT.WinGetHandle(self.driver.title)
        logging.critical('Current window handle: %s'%window_handle)
        self.driver.get(url)
        #self.focus_browser(window_handle)
        time.sleep(2)
        if self.autoit_window_exists('[TITLE:Save As; CLASS:#32770]'):
            self.autoit_cancel_download()

        '''count = 0
        output_file = os.path.join(TEMP_FOLDER, TEMP_FILE_NAME)
        while os.path.isfile(output_file):
            try:
                os.unlink(output_file)
            except:
                output_file = '%s-' % count + TEMP_FILE_NAME
                count += 1

        ## find the window handle
        # window_handle = AUTOIT.WinGetHandle("Calculator")
        window_handle = self.AUTOIT.WinGetHandle(self.driver.title)
        #todo: take care of negative condition when no window could be found with the title
        # (Possible for pages that dynamically change the window titles)

        ## execute the command to capture the screen shot
        autoit_cmd = ' '.join([SCREEN_CAPTURE_CMD, output_file, window_handle, _NORTON_LEFT, _NORTON_TOP,
                              _NORTON_RIGHT, _NORTON_BOTTOM])
        logging.critical(autoit_cmd)
        ShellExecutor.run_wait_standalone(autoit_cmd, env=False)
        '''

        '''generate screenshot names from urls(for getting different samples)
        output_file = os.path.join(TEMP_FOLDER, '%s.bmp'%url[7:16])
        output_file = self.take_screenshot_autoit(self.norton_driver , _NORTON_LEFT, _NORTON_TOP, _NORTON_RIGHT,
                                                  _NORTON_BOTTOM, output_file)
        '''

        output_file = self.take_screenshot_autoit(self.norton_driver , _NORTON_LEFT, _NORTON_TOP, _NORTON_RIGHT,
                                                  _NORTON_BOTTOM)

        if not os.path.isfile(output_file):
            raise Exception('output file not found!')
            #todo: handle this

        '''#Method1: checking the color of the strip when it's monochrome
        #### Deal with blocked URL
        image = Image.open(open(output_file, 'rb'))
        image = image.convert("RGB")
        colors = image.getcolors()
        logging.critical(colors)
        if colors:
            if colors[0][0] == RED_PIXEL_COUNT and colors[0][1] == RED_COLOR_TUPLE:
                return ChromeExtensionBase.return_success_data("RED")
            if colors[0][0] == GREEN_PIXEL_COUNT and colors[0][1] == GREEN_COLOR_TUPLE:
                return ChromeExtensionBase.return_success_data("GREEN")
            # if colors[0][0] == YELLOW_PIXEL_COUNT and colors[0][1] == YELLOW_COLOR_TUPLE:
            #     return ChromeExtensionBase.return_success_data("YELLOW")
            if colors[0][0] == GRAY_PIXEL_COUNT and colors[0][1] == GRAY_COLOR_TUPLE:
                return ChromeExtensionBase.return_success_data("GRAY")
        '''

        #Method2: Checking the complete against a sample
        #pass -- response is red
        '''
        h1 = Image.open(RED_SAMPLE).histogram()
        h2 = Image.open(output_file).histogram()
        rms = math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
        '''
        if self.are_images_identical(RED_SAMPLE, output_file):
            return ChromeExtensionBase.return_success_data("RED")

        #pass -- response is yellow
        '''
        h1 = Image.open(YELLOW_SAMPLE).histogram()
        h2 = Image.open(output_file).histogram()
        rms = math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
        '''
        if self.are_images_identical(YELLOW_SAMPLE, output_file):
            return ChromeExtensionBase.return_success_data("YELLOW")

        #pass -- response is green
        '''
        h1 = Image.open(GREEN_SAMPLE).histogram()
        h2 = Image.open(output_file).histogram()
        rms = math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
        '''
        if self.are_images_identical(GREEN_SAMPLE, output_file):
            return ChromeExtensionBase.return_success_data("GREEN")


        return ChromeExtensionBase.return_not_defined_data("UNKNOWN")


def internal_norton_task(urls):
    chrome_driver_url = "http://localhost:9515"
    logging.info('Loading chrome driver with extension...')
    product = Norton(chrome_driver_url)

    results = []
    for url in urls:
        # this is not working product.reset_browser_tab()
        result = product.analyze_url(url)
        result["url"] = url
        result["competitor"] = module_name
        results.append(result)

    pprint.pprint(results)
    product.driver.close()

    return results

def internal_norton_task_granular(urls):
    """
    yields url results one at a time
    :param urls:
    :return:
    """
    chrome_driver_url = "http://localhost:9515"
    logging.info('Loading chrome driver with extension...')
    product = Norton(chrome_driver_url)

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

if __name__ == '__main__':
    #results = internal_norton_task(['http://serasaexperian.info/', 'http://amazon.com', 'http://finlawfirm.com/images/j79.exe '])
    '''
    results = internal_norton_task_granular(['http://finlawfirm.com/images/j79.exe', 'http://www.tophackingtools.com/', 'http://www.freeidealhacks.com/', 'https://ninite.com/operaChromium/', 'http://hacktoolsoftware.com/', 'http://www.gamespot.com/'])
    logging.error(results)
    '''
    for results in internal_norton_task_granular(['http://finlawfirm.com/images/j79.exe', 'http://www.tophackingtools.com/', 'http://www.freeidealhacks.com/', 'https://ninite.com/operaChromium/', 'http://hacktoolsoftware.com/', 'http://www.gamespot.com/']):
        pass

'''
@app.task(name=task_name, ignore_result=True)
def norton_task(urls):
    """
    Task based on Norton plugin
    :return:
    """
    results = []
    try:
        results = internal_norton_task(urls)
    finally:
        app.send_task(RESULTS_TASK, [results], broker=RABBITMQ_BROKER, backend=RABBITMQ_BACKEND,  queue=RESULTS_QUEUE)
'''

@app.task(name=task_name, ignore_result=True)
def norton_task(urls):
    """
    sends results tasks per URL
    :param urls:
    """
    for results in internal_norton_task_granular(urls):
        app.send_task(RESULTS_TASK, [results], broker=RABBITMQ_BROKER, backend=RABBITMQ_BACKEND,  queue=RESULTS_QUEUE)