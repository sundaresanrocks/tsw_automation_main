"""
=========================
Regex Pre Processor tests
=========================
"""


__author__ = 'abhijeet'


import logging
from unittest.case import SkipTest
import subprocess
from path import Path

import runtime
from libx.process import ShellExecutor
from lib.exceptions import TestFailure
from harvesters.harvester import Harvester
from harvesters.qaharvester import HarvesterQuality
from harvesters.properties import quality_properties
from framework.test import SandboxedTest


LOCAL_PROP_FILE = Path('source-adapter.properties')

CMD_PARSER_TMPL = runtime.SH.source_adapter_driver + ' %(prop)s %(in_file)s'


class GenericSourceAdapterDriver(SandboxedTest):
    """Source adapter tests using GenericSourceAdapterDriver"""
    default_har_config = HarvesterQuality
    content_provider_name = 'FileContentProvider'
    content_parser_name = 'CSVContentParser'

    def setUp(self):
        super(GenericSourceAdapterDriver, self).setUp()
        LOCAL_PROP_FILE.remove_p()
        self.har = Harvester(HarvesterQuality())
        self.har.remove_harvester_log()

        # Skip test
        if not runtime.SH.source_adapter_driver.isfile():
            raise SkipTest('Shell script does not exist: %s' % runtime.SH.source_adapter_driver)

    def run_source_adapter_test(self, prop_file, in_file_name, err_str=None):
        if not in_file_name.isfile():
            raise FileNotFoundError('File: %s not found' % in_file_name)
        out_file = Path('out-' + in_file_name.basename() + '.parsed')
        out_file.remove_p()

        timeout_secs = 8
        cmd = CMD_PARSER_TMPL % {'prop': prop_file, 'in_file': in_file_name}

        sto, ste = ShellExecutor.run_wait_standalone(cmd, timeout=300)
        if ste:
            logging.error('Source adapter driver execution error. %s', ste)
        stdoe = ste + sto
        if err_str:
            if err_str not in stdoe:
                raise TestFailure('%s was not found in log' % err_str)
            else:
                logging.info('Expected error string found in standard out/err stream: %s' % err_str)
            return True
        return stdoe


class Regex(GenericSourceAdapterDriver):
    """Pre processor tests for regex"""
    content_parser_name = 'CSVContentParser'
    pp_res_dir = runtime.data_path + '/tsw/harvesters/driver/pre_processors/regex/'

    def test_01(self):
        """TS-3110:RegexReplacePreProcessor: Positive use case with only one match replace pattern; one URL."""
        prop = quality_properties(content_parser=self.content_parser_name,
                                  content_provider=self.content_provider_name)
        prop['Preprocessor.count'] = '1'
        prop['Preprocessor.1.className'] = 'com.securecomputing.sftools.harvester.preprocessor.RegexReplacePreprocessor'
        prop['RegexReplacePreprocessor.match.1'] = 'hxxp://'
        prop['RegexReplacePreprocessor.replace.1'] = 'http://'
        prop.write_to_file(LOCAL_PROP_FILE)

        base_file = 'protocol-hxxp-to-http.csv'
        in_csv_file = self.pp_res_dir + base_file
        exp_json_file = in_csv_file + '.json'
        act_json_file = 'out-0-' + base_file + '.parsed'

        self.run_source_adapter_test(LOCAL_PROP_FILE, in_file_name=in_csv_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_02(self):
        """TS-3111:RegexReplacePreProcessor: Positive use case with multiple match replace patterns."""
        prop = quality_properties(content_parser=self.content_parser_name,
                                  content_provider=self.content_provider_name)
        prop['Preprocessor.count'] = '1'
        prop['Preprocessor.1.className'] = 'com.securecomputing.sftools.harvester.preprocessor.RegexReplacePreprocessor'
        prop['RegexReplacePreprocessor.match.1'] = 'hxxp://'
        prop['RegexReplacePreprocessor.replace.1'] = 'http://'
        prop['RegexReplacePreprocessor.match.2'] = '.org'
        prop['RegexReplacePreprocessor.replace.2'] = '.com'
        prop.write_to_file(LOCAL_PROP_FILE)

        base_file = 'protocol-hxxp-to-https.csv'
        in_csv_file = self.pp_res_dir + base_file
        exp_json_file = in_csv_file + '.json'
        act_json_file = 'out-0-' + base_file + '.parsed'

        self.run_source_adapter_test(LOCAL_PROP_FILE, in_file_name=in_csv_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_03(self):
        """TS-3112:RegexReplacePreProcessor: No regex replacers defined."""
        prop = quality_properties(content_parser=self.content_parser_name,
                                  content_provider=self.content_provider_name)
        prop['Preprocessor.count'] = '1'
        prop['Preprocessor.1.className'] = 'com.securecomputing.sftools.harvester.preprocessor.RegexReplacePreprocessor'
        prop.write_to_file(LOCAL_PROP_FILE)

        base_file = 'protocol-hxxp-to-http.csv'
        in_csv_file = self.pp_res_dir + base_file
        error_string = 'No regex replacers defined'

        self.run_source_adapter_test(LOCAL_PROP_FILE, in_file_name=in_csv_file, err_str=error_string)

    def test_04(self):
        """TS-3113:RegexReplacePreProcessor: Bad match pattern."""
        prop = quality_properties(content_parser=self.content_parser_name,
                                  content_provider=self.content_provider_name)
        prop['Preprocessor.count'] = '1'
        prop['Preprocessor.1.className'] = 'com.securecomputing.sftools.harvester.preprocessor.RegexReplacePreprocessor'
        prop['RegexReplacePreprocessor.match.1'] = '},{'
        prop['RegexReplacePreprocessor.replace.1'] = 'http://'
        prop.write_to_file(LOCAL_PROP_FILE)

        base_file = 'protocol-hxxp-to-http.csv'
        in_csv_file = self.pp_res_dir + base_file
        error_string = 'Bad match pattern:'

        self.run_source_adapter_test(LOCAL_PROP_FILE, in_file_name=in_csv_file, err_str=error_string)

    def test_05(self):
        """TS-3114:RegexReplacePreProcessor: Positive use case with only one match replace pattern; multiple URLs."""
        prop = quality_properties(content_parser=self.content_parser_name,
                                  content_provider=self.content_provider_name)
        prop['Preprocessor.count'] = '1'
        prop['Preprocessor.1.className'] = 'com.securecomputing.sftools.harvester.preprocessor.RegexReplacePreprocessor'
        prop['RegexReplacePreprocessor.match.1'] = 'hxxp://'
        prop['RegexReplacePreprocessor.replace.1'] = 'http://'
        prop.write_to_file(LOCAL_PROP_FILE)

        base_file = 'protocol-hxxp-to-http-multiple.csv'
        in_csv_file = self.pp_res_dir + base_file
        exp_json_file = in_csv_file + '.json'
        act_json_file = 'out-0-' + base_file + '.parsed'

        self.run_source_adapter_test(LOCAL_PROP_FILE, in_file_name=in_csv_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)


class RemoveCharacter(GenericSourceAdapterDriver):
    """Pre processor tests for remove character"""
    content_parser_name = 'CSVContentParser'
    pp_res_dir = runtime.data_path + '/tsw/harvesters/driver/pre_processors/removecharacter/'

    def test_01(self):
        """TS-3115 : RemoveCharacterPreProcessor: Positive use case with only one match replace pattern; one URL."""
        prop = quality_properties(content_parser=self.content_parser_name,
                                  content_provider=self.content_provider_name)
        prop['Preprocessor.count'] = '1'
        prop['Preprocessor.1.className'] = \
            'com.securecomputing.sftools.harvester.preprocessor.RemoveCharacterPreprocessor'
        prop['RemoveCharacterPreprocessor.count'] = '1'
        prop['RemoveCharacterPreprocessor.char.1'] = 'x'
        prop.write_to_file(LOCAL_PROP_FILE)

        base_file = 'test-01.csv'
        in_csv_file = self.pp_res_dir + base_file
        exp_json_file = in_csv_file + '.json'
        act_json_file = 'out-0-' + base_file + '.parsed'

        self.run_source_adapter_test(LOCAL_PROP_FILE, in_file_name=in_csv_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_02(self):
        """TS-3116 : RemoveCharacterPreProcessor: Missing character count"""
        prop = quality_properties(content_parser=self.content_parser_name,
                                  content_provider=self.content_provider_name)
        prop['Preprocessor.count'] = '1'
        prop['Preprocessor.1.className'] = \
            'com.securecomputing.sftools.harvester.preprocessor.RemoveCharacterPreprocessor'
        prop.write_to_file(LOCAL_PROP_FILE)
        error_string = 'Missing required property: RemoveCharacterPreprocessor.count'

        base_file = 'remove-backslash.csv'
        in_csv_file = self.pp_res_dir + base_file
        self.run_source_adapter_test(LOCAL_PROP_FILE, in_file_name=in_csv_file, err_str=error_string)

    def test_03(self):
        """TS-3117 : RemoveCharacterPreProcessor: Missing char properties"""
        prop = quality_properties(content_parser=self.content_parser_name,
                                  content_provider=self.content_provider_name)
        prop['Preprocessor.count'] = '1'
        prop['Preprocessor.1.className'] = \
            'com.securecomputing.sftools.harvester.preprocessor.RemoveCharacterPreprocessor'
        prop['RemoveCharacterPreprocessor.count'] = '2'
        prop['RemoveCharacterPreprocessor.char.1'] = 'x'
        prop.write_to_file(LOCAL_PROP_FILE)
        error_string = 'Missing expected property. RemoveCharacterPreprocessor.char.2'

        base_file = 'remove-backslash.csv'
        in_csv_file = self.pp_res_dir + base_file
        self.run_source_adapter_test(LOCAL_PROP_FILE, in_file_name=in_csv_file, err_str=error_string)

    def test_04(self):
        """TS-3118 : RemoveCharacterPreProcessor: Multiple characters to remove; single URL."""
        prop = quality_properties(content_parser=self.content_parser_name,
                                  content_provider=self.content_provider_name)
        prop['Preprocessor.count'] = '1'
        prop['Preprocessor.1.className'] = \
            'com.securecomputing.sftools.harvester.preprocessor.RemoveCharacterPreprocessor'
        prop['RemoveCharacterPreprocessor.count'] = '2'
        prop['RemoveCharacterPreprocessor.char.1'] = 'x'
        prop['RemoveCharacterPreprocessor.char.2'] = 'z'
        prop.write_to_file(LOCAL_PROP_FILE)

        base_file = 'test-04.csv'
        in_csv_file = self.pp_res_dir + base_file
        exp_json_file = in_csv_file + '.json'
        act_json_file = 'out-0-' + base_file + '.parsed'

        self.run_source_adapter_test(LOCAL_PROP_FILE, in_file_name=in_csv_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_05(self):
        """TS-3119 : RemoveCharacterPreProcessor: Multiple characters to remove; multipple URLs."""
        prop = quality_properties(content_parser=self.content_parser_name,
                                  content_provider=self.content_provider_name)
        prop['Preprocessor.count'] = '1'
        prop['Preprocessor.1.className'] = \
            'com.securecomputing.sftools.harvester.preprocessor.RemoveCharacterPreprocessor'
        prop['RemoveCharacterPreprocessor.count'] = '2'
        prop['RemoveCharacterPreprocessor.char.1'] = 'x'
        prop['RemoveCharacterPreprocessor.char.2'] = 'z'
        prop.write_to_file(LOCAL_PROP_FILE)

        base_file = 'test-05.csv'
        in_csv_file = self.pp_res_dir + base_file
        exp_json_file = in_csv_file + '.json'
        act_json_file = 'out-0-' + base_file + '.parsed'

        self.run_source_adapter_test(LOCAL_PROP_FILE, in_file_name=in_csv_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)
