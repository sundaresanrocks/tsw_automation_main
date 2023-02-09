"""
=======================
Content Extractor tests
=======================

"""

__author__ = 'abhijeet'

import logging
from unittest.case import SkipTest
import unittest
import uuid
import shutil
import filecmp
import json

from path import Path

import runtime
from libx.process import ShellExecutor
from lib.exceptions import TestFailure
from conf.files import SH
from harvesters.properties import quality_properties
from harvesters.harvester import Harvester
from harvesters.qaharvester import HarvesterQuality


LOCAL_PROP_FILE = Path('content-extractor.properties')
CMD_PARSER_TMPL = SH.content_extractor_driver + ' %(prop)s %(class)s %(in_file)s %(dest_dir)s %(out_file)s'


class ContentExtractorDriver(unittest.TestCase):
    """Content extractor tests using ContentExtractorDriver"""
    default_har_config = HarvesterQuality

    def setUp(self):
        super(ContentExtractorDriver, self).setUp()
        LOCAL_PROP_FILE.remove_p()
        self.har = Harvester(HarvesterQuality())
        self.har.remove_harvester_log()

        ### Skip all test if the shell executable does not exist.
        if not SH.content_extractor_driver.isfile():
            raise SkipTest('Shell script does not exist: %s' % SH.content_extractor_driver)

    def run_content_extractor_test(self, prop_file, class_name, in_file_name, out_file_name, err_str=None):
        if not Path(in_file_name).isfile():
            raise FileNotFoundError('File: %s not found.' % in_file_name)
        if Path(out_file_name).isfile():
            backup_old_file_name = out_file_name + str(uuid.uuid4())
            logging.info('output file:%s exists. Will be renamed to: %s' % (out_file_name, backup_old_file_name))
            shutil.move(out_file_name, backup_old_file_name)
        destination_path = Path().getcwd().joinpath('extractor_destination')
        if destination_path.isfile():
            destination_path.remove()
        if destination_path.isdir():
            destination_path.rmtree_p()
        destination_path.makedirs()

        sto, ste = ShellExecutor.run_wait_standalone(CMD_PARSER_TMPL % {'prop': prop_file,
                                                                        'class': class_name,
                                                                        'in_file': in_file_name,
                                                                        'dest_dir': destination_path,
                                                                        'out_file': out_file_name})

        if ste:
            logging.error('Content Extractor driver execution error: \n %s' % ste)
        stdoe = ste + sto
        if err_str:
            if err_str not in stdoe:
                raise TestFailure('Expected error: %s not found in logs' % err_str)
            else:
                logging.info('Expected error string found in standard out/err stream: %s' % err_str)
            return True
        return stdoe

    def compare_file_lists(self, exp_file_list, exp_file_dir, act_file_list):

        logging.info('Actual file list: %s' % Path(act_file_list).abspath())
        logging.info('Expected file list: %s' % Path(exp_file_list).abspath())
        act_json = json.load(open(act_file_list))
        exp_json = json.load(open(exp_file_list))

        if not (len(exp_json) == len(act_json)):
            raise TestFailure('Number of files does not match expected number. Expected: %d. Actual: %d' % (len(
                exp_json), len(act_json)))
        for filename in act_json:
            clipped_filename = (filename.split('/'))[-1]
            if clipped_filename not in exp_json:
                raise TestFailure('Filename: %s not found in expected file list' % clipped_filename)
            if not filecmp.cmp(Path(exp_file_dir).joinpath(exp_json[exp_json.index(clipped_filename)]), filename):
                raise TestFailure('Actual file: %s does not match expected file: %s' % (filename,
                                  exp_json[exp_json.index(clipped_filename)]))
        logging.info('File lists and content matches!')
        return True


class SystemCommand(ContentExtractorDriver):
    """
    ======================================
    System Command Content Extractor Tests
    ======================================
    """
    content_extractor_name = 'TARGZContentExtractor'
    data_dir = runtime.data_path.joinpath('tsw/harvesters/driver/content_extractors/systemcommand')
    prop_dict_single_command = {'ContentExtractor.className':
                                    'com.securecomputing.sftools.harvester.contentExtractors.'
                                    'SystemCommandContentExtractor',
                                'SystemCommandContentExtractor.commandCount': '1',
                                'ContentExtractor.extractedFileRegex': r'\\.*urls.*\\.txt',
                                'SystemCommandContentExtractor.command':
                                    r'/usr/bin/unrar e -pinfected {{{filename}}} {{{dir}}}'}
    prop_dict_multi_command = {'ContentExtractor.className':
                                   'com.securecomputing.sftools.harvester.contentExtractors.'
                                   'SystemCommandContentExtractor',
                               'SystemCommandContentExtractor.commandCount': '2',
                               'SystemCommandContentExtractor.command.1':
                                    'echo buffercommand',
                               'SystemCommandContentExtractor.command.2':
                                   r'/usr/bin/unrar e -pinfected {{{filename}}} {{{dir}}}',
                               }
    classname = 'com.securecomputing.sftools.harvester.contentExtractors.SystemCommandContentExtractor'

    def test_01(self):
        """TS-3124 : SystemCommandContentExtractor: Positive test case; With SingleCommand single file."""
        prop = quality_properties(properties_as_dict=self.prop_dict_single_command)
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_01')
        in_file = test_data_dir.joinpath('in-01.rar')
        actual_out_file = 'filelist.json'
        exp_out_file = test_data_dir.joinpath('out-01.json')
        exp_file_dir = test_data_dir.joinpath('in-01')

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file)
        self.compare_file_lists(exp_out_file, exp_file_dir, actual_out_file)

    def test_02(self):
        """TS-3125 : SystemCommandContentExtractor: Positive test case: With SingleCommand multiple files."""
        prop = quality_properties(properties_as_dict=self.prop_dict_single_command)
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_02')
        in_file = test_data_dir.joinpath('in-02.rar')
        actual_out_file = 'filelist.json'
        exp_out_file = test_data_dir.joinpath('out-02.json')
        exp_file_dir = test_data_dir.joinpath('in-02')

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file)
        self.compare_file_lists(exp_out_file, exp_file_dir, actual_out_file)

    def test_03(self):
        """TS-3126 : SystemCommandContentExtractor: Positive test case; With MultiCommand single file."""
        prop = quality_properties(properties_as_dict=self.prop_dict_multi_command)
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_03')
        in_file = test_data_dir.joinpath('in-03.rar')
        actual_out_file = 'filelist.json'
        exp_out_file = test_data_dir.joinpath('out-03.json')
        exp_file_dir = test_data_dir.joinpath('in-03')

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file)
        self.compare_file_lists(exp_out_file, exp_file_dir, actual_out_file)

    def test_04(self):
        """TS-3127 : SystemCommandContentExtractor: Positive test case; With MultiCommand multiple files."""
        prop = quality_properties(properties_as_dict=self.prop_dict_multi_command)
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_04')
        in_file = test_data_dir.joinpath('in-04.rar')
        actual_out_file = 'filelist.json'
        exp_out_file = test_data_dir.joinpath('out-04.json')
        exp_file_dir = test_data_dir.joinpath('in-04')

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file)
        self.compare_file_lists(exp_out_file, exp_file_dir, actual_out_file)

    def test_05(self):
        """TS-3128 : SystemCommandContentExtractor: No command count is given."""
        prop = quality_properties(properties_as_dict=self.prop_dict_single_command)
        del prop['SystemCommandContentExtractor.commandCount']
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_05')
        in_file = test_data_dir.joinpath('in-05.rar')
        actual_out_file = 'filelist.json'
        exp_out_file = test_data_dir.joinpath('out-05.json')
        exp_file_dir = test_data_dir.joinpath('in-05')

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file)
        self.compare_file_lists(exp_out_file, exp_file_dir, actual_out_file)

    def test_06(self):
        """TS-3129 : SystemCommandContentExtractor: Command does not contain filename, SingleCommmand"""
        prop = quality_properties(properties_as_dict=self.prop_dict_single_command)
        prop['SystemCommandContentExtractor.command'] = 'echo nofilename {{{dir}}}'
        err_str = 'HarvesterGeneralException: Missing \'{{{filename}}}\' and or \'{{{dir}}}\' in commands.'
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_06')
        in_file = test_data_dir.joinpath('in-06.rar')
        actual_out_file = 'filelist.json'

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file, err_str=err_str)

    def test_07(self):
        """TS-3145 : SystemCommandContentExtractor: Command does not contain directory name, SingleCommmand"""
        prop = quality_properties(properties_as_dict=self.prop_dict_single_command)
        prop['SystemCommandContentExtractor.command'] = 'echo {{{filename}}} butnodir'
        err_str = 'HarvesterGeneralException: Missing \'{{{filename}}}\' and or \'{{{dir}}}\' in commands.'
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_07')
        in_file = test_data_dir.joinpath('in-07.rar')
        actual_out_file = 'filelist.json'

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file, err_str=err_str)

    def test_08(self):
        """TS-3130 : SystemCommandContentExtractor: Command does not contain dir, MultiCommmand"""
        prop = quality_properties(properties_as_dict=self.prop_dict_multi_command)
        prop['SystemCommandContentExtractor.command.2'] = '/usr/bin/unrar e -pinfected {{{filename}}} nodir'
        err_str = 'HarvesterGeneralException: Missing \'{{{filename}}}\' and or \'{{{dir}}}\' in commands.'
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_07')
        in_file = test_data_dir.joinpath('in-07.rar')
        actual_out_file = 'filelist.json'

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file, err_str=err_str)

    def test_09(self):
        """TS-3131 : SystemCommandContentExtractor: Command does not contain filename, MultiCommmand."""
        prop = quality_properties(properties_as_dict=self.prop_dict_multi_command)
        prop['SystemCommandContentExtractor.command.2'] = '/usr/bin/unrar e -pinfected nofilename {{{dir}}}'
        err_str = 'HarvesterGeneralException: Missing \'{{{filename}}}\' and or \'{{{dir}}}\' in commands.'
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_09')
        in_file = test_data_dir.joinpath('in-09.rar')
        actual_out_file = 'filelist.json'

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file, err_str=err_str)

    def test_10(self):
        """TS-3132 : SystemCommandContentExtractor: Unable to run command"""
        prop = quality_properties(properties_as_dict=self.prop_dict_single_command)
        prop['SystemCommandContentExtractor.command'] = 'exho {{{filename}}} {{{dir}}}'
        err_str = 'HarvesterGeneralException: Unable to run command'
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_10')
        in_file = test_data_dir.joinpath('in-10.rar')
        actual_out_file = 'filelist.json'

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file, err_str=err_str)

    def test_11(self):
        """TS-3133 : SystemCommandContentExtractor: System command failed(IOException in executing command)"""
        prop = quality_properties(properties_as_dict=self.prop_dict_multi_command)
        prop['SystemCommandContentExtractor.command.2'] = '/usr/bin/unwar e -pinfected {{{filename}}} {{{dir}}}'
        err_str = 'HarvesterGeneralException: System command failed'
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_11')
        in_file = test_data_dir.joinpath('in-11.rar')
        actual_out_file = 'filelist.json'

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file, err_str=err_str)


class TARGZ(ContentExtractorDriver):
    """
    =============================
    TarGZ Content Extractor Tests
    =============================
    """
    content_extractor_name = 'TARGZContentExtractor'
    data_dir = runtime.data_path.joinpath('tsw/harvesters/driver/content_extractors/targz')
    prop_dict = {'ContentExtractor.className':
                     'com.securecomputing.sftools.harvester.contentExtractors.TarGZContentExtractor',
                 'ContentExtractor.extractedFileRegex': '.*.csv'}
    classname = 'com.securecomputing.sftools.harvester.contentExtractors.TarGZContentExtractor'

    def test_01(self):
        """TS-3108 : TARGZContentExtractor: Positive test case. Proper tar.gz with single file."""
        prop = quality_properties(properties_as_dict=self.prop_dict)
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_01')
        in_file = test_data_dir.joinpath('in-01.tar.gz')
        actual_out_file = 'filelist.json'
        exp_out_file = test_data_dir.joinpath('out-01.json')
        exp_file_dir = test_data_dir.joinpath('in-01')

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file)
        self.compare_file_lists(exp_out_file, exp_file_dir, actual_out_file)

    def test_02(self):
        """TS-3109 : TARGZContentExtractor: Positive test case. Proper tar.gz with multiple files in archive."""
        prop = quality_properties(properties_as_dict=self.prop_dict)
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_02')
        in_file = test_data_dir.joinpath('in-02.tar.gz')
        actual_out_file = 'filelist.json'
        exp_out_file = test_data_dir.joinpath('out-02.json')
        exp_file_dir = test_data_dir.joinpath('in-02')

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file)
        self.compare_file_lists(exp_out_file, exp_file_dir, actual_out_file)

    def test_03(self):
        """TS-3120 : TARGZContentExtractor: Archive has txt files and extracted file regex is csv."""
        prop = quality_properties(properties_as_dict=self.prop_dict)
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_03')
        in_file = test_data_dir.joinpath('in-03.tar.gz')
        actual_out_file = 'filelist.json'
        exp_out_file = test_data_dir.joinpath('out-03.json')
        exp_file_dir = test_data_dir.joinpath('in-03')

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file)
        self.compare_file_lists(exp_out_file, exp_file_dir, actual_out_file)

    def test_04(self):
        """TS-3121 : TARGZContentExtractor: Tar file as input instead of tar.gz"""
        prop = quality_properties(properties_as_dict=self.prop_dict)
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_04')
        in_file = test_data_dir.joinpath('in-04.tar')
        actual_out_file = 'filelist.json'
        err_str = 'error=Input is not in the .gz format'

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file, err_str)

    def test_05(self):
        """TS-3122 : TARGZContentExtractor: .gz file as input instead of tar.gz"""
        prop = quality_properties(properties_as_dict=self.prop_dict)
        prop.write_to_file(LOCAL_PROP_FILE)
        test_data_dir = self.data_dir.joinpath('test_05')
        in_file = test_data_dir.joinpath('in-05.gz')
        actual_out_file = 'filelist.json'
        err_str = 'error=No such file or directory'

        self.run_content_extractor_test(LOCAL_PROP_FILE, self.classname, in_file, actual_out_file, err_str)

    def test_06(self):
        """TS-3123 : TARGZContentExtractor: Non existent tar file"""
        prop = quality_properties(properties_as_dict=self.prop_dict)
        prop.write_to_file(LOCAL_PROP_FILE)
        in_file = 'non-existent-file-name.tar.gz'
        actual_out_file = 'filelist.json'
        err_str = 'error=%s (No such file or directory)' % in_file

        sto, ste = ShellExecutor.run_wait_standalone(CMD_PARSER_TMPL % {'prop': LOCAL_PROP_FILE,
                                                                        'class': self.classname,
                                                                        'in_file': in_file,
                                                                        'dest_dir': 'extractor_destination',
                                                                        'out_file': actual_out_file})

        if ste:
            logging.error('Content Extractor driver execution error: \n %s' % ste)
        stdoe = ste + sto
        if err_str:
            if err_str not in stdoe:
                raise TestFailure('Expected error: %s not found in logs' % err_str)
            else:
                logging.info('Expected error string found in standard out/err stream: %s' % err_str)
