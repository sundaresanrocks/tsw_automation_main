"""
====================
Content parser tests
====================

"""
import shutil
from unittest.case import SkipTest
import uuid
from path import Path
from framework.test import SandboxedTest

# import os
import logging
import json

import runtime
from conf.files import LOG, SH
from libx.process import ShellExecutor
from lib.exceptions import TestFailure
from harvesters.harvester import Harvester
from harvesters.properties import quality_properties
from harvesters.qaharvester import HarvesterQuality


DEFAULT_PARSER_CLASSES = {
    'BotnetCC': 'com.securecomputing.sftools.harvester.contentParsers.BotnetCCContentParser',
    'CrawlResult': 'com.securecomputing.sftools.harvester.contentParsers.CrawlResultContentParser',
    'CSV': 'com.securecomputing.sftools.harvester.contentParsers.CSVContentParser',
    'CysconSIRT': 'com.securecomputing.sftools.harvester.contentParsers.CysconSIRTContentParser',
    'HTMLTable': 'com.securecomputing.sftools.harvester.contentParsers.HTMLTableContentParser',
    'JSON': 'com.securecomputing.sftools.harvester.contentParsers.JSONContentParser',
    'JSONPath': 'com.securecomputing.sftools.harvester.contentParsers.JSONPathContentParser',
    'MalwareDomainList': 'com.securecomputing.sftools.harvester.contentParsers.MalwareDomainListContentParser',
    'NVPair': 'com.securecomputing.sftools.harvester.contentParsers.NVPairContentParser',
    'Regex': 'com.securecomputing.sftools.harvester.contentParsers.RegexContentParser',
    'RSS': 'com.securecomputing.sftools.harvester.contentParsers.RSSContentParser',
    'SAX': 'com.securecomputing.sftools.harvester.contentParsers.SAXContentParser',
    'XML': 'com.securecomputing.sftools.harvester.contentParsers.XMLContentParser',
}

LOCAL_PROP_FILE = Path('content_parser.properties')

CMD_PARSER_TMPL = SH.content_parser_driver + ' %(prop)s %(class)s %(in_file)s %(out_file)s'


class ContentParerTest(SandboxedTest):
    """Content parser tests using driver"""
    default_har_config = HarvesterQuality
    content_provider_name = 'File'
    sandbox_json_file = 'content-parser-output.json'

    def setUp(self):
        super(ContentParerTest, self).setUp()
        LOCAL_PROP_FILE.remove_p()
        LOG.harvester.remove_p()

        self.har = Harvester(HarvesterQuality())

        if not SH.content_parser_driver.isfile():
            # logging.error(os.path.isfile(SH.content_parser_driver))
            # Skip tests
            raise SkipTest('Shell script does not exist: %s' % SH.content_parser_driver)

    def run_content_parser_test(self, prop_file, class_name, in_file_name, out_file_name='content-parser-output.json',
                                err_str=None):
        if not Path(in_file_name).isfile():
            raise FileNotFoundError('File: %s not found' % in_file_name)
        if Path(out_file_name).isfile():
            backup_old_file_name = out_file_name + str(uuid.uuid4())
            logging.info('output file:%s exists. Will be renamed to: %s' % (out_file_name, backup_old_file_name))
            shutil.move(out_file_name, backup_old_file_name)

        sto, ste = ShellExecutor.run_wait_standalone(CMD_PARSER_TMPL % {'prop': prop_file,
                                                                        'class': class_name,
                                                                        'in_file': in_file_name,
                                                                        'out_file': out_file_name})
        if ste:
            logging.error('Content Parser driver execution error. %s', ste)
        stdoe = ste + sto
        if err_str:
            if err_str not in stdoe:
                raise TestFailure('%s was not found in log' % err_str)
            else:
                logging.info('Expected error string found in standard out/err stream: %s' % err_str)
            return True
        return stdoe


class CSVContentParser(ContentParerTest):
    """CSV Content parser tests"""

    content_parser_name = 'CSVContentParser'
    cp_res_dir = runtime.data_path + '/tsw/harvesters/driver/content_parsers/CSV/'

    def test_01(self):
        """Missing csv file"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = 'non-existing-name.txt'
        err_str = 'Could not read missing CSV filename=%s' % local_data_file

        sto, ste = ShellExecutor.run_wait_standalone(CMD_PARSER_TMPL % {'prop': LOCAL_PROP_FILE,
                                                                        'class': DEFAULT_PARSER_CLASSES['CSV'],
                                                                        'in_file': local_data_file,
                                                                        'out_file': 'out-file'})
        if err_str not in ste + sto:
            raise TestFailure('%s was not found in log' % err_str)
        else:
            logging.info('Expected error string found in standard out/err stream: %s' % err_str)
        return True

    def test_02(self):
        """Missing property, CSVContentParser.maxNumberOfColumns"""
        prop = quality_properties(content_parser=self.content_parser_name)
        del prop['CSVContentParser.maxNumberOfColumns']
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = 'missing-prop.csv'
        with open(local_data_file, 'w') as fpb:
            fpb.write('url')
        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['CSV'],
                                     local_data_file,
                                     err_str="Missing required 'CSVContentParser.maxNumberOfColumns' property")

    def test_03(self):
        """Missing required column 'url'"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['CSVContentParser.column.1'] = 'unknown'
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = 'missing-column.csv'
        with open(local_data_file, 'w') as fpb:
            fpb.write('missing url column')
        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['CSV'],
                                     local_data_file,
                                     err_str="Missing required column 'url'")

    def test_04(self):
        """Skip Row - default - no rows skipped"""
        quality_properties(content_parser=self.content_parser_name,
                           write_to_file=LOCAL_PROP_FILE)
        exp_data = json.load(open(self.cp_res_dir + 'skip-tests-0-rows.json'))

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['CSV'],
                                     in_file_name=self.cp_res_dir + 'skip-tests-10-rows.csv',
                                     out_file_name='parsed-output.json')
        actual_data = json.load(open('parsed-output.json'))
        self.assert_json_equal(exp_data, actual_data)

    def test_05(self):
        """Skip Row - default - 2 rows skipped"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['CSVContentParser.skipRowCount'] = '2'
        prop.write_to_file(LOCAL_PROP_FILE)
        in_csv_file = self.cp_res_dir + 'skip-tests-10-rows.csv'
        exp_json_file = self.cp_res_dir + 'skip-tests-2-rows.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['CSV'],
                                     in_file_name=in_csv_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_06(self):
        """Missing data row"""
        quality_properties(content_parser=self.content_parser_name,
                           write_to_file=LOCAL_PROP_FILE)
        in_csv_file = self.cp_res_dir + 'missing-row.csv'
        exp_json_file = self.cp_res_dir + 'missing-row.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['CSV'],
                                     in_file_name=in_csv_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_07(self):
        """Quoted CSV File - default double quotes"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['CSVContentParser.maxNumberOfColumns'] = '2'
        prop['CSVContentParser.column.2'] = 'id'
        prop.write_to_file(LOCAL_PROP_FILE)

        in_csv_file = self.cp_res_dir + 'default-double-quotes.csv'
        exp_json_file = self.cp_res_dir + '2-rows,2-cols.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['CSV'],
                                     in_file_name=in_csv_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_08(self):
        """Quoted CSV File - pipe quotes"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['CSVContentParser.maxNumberOfColumns'] = '2'
        prop['CSVContentParser.quoteChar'] = '|'
        prop['CSVContentParser.column.2'] = 'id'
        prop.write_to_file(LOCAL_PROP_FILE)

        in_csv_file = self.cp_res_dir + 'pipe-quotes.csv'
        exp_json_file = self.cp_res_dir + '2-rows,2-cols.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['CSV'],
                                     in_file_name=in_csv_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_09(self):
        """Field separator - pipe"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['CSVContentParser.maxNumberOfColumns'] = '2'
        prop['CSVContentParser.fieldSeparator'] = '|'
        prop['CSVContentParser.column.2'] = 'id'
        prop.write_to_file(LOCAL_PROP_FILE)

        in_csv_file = self.cp_res_dir + 'pipe-field-separator.csv'
        exp_json_file = self.cp_res_dir + '2-rows,2-cols.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['CSV'],
                                     in_file_name=in_csv_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_10(self):
        """Column count is less than the max number of cols for all rows"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['CSVContentParser.maxNumberOfColumns'] = '2'
        prop['CSVContentParser.column.2'] = 'id'
        prop.write_to_file(LOCAL_PROP_FILE)

        in_csv_file = self.cp_res_dir + '2-rows,1-cols.csv'
        exp_json_file = self.cp_res_dir + 'empty.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['CSV'],
                                     in_file_name=in_csv_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_11(self):
        """Column count is less than the max number of cols for few rows"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['CSVContentParser.maxNumberOfColumns'] = '3'
        prop['CSVContentParser.column.2'] = 'id'
        prop['CSVContentParser.column.3'] = 'words'
        prop.write_to_file(LOCAL_PROP_FILE)

        in_csv_file = self.cp_res_dir + '3-rows,3-cols,2nd_row_has_2_cols.csv'
        exp_json_file = self.cp_res_dir + '3-rows,3-cols,2nd_row_has_2_cols.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['CSV'],
                                     in_file_name=in_csv_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_12(self):
        """Column count is more than the max number of cols for few rows"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['CSVContentParser.maxNumberOfColumns'] = '2'
        prop['CSVContentParser.column.2'] = 'id'
        prop['CSVContentParser.column.3'] = 'words'
        prop.write_to_file(LOCAL_PROP_FILE)

        in_csv_file = self.cp_res_dir + '3-rows,3-cols,2nd_row_has_2_cols.csv'
        exp_json_file = self.cp_res_dir + 'u2-two.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['CSV'],
                                     in_file_name=in_csv_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_13(self):
        """Column def count is less than the max number of cols"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['CSVContentParser.maxNumberOfColumns'] = '3'
        prop['CSVContentParser.column.2'] = 'id'
        prop.write_to_file(LOCAL_PROP_FILE)

        in_csv_file = self.cp_res_dir + '2-rows,3-cols.csv'
        exp_json_file = self.cp_res_dir + '2-rows,2-cols.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['CSV'],
                                     in_file_name=in_csv_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_14(self):
        """Column def count is less than the max number of cols - missing col def"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['CSVContentParser.maxNumberOfColumns'] = '3'
        prop['CSVContentParser.column.3'] = 'id'
        prop.write_to_file(LOCAL_PROP_FILE)

        in_csv_file = self.cp_res_dir + '2-rows,3-cols.csv'
        exp_json_file = self.cp_res_dir + '2-rows-word.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['CSV'],
                                     in_file_name=in_csv_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_15(self):
        """Missing url"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['CSVContentParser.maxNumberOfColumns'] = '1'
        prop.write_to_file(LOCAL_PROP_FILE)

        in_csv_file = self.cp_res_dir + '3-rows,1-cols,2-invalid.csv'
        exp_json_file = self.cp_res_dir + 'missing-url.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['CSV'],
                                     in_file_name=in_csv_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)


class JSONContentParser(ContentParerTest):
    """JSON Content parser tests"""

    content_parser_name = 'JSONContentParser'
    cp_res_dir = runtime.data_path + '/tsw/harvesters/driver/content_parsers/JSON/'

    def test_01(self):
        """Missing json file"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = 'non-existing-name.json'
        err_str = 'IOException while parsing JSON. Error Message: ' + local_data_file

        sto, ste = ShellExecutor.run_wait_standalone(CMD_PARSER_TMPL % {'prop': LOCAL_PROP_FILE,
                                                                        'class': DEFAULT_PARSER_CLASSES['JSON'],
                                                                        'in_file': local_data_file,
                                                                        'out_file': 'out-file'})
        if err_str not in ste + sto:
            raise TestFailure('%s was not found in log' % err_str)
        else:
            logging.info('Expected error string found in standard out/err stream: %s' % err_str)

    def test_02(self):
        """Missing required 'JSONContentParser.prefix' property."""
        prop = quality_properties(content_parser=self.content_parser_name)
        del prop['Quality.JSONContentParser.prefix']
        logging.info('Remove property JSONContentParser.prefix')
        prop.write_to_file(LOCAL_PROP_FILE)

        in_json_file = self.cp_res_dir + 'seo-trends-1.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['JSON'],
                                     in_json_file,
                                     err_str="Missing required 'JSONContentParser.prefix' property.")

    def test_03(self):
        """SEO Trends harvester test data"""
        prop = quality_properties(content_parser=self.content_parser_name)

        prop.write_to_file(LOCAL_PROP_FILE)

        in_json_file = self.cp_res_dir + 'seo-trends-1.json'
        exp_json_file = self.cp_res_dir + 'seo-trends-1_exp.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['JSON'],
                                     in_file_name=in_json_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)
        logging.info('SEO Trends json File with one entry was parsed successfully.')

    def test_04(self):
        """SEO Trends harvester test data - multiple entries"""
        prop = quality_properties(content_parser=self.content_parser_name)

        prop.write_to_file(LOCAL_PROP_FILE)

        in_json_file = self.cp_res_dir + 'seo-trends-10.json'
        exp_json_file = self.cp_res_dir + 'seo-trends-10_exp.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['JSON'],
                                     in_file_name=in_json_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)
        logging.info('SEO Trends json File with multiple entries was parsed successfully.')

    def test_05(self):
        """Missing required field mapping 'url'"""
        prop = quality_properties(content_parser=self.content_parser_name)
        del prop['JSONContentParser.keyname.url']
        logging.info('Remove property JSONContentParser.keyname.url')
        prop.write_to_file(LOCAL_PROP_FILE)

        in_json_file = self.cp_res_dir + 'seo-trends-1.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['JSON'],
                                     in_json_file,
                                     err_str="Missing required field mapping 'url'")

    def test_06(self):
        """Unable to parse the json file"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)

        in_json_file = self.cp_res_dir + 'unable-to-parse.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['JSON'],
                                     in_json_file,
                                     err_str="HarvesterGeneralException: Unable to parse JSON. Error Message")

    def test_07(self):
        """Unable to map the json file"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)

        in_json_file = self.cp_res_dir + 'io-exception-while-parsing.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['JSON'],
                                     in_json_file,
                                     err_str="IOException while parsing JSON")

    def test_08(self):
        """empty file"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)

        in_json_file = self.cp_res_dir + 'empty.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['JSON'],
                                     in_json_file,
                                     err_str="IOException while parsing JSON. Error Message:"
                                             " No content to map to Object due to end of input")

    def test_09(self):
        """Missing required field 'key'"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)

        in_json_file = self.cp_res_dir + 'missing-req-field.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['JSON'],
                                     in_json_file,
                                     err_str="Missing required field 'key'")

    def test_10(self):
        """root node value = null"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['JSONContentParser.root'] = ''
        prop.write_to_file(LOCAL_PROP_FILE)

        in_json_file = self.cp_res_dir + 'seo-trends-1.json'
        exp_json_file = self.cp_res_dir + 'empty_exp.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['JSON'],
                                     in_file_name=in_json_file,
                                     out_file_name=act_json_file
                                     )
        self.assert_json_file_equal(exp_json_file, act_json_file)
        logging.info('JSONContentParser.root=null results in {} expected data')

    def test_11(self):
        """null value for a key"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['JSONContentParser.root'] = ''
        prop.write_to_file(LOCAL_PROP_FILE)

        in_json_file = self.cp_res_dir + 'null-value-key.json'
        exp_json_file = self.cp_res_dir + 'empty_exp.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['JSON'],
                                     in_file_name=in_json_file,
                                     out_file_name=act_json_file
                                     )
        self.assert_json_file_equal(exp_json_file, act_json_file)
        logging.info('JSONContentParser.root=null results in {} expected data')


class RSSContentParser(ContentParerTest):
    """RSS Content parser tests"""
    content_parser_name = 'RSSContentParser'
    data_dir = runtime.data_path.joinpath('tsw/harvesters/driver/content_parsers/RSS')

    def test_01(self):
        """TS-3134:RSSContentParser: Missing working file"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = 'non-existing-name'
        err_str = 'Unable to process the specified file. fileName=%s' % local_data_file

        sto, ste = ShellExecutor.run_wait_standalone(CMD_PARSER_TMPL % {'prop': LOCAL_PROP_FILE,
                                                                        'class': DEFAULT_PARSER_CLASSES['RSS'],
                                                                        'in_file': local_data_file,
                                                                        'out_file': 'out-file'})
        if err_str not in ste + sto:
            raise TestFailure('%s was not found in log' % err_str)
        else:
            logging.info('Expected error string found in standard out/err stream: %s' % err_str)

    def test_03(self):
        """TS-3135:RSSContentParser: RSS FeedException. RSS is invalid."""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = self.data_dir.joinpath('Hashes-03.txt')
        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['RSS'],
                                     local_data_file,
                                     err_str='Unable to process the RSS Feed. fileName=%s' % local_data_file)

    def test_05(self):
        """TS-3136:RSSContentParser: Positive test case."""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = self.data_dir.joinpath('Hashes-05.txt')
        act_json_file = 'content-parser-output.json'
        exp_json_file = self.data_dir + '/out-05.json'
        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['RSS'],
                                     in_file_name=local_data_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_06(self):
        """TS-3137:RSSContentParser: Number of fields value less than actual attributes"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['RSSContentParser.numberOfFields'] = '2'
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = self.data_dir.joinpath('Hashes-06.txt')
        act_json_file = 'content-parser-output.json'
        exp_json_file = self.data_dir + '/out-06.json'
        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['RSS'],
                                     in_file_name=local_data_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_07(self):
        """TS-3138:RSSContentParser: Field value is null."""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['RSSContentParser.field.3'] = ""
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = self.data_dir.joinpath('Hashes-07.txt')
        act_json_file = 'content-parser-output.json'
        exp_json_file = self.data_dir + '/out-07.json'
        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['RSS'],
                                     in_file_name=local_data_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_08(self):
        """TS-3139:RSSContentParser: Missing URL field."""
        prop = quality_properties(content_parser=self.content_parser_name)
        del prop['RSSContentParser.field.1']
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = self.data_dir.joinpath('Hashes-08.txt')
        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['RSS'],
                                     local_data_file, err_str='Missing required \'url\' field.')

    def test_09(self):
        """TS-3140:RSSContentParser: Incorrect regex."""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['RSSContentParser.regex'] = '^U: (.*?), IP Address: (.*?), Country: (.*?), ASN: (.*?), MD5: (.*?)$'
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = self.data_dir.joinpath('Hashes-09.txt')
        act_json_file = 'content-parser-output.json'
        exp_json_file = self.data_dir + '/out-09.json'
        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['RSS'],
                                     in_file_name=local_data_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_10(self):
        """TS-3141:RSSContentParser: Invalid regex."""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['RSSContentParser.regex'] = '^URL**: (.*?), IP Address: (.*?), Country: (.*?), ASN: (.*?), MD5: (.*?)$'
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = self.data_dir.joinpath('Hashes-10.txt')
        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['RSS'],
                                     local_data_file, err_str='java.util.regex.PatternSyntaxException')

    def test_11(self):
        """TS-3142:RSSContentParser: Invalid number of fields."""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['RSSContentParser.numberOfFields'] = 'five'
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = self.data_dir.joinpath('Hashes-11.txt')
        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['RSS'],
                                     in_file_name=local_data_file,
                                     err_str='java.lang.NumberFormatException')

    def test_12(self):
        """TS-3143:RSSContentParser:Number of fields value more than actual attributes."""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['RSSContentParser.numberOfFields'] = '10'
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = self.data_dir.joinpath('Hashes-12.txt')
        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['RSS'],
                                     in_file_name=local_data_file)
        act_json_file = 'content-parser-output.json'
        exp_json_file = self.data_dir + '/out-12.json'
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_13(self):
        """TS-3144:RSSContentParser: No items in RSS."""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['RSSContentParser.numberOfFields'] = '10'
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = self.data_dir.joinpath('Hashes-13.txt')
        act_json_file = 'content-parser-output.json'
        exp_json_file = self.data_dir + '/out-13.json'
        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['RSS'],
                                     in_file_name=local_data_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)


class XMLContentParser(ContentParerTest):
    """XML Content parser tests"""

    content_parser_name = 'XMLContentParser'
    cp_res_dir = runtime.data_path + '/tsw/harvesters/driver/content_parsers/XML/'

    def test_01(self):
        """Missing xml file"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)
        local_data_file = 'non-existing-name.xml'
        err_str = 'com.securecomputing.sftools.harvester.exception.HarvesterGeneralException: IO error'

        sto, ste = ShellExecutor.run_wait_standalone(CMD_PARSER_TMPL % {'prop': LOCAL_PROP_FILE,
                                                                        'class': DEFAULT_PARSER_CLASSES['XML'],
                                                                        'in_file': local_data_file,
                                                                        'out_file': 'out-file'})
        if err_str not in ste + sto:
            raise TestFailure('%s was not found in log' % err_str)
        else:
            logging.info('Expected error string found in standard out/err stream: %s' % err_str)

    def test_02(self):
        """Missing property, XMLContentParser.minLines - defaults to 3 - negative test"""
        prop = quality_properties(content_parser=self.content_parser_name)
        del prop['XMLContentParser.minLines']
        logging.info('Removing property XMLContentParser.minLines')
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + '1-line-valid.xml'
        exp_json_file = self.cp_res_dir + 'empty.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_file_name=in_xml_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)
        logging.info('Min lines default to 3. Less than 3 lines are not loaded.')

    def test_03(self):
        """Missing property, XMLContentParser.minLines - defaults to 3 - positive test"""
        prop = quality_properties(content_parser=self.content_parser_name)
        del prop['XMLContentParser.minLines']
        logging.info('Removing property XMLContentParser.minLines')
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + '3-lines.xml'
        exp_json_file = self.cp_res_dir + '1-entry.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_file_name=in_xml_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)
        logging.info('Min lines default to 3. XML File with 3 lines was loaded successfully')

    def test_04(self):
        """Parse property, XMLContentParser.minLines - defaults to 3"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['XMLContentParser.minLines'] = 'invalid'
        logging.info('Set XMLContentParser.minLines=invalid')
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + '3-lines.xml'
        exp_json_file = self.cp_res_dir + '1-entry.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_file_name=in_xml_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)
        logging.info('Min lines default to 3. XML File with 3 lines was loaded successfully')

    def test_05(self):
        """Missing required 'XMLContentParser.prefix' property."""
        prop = quality_properties(content_parser=self.content_parser_name)
        del prop['XMLContentParser.prefix']
        logging.info('Remove property XMLContentParser.prefix')
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + '3-lines.xml'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_xml_file,
                                     err_str="Missing required 'XMLContentParser.prefix' property.")

    def test_06(self):
        """Missing required 'XMLContentParser.required' property"""
        prop = quality_properties(content_parser=self.content_parser_name)
        del prop['XMLContentParser.required']
        logging.info('Remove property XMLContentParser.required')
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + '3-lines.xml'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_xml_file,
                                     err_str="Missing required 'XMLContentParser.required' property.")

    def test_07(self):
        """Empty 'XMLContentParser.required' property"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['XMLContentParser.required'] = ""
        logging.info('Set the property XMLContentParser.required=""')
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + '3-lines.xml'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_xml_file,
                                     err_str="Missing required field mapping ''")

    def test_08(self):
        """Missing required field mapping 'url'"""
        prop = quality_properties(content_parser=self.content_parser_name)
        del prop['Prefix.url']
        logging.info('Remove filed/property Prefix.url')
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + '3-lines.xml'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_xml_file,
                                     err_str="Missing required field mapping 'url'")

    def test_09(self):
        """Missing required 'XMLContentParser.root' property"""
        prop = quality_properties(content_parser=self.content_parser_name)
        del prop['XMLContentParser.root']
        logging.info('Remove property XMLContentParser.root')
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + '3-lines.xml'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_xml_file,
                                     err_str="java.lang.NullPointerException")

    def test_10(self):
        """Missing required 'XMLContentParser.key' property"""
        prop = quality_properties(content_parser=self.content_parser_name)
        del prop['XMLContentParser.key']
        logging.info('Remove property XMLContentParser.key')
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + '3-lines.xml'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_xml_file,
                                     err_str="java.lang.NullPointerException")

    def test_11(self):
        """"Missing value of required field 'count'"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + '1-line-null-count.xml'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_xml_file,
                                     err_str="Missing value of required field 'count'")

    def test_12(self):
        """"Missing value of required field 'url'"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + '1-line-null-url.xml'
        exp_json_file = self.cp_res_dir + 'empty.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_xml_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_13(self):
        """"Missing required field 'count'"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + '1-line-no-count.xml'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_xml_file,
                                     err_str="Missing required field 'count'")

    def test_14(self):
        """"Missing required field 'url'"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + '1-line-no-url.xml'
        exp_json_file = self.cp_res_dir + 'empty.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_xml_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)

    def test_15(self):
        """"Malformed xml file - sax exception"""

        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + '1-line-malformed.xml'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_xml_file,
                                     err_str="HarvesterGeneralException: Sax exception error")

    def test_16(self):
        """"Empty XML file"""

        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + 'empty.xml'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_xml_file,
                                     err_str="HarvesterGeneralException: Sax exception error")

    def test_17(self):
        """"No root element"""

        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + 'no-root-data.xml'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_xml_file,
                                     err_str="markup in the document following the root element must be well-formed")

    def test_18(self):
        """Positive test - multiple entries"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + 'multiple-entries.xml'
        exp_json_file = self.cp_res_dir + 'multiple-entries.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_file_name=in_xml_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)
        logging.info('XML File with multiple entries was parsed successfully.')

    def test_19(self):
        """Clean mx test"""
        prop = quality_properties(content_parser=self.content_parser_name)

        prop['Quality.XMLContentParser.prefix'] = 'Quality.XMLContentParser.xmltag'
        prop['Quality.XMLContentParser.required'] = 'url,response'
        prop['Quality.XMLContentParser.root'] = 'entry'
        prop['Quality.XMLContentParser.key'] = 'url'

        prop['Quality.XMLContentParser.xmltag.line'] = 'line'
        prop['Quality.XMLContentParser.xmltag.id'] = 'id'
        prop['Quality.XMLContentParser.xmltag.first'] = 'first'
        prop['Quality.XMLContentParser.xmltag.last'] = 'last'
        prop['Quality.XMLContentParser.xmltag.phishtank'] = 'phishtank'
        prop['Quality.XMLContentParser.xmltag.url'] = 'url'
        prop['Quality.XMLContentParser.xmltag.recent'] = 'recent'
        prop['Quality.XMLContentParser.xmltag.response'] = 'response'
        prop['Quality.XMLContentParser.xmltag.ip'] = 'ip'
        prop['Quality.XMLContentParser.xmltag.review'] = 'review'
        prop['Quality.XMLContentParser.xmltag.domain'] = 'domain'
        prop['Quality.XMLContentParser.xmltag.country'] = 'country'
        prop['Quality.XMLContentParser.xmltag.source'] = 'source'
        prop['Quality.XMLContentParser.xmltag.email'] = 'email'
        prop['Quality.XMLContentParser.xmltag.inetnum'] = 'inetnum'
        prop['Quality.XMLContentParser.xmltag.netname'] = 'netname'
        prop['Quality.XMLContentParser.xmltag.descr'] = 'descr'
        prop['Quality.XMLContentParser.xmltag.ns1'] = 'ns1'
        prop['Quality.XMLContentParser.xmltag.ns2'] = 'ns2'
        prop['Quality.XMLContentParser.xmltag.ns3'] = 'ns3'
        prop['Quality.XMLContentParser.xmltag.ns4'] = 'ns4'
        prop['Quality.XMLContentParser.xmltag.ns5'] = 'ns5'
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + 'cleanmx-phishing.xml'
        exp_json_file = self.cp_res_dir + 'cleanmx-phishing.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_file_name=in_xml_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)
        logging.info('Clean MX Phishing XML File with multiple entries was parsed successfully.')

    def test_20(self):
        """Face book black list tests"""
        prop = quality_properties(content_parser=self.content_parser_name)
        prop['Quality.XMLContentParser.prefix'] = 'Quality.XMLContentParser.xmltag'
        prop['Quality.XMLContentParser.required'] = 'content,status'
        prop['Quality.XMLContentParser.root'] = 'externalblacklistread_response_elt'
        prop['Quality.XMLContentParser.key'] = 'content'

        prop['Quality.XMLContentParser.xmltag.content'] = 'url'
        prop['Quality.XMLContentParser.xmltag.status'] = 'status'
        prop['Quality.XMLContentParser.xmltag.type'] = 'type'
        prop['Quality.XMLContentParser.xmltag.time'] = 'date_added'
        prop.write_to_file(LOCAL_PROP_FILE)

        in_xml_file = self.cp_res_dir + 'facebook-blacklist.xml'
        exp_json_file = self.cp_res_dir + 'facebook-blacklist.json'
        act_json_file = 'parsed-output.json'

        self.run_content_parser_test(LOCAL_PROP_FILE,
                                     DEFAULT_PARSER_CLASSES['XML'],
                                     in_file_name=in_xml_file,
                                     out_file_name=act_json_file)
        self.assert_json_file_equal(exp_json_file, act_json_file)
        logging.info('Facebook blacklist XML File with multiple entries was parsed successfully.')
