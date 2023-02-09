"""
Sandbox Environment
*******************

Create a sandbox environment and execute each test in it.

Collect and store all data/artifacts in the sandbox folder(current folder)

"""

import json
import pprint
from json_tools import diff as json_diff
from lib.exceptions import TestFailure

__author__ = 'manoj'

import os
import logging
import unittest
import datetime
from path import Path

import runtime

import framework.log
import libx
import libx.filex
import libx.archives


class TestData:
    """Class to pass test data to data driven tests"""

    def __init__(self, **entries):
        """assign the values to self!!"""
        self.__dict__.update(entries)


class SandboxedTest(unittest.TestCase):
    """All tests must instantiate from this"""

    # def setUp(self):
    #     super(SandboxedTest, self).setUp()
    #     try:
    #         # _class_name = str(self).rpartition('(')[2].rpartition('.')[2][:-1]
    #         _class_str = str(str(self).rpartition('(')[2].rpartition(')')[0])
    #         if _class_str.startswith('tests.'):
    #             _class_str = _class_str.replace('tests.', '', 1)
    #         _class_name = _class_str.replace('.', '/', _class_str.count('.') - 1)
    #
    #     except:
    #         _class_name = 'default.Suite'
    #         msg = 'WARNING: Unable to find suite name in sandbox. Using default in %s' % str(self)
    #         logging.warning(msg)
    #     try:
    #         _func_name = self._testMethodName
    #     except:
    #         _func_name = 'default_test'
    #         msg = 'WARNING: Unable to find test name in sandbox. using default in %s' % str(self)
    #         logging.warning(msg)
    #     self.sandbox = SandboxTestEnvironment(_class_name, _func_name)
    #     # ### Setup sandbox ####
    #     self.sandbox.setup_sandbox()
    #     # ### Setup new logger ####
    #     _log_set = framework.log.LogSettings
    #     fh = logging.FileHandler(_log_set.log_sandbox_file_name)
    #     fh.setLevel(_log_set.log_sandbox_file_level)
    #     fh.setFormatter(logging.Formatter(_log_set.log_sandbox_format,
    #                                       _log_set.log_sandbox_format_time))
    #     self.sandbox_log_handler = fh
    #     logging.addHandler(fh)
    #
    # def tearDown(self):
    #     super(SandboxedTest, self).tearDown()
    #     self.sandbox.exit_sandbox()
    #     try:
    #         self.duration = self.sandbox.time_end - self.sandbox.time_start
    #     except AttributeError:
    #         self.duration = datetime.timedelta(0)
    #     logging.removeHandler(self.sandbox_log_handler)  # remove file logger

    def assert_json_equal(self, expected_dict, actual_dict):
        """

        :param expected_dict: Expected json data for comparison
        :param actual_dict: Actual json data for comparison
        :return: [] when both dicts are equal
        :raises: Test Failure on mismatch
        """
        diff = json_diff(expected_dict, actual_dict)
        if diff:
            err_msg = 'Json dict data mismatch! patch: %s' % pprint.pformat(diff)
            logging.error(err_msg)
            # logging.error('ACTUAL DICT: %s'%actual_dict)
            # logging.error('EXPECTED DICT: %s'%expected_dict)
            raise TestFailure(err_msg)
        logging.info('Json dict data matches!')

    def assert_json_file_equal(self, expected_json_file_path, actual_json_file_path):
        """

        :param expected_json_file_path: Expected json file path for comparison
        :param actual_json_file_path: Actual json file path for comparison
        :return: [] when both dicts are equal
        :raises: Test Failure on mismatch
        """
        logging.info('Actual json file: %s' % os.path.abspath(actual_json_file_path))
        logging.info('Expected json file: %s' % os.path.abspath(expected_json_file_path))
        act_json = json.load(open(actual_json_file_path))
        exp_json = json.load(open(expected_json_file_path))
        self.assert_json_equal(act_json, exp_json)


class SandboxTestEnvironment(object):
    """Class that does sandboxing"""

    # todo: change component to more meaningful thing
    def __init__(self, component, testcase_id):
        self.time_start = datetime.datetime.now()
        if not isinstance(testcase_id, str):
            raise Exception('Sandbox: testcase_id should be string')
        if not isinstance(component, str):
            raise Exception('Sandbox: component should be string')
        if (not testcase_id) or len(str(testcase_id)) <= 0:
            raise Exception("Sandbox: Wrong input parameters to the create " +
                            "Test Environment. Need Test case id")
        if (not component) or len(str(component)) <= 0:
            raise Exception("Sandbox: Wrong input parameters to the create " +
                            "Test Environment. Need component")
        self._last_dir = os.getcwd()
        self._sandbox_dir = ''
        self.component = str(component)
        self.testcase_id = str(testcase_id)
        self.run_id = str(TestInfo.run_id)
        self.jenkins_id = str(TestInfo.jenkins_id)

    def setup_sandbox(self):
        """
        Will create the sandbox test execution directory.
        Will change to the target directory.
        .. note: To be called at the begining each test case
        """

        self._last_dir = os.getcwd()
        self._sandbox_dir = tcdir = self.get_sandbox_dir()
        if os.path.isdir(tcdir):
            _tf = open(tcdir + '/' + 'sandbox.log', 'a', encoding='utf-8')
            _tf.write('Archive time: ' + str(datetime.datetime.now()))
            _tf.close()

            archive_file = config._archive_path + '/' + self.run_id + '-' + self.jenkins_id + '/' + self.component + \
                '/' + libx.filex.slugify(self.testcase_id)[:100] + '_' + libx.filex.get_file_timestamp()

            if os.path.isfile(archive_file):
                archive_file = archive_file + libx.filex.get_file_timestamp()

            logging.debug("Sandbox: dir exists: %s \narchiving it to:%s " % (tcdir, archive_file))

            libx.archives.zip(archive_file, tcdir)
            logging.debug("Sandbox: Previous execution is archived in %s" % archive_file)

            Path(tcdir).rmtree_p()

        try:
            Path(tcdir).mkdir()
        except:
            msg = "Sandbox: Unable to create directory: %s" % tcdir
            logging.error(msg)
            raise

        logging.info("Sandbox: Changing current dir to: %s" % tcdir)
        os.chdir(tcdir)

        with open('sandbox.log', 'a', encoding='utf-8') as fp:
            fp.write('\nSandbox: Initialized at %s' % str(self.time_start))
        return self

    def exit_sandbox(self):
        """
        Will run cleanup if needed after sandbox is created.
        Should be called in cleanup() of the testcase
        """
        # todo: remove exceptions
        self.time_end = datetime.datetime.now()

        if (os.path.normcase(os.path.normpath(self._sandbox_dir)) == os.path.normcase(os.path.normpath(os.getcwd()))):
            with open('sandbox.log', 'a', encoding='utf-8') as fp:
                # write end time
                fp.write('\nSandbox: End at %s' % str(self.time_end))
        else:
            # log a warning about dir change
            msg = 'Sandbox: working directory changed in test case from sandbox directory: %s to: %s' % (
                self._sandbox_dir, os.getcwd())
            logging.warning(msg)
        logging.debug("Sandbox: Changing current dir to %s" % self._last_dir)
        if self._last_dir:
            # change to this _last_dir
            os.chdir(self._last_dir)
        else:
            # log a warn
            msg = 'Sandbox: Unable to change to base directory from sandbox directory %s' % self._sandbox_dir
            logging.warning(msg)
            # raise Exception (msg)
        return True

    def get_sandbox_dir(self):
        """
        Returns the sandbox test case execution directory

        .. note: To be called at end of each test case
        """
        if self.testcase_id:
            return runtime.exec_path \
                   + '/' + self.run_id \
                   + '/' + self.component \
                   + '/' + libx.filex.slugify(self.testcase_id)[:100]
            # + '-' + self.jenkins_id \

    @staticmethod
    def delete_file(file_name):
        """ Delete the given file_name

        :param file_name:
        :return:
        """
        if os.path.isfile(file_name):
            os.remove(file_name)
            logging.debug('Delete Log file: %s' % file_name)

    @staticmethod
    def copy_modified_files(folder_name, time_start, starts_with_filter=''):
        """ Copies new and modified files to sandbox based on folder_name

        :param folder_name: Input folder name
        :param time_start: datetime object
        :param starts_with_filter: Filter
        :return:
        """
        if not isinstance(time_start, datetime.datetime):
            raise TypeError('time_start must be datetime object')
        if not isinstance(folder_name, str):
            raise TypeError('folder_name must be str')
        if not isinstance(starts_with_filter, str):
            raise TypeError('starts_with_filter must be str')

        for tmp, dirs, files in os.walk(folder_name):
            for basename in files:
                print('sandbox file copy: %s' % basename)
                if not basename.startswith(starts_with_filter):
                    continue
                _file = os.path.join(tmp, basename)
                file_time_stamp = datetime.datetime.fromtimestamp(os.path.getmtime(_file))
                stat = os.stat(_file)
                if file_time_stamp > time_start:
                    # create new name for files that with same base name in different folders
                    new_file_name = './' + basename
                    while True:
                        if os.path.isfile(new_file_name):
                            new_file_name += '_tmp'
                            break

                    # copy the file
                    try:
                        Path.copy(_file, new_file_name)
                        logging.debug('Sandbox: copy modified file: %s', _file)
                    except:
                        logging.warning('Sandbox: copy failed for file: %s', _file)

    @staticmethod
    def copy_file_to_sandbox(file_name):
        """ Copies given file to sandbox

        :param file_name:
        :return: bool
        """

        if os.path.isfile(file_name):
            Path.copy(file_name, '.')
            logging.debug('Sandbox: File %s copied to sandbox', file_name)
            return True
        else:
            logging.warning('Sandbox: File not found: %s', file_name)
            return False
