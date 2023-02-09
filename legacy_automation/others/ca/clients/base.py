import logging
import os
import time

from libx.process import ShellExecutor
from selenium.webdriver.common.keys import Keys
import math
import operator
from functools import reduce
from PIL import Image

__author__ = 'manoj'

AUTOIT_EXE = r'"C:\Program Files (x86)\AutoIt3\AutoIt3.exe" '
AU3_SCREEN_CAPTURE = r"c:\src\ca\screen-capture.au3"
SCREEN_CAPTURE_CMD = "%s %s " % (AUTOIT_EXE, AU3_SCREEN_CAPTURE)
TEMP_FOLDER = r'c:\tsw-ui\ca\tmp'
TEMP_FILE_NAME = "autoit-temp-file.bmp"


class ChromeExtensionBase:
    def __init__(self, driver):

        #### removes warning message regarding the certificate
        import win32com.client
        self.AUTOIT = win32com.client.Dispatch("AutoItX3.Control")

        logging.info('Closing first time popup from extension.')
        #todo: check if file on the local system works
        driver.get('http://yahoo.com')
        driver.get('http://amazon.com')
        driver.get('http://google.com')
        self.AUTOIT.WinActivate(driver.title)
        self.AUTOIT.Send("{ENTER}")

        self.autoit_confirm_new_extension()

        logging.info('Setting window size and position...')
        driver.set_window_position(0, 0)
        driver.set_window_size(150, 250)
        time.sleep(2)

        self.driver = driver
        logging.info('Initialization complete for product: %s' % self.__class__.__name__)

    def autoit_confirm_new_extension(self):

        count = 0
        while self.AUTOIT.WinExists("Confirm New Extension"):
            count += 1
            # just a precaution to close any other window with same title from previous sessions
            if count > 10:
                raise Exception("Unable to load extension. Maximum reties - 10")
            self.AUTOIT.WinActivate("Confirm New Extension")
            time.sleep(1)

            self.AUTOIT.Send("{TAB}{ENTER}")
            time.sleep(1)

    def set_capability_custom_download_location(self, driver):
        """configures browser instance to ask for download location so that it can be accepted/cancelled"""
        driver.get('chrome://settings-frame/')
        """
        if os.path.isfile(os.path.join(TEMP_FOLDER, 'temp-page-source')):
            os.unlink(os.path.join(TEMP_FOLDER, 'temp-page-source'))
        with open(os.path.join(TEMP_FOLDER, 'temp-page-source'), mode='w') as ps:
            ps.write(driver.page_source)
        """
        driver.find_element_by_id('advanced-settings-expander').click()
        if not driver.find_element_by_id('prompt-for-download').is_selected():
            driver.find_element_by_id('prompt-for-download').click()

    def autoit_window_exists(self, win_title_match_criteria, win_text_match_criteria = None, retries_no = 10,
                             wait_period = 1):
        retries = 0
        while retries < retries_no:
            if win_text_match_criteria == None:
                winexists = self.AUTOIT.WinExists("%s"%(win_title_match_criteria))
            else:
                winexists = self.AUTOIT.WinExists("%s, %s"%(win_title_match_criteria, win_text_match_criteria))
            logging.info('Match criteria: Title definition: %s Text Definition: %s' %(win_title_match_criteria,
                                                                                      win_text_match_criteria))
            logging.info('Winexists = %s'%winexists)
            if winexists:
                logging.info('Window found.')
                return True
            logging.info('Window not found. Waiting for 1 second.')
            retries += 1
            time.sleep(wait_period)
        return False

    def autoit_cancel_download(self):
        """cancels download if a manual prompt for where to download is presented"""
        count=0
        while self.AUTOIT.WinExists("Save As"):
            count += 1
            if count>10:
                raise Exception('Unable to close download prompt.')
            self.AUTOIT.WinActivate("Save As")
            time.sleep(1)
            self.AUTOIT.Send("{TAB}{ENTER}")

    def run_autit3(self, au3_path, cmd_args):
        """
        Runs autoit 3
        :param au3_path: Path to au3 script file 
        :param cmd_args: Arguments to the script
        :return:
        """
        if not os.path.isfile(au3_path):
            raise FileNotFoundError(au3_path)
        
        exec_cmd = ' '.join([AUTOIT_EXE, au3_path, cmd_args])
        logging.critical(exec_cmd)
        ShellExecutor.run_wait_standalone(exec_cmd)

    def reset_browser_tab(self):
        body = self.driver.find_element_by_tag_name("body")
        body.send_keys(Keys.CONTROL + 't')
        original_handle = self.driver.current_window_handle
        for win_handle in self.driver.window_handles:
            if not win_handle == original_handle:
                self.driver.switch_to.window(win_handle)

    def are_images_identical(self, expected, actual):
        h1 = Image.open(expected).histogram()
        h2 = Image.open(actual).histogram()
        rms = math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
        if rms == 0:
            return True
        else:
            return False

    def take_screenshot_autoit(self, driver, left, top, right, bottom, output_file=None):
        count=0
        if output_file == None:
            output_file = output_file = os.path.join(TEMP_FOLDER, TEMP_FILE_NAME)
        while os.path.isfile(output_file):
            try:
                os.unlink(output_file)
            except:
                output_file = '%s-' % count + TEMP_FILE_NAME
                count += 1
        logging.critical('Window handle selenium: %s' % self.driver.title)
        window_handle = self.AUTOIT.WinGetHandle(self.driver.title)
        logging.critical('window_handle = %s' % window_handle)
        autoit_cmd = ' '.join([SCREEN_CAPTURE_CMD, output_file, window_handle, str(left), str(top), str(right),
                               str(bottom)])
        logging.critical(autoit_cmd)
        ShellExecutor.run_wait_standalone(autoit_cmd, env=False)
        return output_file

    @staticmethod
    def return_success_data(data):
        return {"status": "success",
                "data": data}

    @staticmethod
    def return_fail_data(data):
        return {"status": "fail",
                "data": data}

    @staticmethod
    def return_not_defined_data(data):
        return {"status": "not defined",
                "data": data}