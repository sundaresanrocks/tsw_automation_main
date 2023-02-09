"""
Content Provider tests
======================

export CLASSPATH_PREFIX=$DIR_SRC/java_tsw/src/main/java:$CLASSPATH_PREFIX
cp /opt/sftools/bin/ContentProviderDriver.sh /opt/sftools/bin/qa-ContentProviderDriver.sh
perl -e "s|com.securecomputing.sftools.harvester.devutils.ContentProviderDriver|ContentProviderDriver|g;" -pi.save /opt/sftools/bin/qa-ContentProviderDriver.sh


"""

# import os
import re
import logging
import json

import runtime

from libx.process import ShellExecutor
from lib.exceptions import TestFailure
from harvesters.harvester import Harvester
from harvesters.qaharvester import HarvesterQuality
from harvesters.properties import quality_properties
from framework.test import SandboxedTest
from lib.db.mongowrap import get_qa_mongo_wrap
from path import Path
from runtime import Mongo

DEFAULT_CLASS = {'HTTP': 'com.securecomputing.sftools.harvester.contentProviders.HTTPContentProvider',
                 'FTP': 'com.securecomputing.sftools.harvester.contentProviders.FTPContentProvider',
                 'File': 'com.securecomputing.sftools.harvester.contentProviders.FileContentProvider',
                 'GenericMongoDB': 'com.securecomputing.sftools.harvester.contentProviders.GenericMongoDBContentProvider'}

CMD_CP_TMPL = runtime.SH.content_provider_driver + ' %(prop)s %(class)s'

LOCAL_PROP_FILE = Path('content-provider.properties')

DEFAULT_FTP_KEYS = {'FTPContentProvider.username': 'user',
                    'FTPContentProvider.password': 'pass',
                    'FTPContentProvider.host': 'localhost',
                    'FTPContentProvider.port': '2121',
                    'FTPContentProvider.directory': '.',
                    'FTPContentProvider.fileRegex': 'sample.txt'}

DEFAULT_HTTP_KEYS = {'HTTPContentProvider.binaryMode': 'false',
                     'HTTPContentProvider.source_url': 'http://localhost:8001/',
                     'HTTPContentProvider.userName': 'user',
                     'HTTPContentProvider.password': 'pass'}

DEFAULT_APWG_KEYS = {'HTTPContentProvider.binaryMode': 'true',
                     'HTTPContentProvider.source_url': 'https://www.ecrimex.net/assets/externalDownload',
                     'HTTPContentProvider.customFormName.1': 'email',
                     'HTTPContentProvider.customFormValue.1': 'john_wagener@mcafee.com',
                     'HTTPContentProvider.customFormName.2': 'password',
                     'HTTPContentProvider.customFormValue.2': 'Mcafee01',
                     'HTTPContentProvider.customFormName.3': 'extAssetId',
                     'HTTPContentProvider.customFormValue.3': 'dd0a475f75ebd6122d26ef0efa0d9bf8c0289535.CSV.tgz'}

DEFAULT_MONGODB_KEYS = {'MongoDBContentProvider.host': '%s' % Mongo.host,
                        'MongoDBContentProvider.port': '%s' % Mongo.port,
                        'MongoDBContentProvider.database': 'QAContentProvider',
                        'MongoDBContentProvider.collection': 'scorer_results',
                        'mongoQuery': '{"facts.factName":"SampleDBChildResultFact", "completeDate" : { "$gt" : ' + \
                                      '{ "$date" : "<<<max_complete_date>>>"} } }',
                        'mongoProjection': '{ "urlString":1, "facts":1, "completeDate":1}',
                        'mongoSortKey': '{completeDate:1}',
                        'max_complete_date': '2013-04-16T01:47:03Z'
                        }

DEFAULT_File_KEYS = {'FileContentProvider.sourceDir': Path(runtime.data_path + '/tsw/harvesters/driver/content_providers/server_root'),
                     'FileContentProvider.fileRegex': '.*'}

# DEFAULT_HTTP_KEYS = {}

C_PROVIDER_KEYS_MAP = {'FTP': DEFAULT_FTP_KEYS,
                       'HTTP': DEFAULT_HTTP_KEYS,
                       'File': DEFAULT_File_KEYS,
                       'GenericMongoDB': DEFAULT_MONGODB_KEYS}


def generic_mongodb_remove_id_from_json(actual_file):
    actual_json = json.load(open(actual_file))
    for record in actual_json:
        del record['_id']
    with open(actual_file, 'w') as file:
        json.dump(actual_json, file)


def generic_mongodb_recreate_collection(collname, dumpfp, record_count):
    mongodb = get_qa_mongo_wrap(collname, 'QAContentProvider')
    dump_path = '/tsw/harvesters/driver/content_providers/genericmongodb/' + dumpfp

    load_dump = True
    if mongodb.collection_exists():
        if mongodb.coll.count() == record_count:
            load_dump = False
    if load_dump:
        mongodb.drop_collection()
        mongodb.load_dump_into_collection(dump_path)
    mongodb.add_index('facts.factName', 1)
    mongodb.add_index('urlId', 1)

    if not mongodb.collection_exists():
        raise Exception('Recreation of collection: %s failed.' % collname)


class ContentProviderBase(SandboxedTest):
    """Content provider tests using driver"""
    default_har_config = HarvesterQuality
    content_provider_name = 'File'

    def setUp(self):
        super(ContentProviderBase, self).setUp()
        LOCAL_PROP_FILE.remove_p()
        self.har = Harvester(HarvesterQuality())
        self.har.remove_harvester_log()

        self.harvester_prop = quality_properties(content_provider=self.content_provider_name + 'ContentProvider',
                                                 properties_as_dict=C_PROVIDER_KEYS_MAP[self.content_provider_name],
                                                 content_parser='CSVContentParser')

    def run_content_provider_test(self, prop_file, class_name, err_str=None):
        sto, ste = ShellExecutor.run_wait_standalone(CMD_CP_TMPL % {'prop': prop_file, 'class': class_name})
        if ste:
            logging.error('Content Provider driver execution error. %s', ste)
        stdoe = sto + ste
        if err_str:
            if err_str not in stdoe:
                raise TestFailure('%s was not found in log' % err_str)
            return True
        return stdoe

    @staticmethod
    def ftp_check_file_download(file_list, stdoe):
        file_dict = {}
        for file_name in file_list:
            pat = 'Downloading %s to (.*)\n' % file_name
            matches = re.findall(pat, stdoe)
            if matches:
                file_dict[file_name] = matches[0]
            else:
                file_dict[file_name] = None
        return file_dict

    @staticmethod
    def files_from_stdout(stdoe, file_list=None):
        file_log_line = ''
        file_d = {}
        for line in stdoe.splitlines(keepends=False):
            if line.startswith('[ "'):
                file_log_line += line + '\n'
        pat = '"([^"]*)"'
        matches = re.findall(pat, file_log_line)
        if file_list is None:
            return matches

        if len(matches) != len(file_list):
            raise TestFailure('No of files processed does not match the length of input file_list')
        for match in matches:
            for file_name in file_list:
                if match.endswith('/' + file_name):
                    file_d[file_name] = match
        logging.warning(file_d)
        return file_d


class FileContentProvider(ContentProviderBase):
    """File content provider tests"""
    content_provider_name = 'File'

    def test_01(self):
        """Required property: sourceDir is invalid"""
        err_str = "Required property: sourceDir is invalid"
        pob = self.harvester_prop
        del pob[self.content_provider_name + 'ContentProvider.sourceDir']
        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE,
                                                DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_02(self):
        """sourceDir does not exist"""
        err_str = "Unable to process files in directory. No files were found that matched fileRegex property."
        pob = self.harvester_prop
        pob[self.content_provider_name + 'ContentProvider.sourceDir'] = './non-existing-dir'
        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE,
                                                DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_03(self):
        """Empty source directory"""
        err_str = "Unable to process files in directory. No files were found that matched fileRegex property."
        pob = self.harvester_prop
        src_key = self.content_provider_name + 'ContentProvider.sourceDir'
        pob[src_key] = runtime.data_path + '/tsw/harvesters/driver/content_providers/file/source/empty'
        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE,
                                                DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_04(self):
        """No file regex"""
        err_str = "No regex property found.  Setting regex"
        pob = self.harvester_prop
        file_key = self.content_provider_name + 'ContentProvider.fileRegex'
        del pob[file_key]
        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE,
                                                DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_05(self):
        """Process 2 files"""
        err_str = 'FileContentProvider.getContent Completed processing2 files'
        pob = self.harvester_prop
        src_key = self.content_provider_name + 'ContentProvider.sourceDir'
        src_dir = Path('2-files')
        src_dir.rmtree_p()
        src_dir.makedirs_p()
        for file in Path(pob[src_key] + '/2-files/').files():
            file.copy2(src_dir)
        src_dir.joinpath('.svn').rmtree_p()
        pob[src_key] = src_dir
        pob.write_to_file(LOCAL_PROP_FILE)

        stdoe = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name])
        if err_str not in stdoe:
            raise TestFailure('Error string not found in log.')

        file_list = ['a.txt', 'sample.txt']
        file_d = self.files_from_stdout(stdoe, file_list)

        for key in file_list:
            try:
                if not Path(file_d[key]).isfile():
                    logging.error('Unable to parse downloaded file for %s' % key)
            except:
                logging.error('Unable to verify downloaded file - %s' % key)
                raise

        file_name = 'sample.txt'
        expected_md5 = '84fb7eef50905958976cd8c991b4baac'
        local_file_name = file_d[file_name]
        actual_md5 = Path(local_file_name).read_hexhash("md5")
        self.assertEqual(actual_md5, expected_md5, 'md5 mismatch for downloaded file.')

        file_name = 'a.txt'
        expected_md5 = 'f3945698918f3906082d3480d9cbd311'
        local_file_name = file_d[file_name]
        actual_md5 = Path(local_file_name).read_hexhash("md5")
        self.assertEqual(actual_md5, expected_md5, 'md5 mismatch for downloaded file.')


class FTPContentProvider(ContentProviderBase):
    """FTP content provider tests"""
    content_provider_name = 'FTP'

    @classmethod
    def setUpClass(cls):
        super(FTPContentProvider, cls).setUpClass()
        # cls.ftp_process = ftp_subprocess('user:pass:' + runtime.data_path +
        # '/tsw/harvesters/driver/content_providers/server_root/')

    @classmethod
    def tearDownClass(cls):
        # cls.ftp_process.terminate()
        super(FTPContentProvider, cls).tearDownClass()

    def test_missing_user_name(self):
        err_str = "Missing required 'username' property"
        pob = self.harvester_prop

        del pob[self.content_provider_name + 'ContentProvider.username']
        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string was found in log file.")

    def test_missing_password(self):
        err_str = "Missing required 'password' property"
        pob = self.harvester_prop
        del pob[self.content_provider_name + 'ContentProvider.password']

        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_missing_hostname(self):
        err_str = "Missing required 'host' property"
        pob = self.harvester_prop
        del pob[self.content_provider_name + 'ContentProvider.host']

        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_missing_port(self):
        err_str = "Unable to connect to FTP server 'localhost:21': Connection refused"
        pob = self.harvester_prop
        del pob[self.content_provider_name + 'ContentProvider.port']

        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_invalid_port(self):
        err_str = "java.lang.IllegalArgumentException: port out of range"
        pob = self.harvester_prop
        pob[self.content_provider_name + 'ContentProvider.port'] = '787878'

        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_empty_port(self):
        err_str = "Invalid port specified:"
        pob = self.harvester_prop
        pob[self.content_provider_name + 'ContentProvider.port'] = ''
        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_missing_directory(self):
        err_str = "Missing required 'directory' property"
        pob = self.harvester_prop
        del pob[self.content_provider_name + 'ContentProvider.directory']

        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_non_existing_directory(self):
        err_str = "Unable to change directory on FTP server"
        pob = self.harvester_prop
        pob[self.content_provider_name + 'ContentProvider.directory'] = 'NoSuchDirectoryOnServer'

        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_empty_directory(self):
        err_str = "Unable to change directory on FTP server"
        pob = self.harvester_prop
        pob[self.content_provider_name + 'ContentProvider.directory'] = 'empty'

        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_invalid_host(self):
        err_str = "Unable to connect to FTP server"
        pob = self.harvester_prop
        pob[self.content_provider_name + 'ContentProvider.host'] = 'invalidhostzxcfda.wsrlab'

        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_wrong_auth(self):
        err_str = "Unable to login to FTP server"
        pob = self.harvester_prop
        pob[self.content_provider_name + 'ContentProvider.username'] = 'wrong-user'

        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_successful_login(self):
        err_str = "Changing directory to"
        pob = self.harvester_prop

        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_download_sample_file(self):
        pob = self.harvester_prop
        pob.write_to_file(LOCAL_PROP_FILE)
        stdoe = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name])

        expected_md5 = '84fb7eef50905958976cd8c991b4baac'

        file_name = 'sample.txt'
        file_d = self.ftp_check_file_download([file_name], stdoe)

        local_file_name = file_d[file_name]
        actual_md5 = Path(local_file_name).read_hexhash("md5")
        self.assertEqual(actual_md5, expected_md5, 'md5 mismatch for downloaded file.')

    def test_download_all_files(self):
        pob = self.harvester_prop
        pob['FTPContentProvider.fileRegex'] = '.*'
        pob.write_to_file(LOCAL_PROP_FILE)

        stdoe = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name])

        file_list = ['a.txt', 'sample.txt']

        file_d = self.ftp_check_file_download(file_list, stdoe)

        for key in file_list:
            try:
                if not Path(file_d[key]).isfile():
                    logging.error('Unable to parse downloaded file for %s' % key)
            except:
                logging.error('Unable to verify downloaded file - %s' % key)
                raise

        file_name = 'sample.txt'
        expected_md5 = '84fb7eef50905958976cd8c991b4baac'
        local_file_name = file_d[file_name]
        actual_md5 = Path(local_file_name).read_hexhash("md5")
        self.assertEqual(actual_md5, expected_md5, 'md5 mismatch for downloaded file.')

        file_name = 'a.txt'
        expected_md5 = 'f3945698918f3906082d3480d9cbd311'
        local_file_name = file_d[file_name]
        actual_md5 = Path(local_file_name).read_hexhash("md5")
        self.assertEqual(actual_md5, expected_md5, 'md5 mismatch for downloaded file.')

    def test_invalid_regex(self):
        err_str = 'Invalid pattern specifed:'

        pob = self.harvester_prop
        pob['FTPContentProvider.fileRegex'] = '['
        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string was found in log file.")


class HTTPContentProvider(ContentProviderBase):
    """HTTP content provider tests"""
    content_provider_name = 'HTTP'
    http_log_file = Path('/tmp/http_service.log')
    src_url_key = content_provider_name + 'ContentProvider.source_url'
    key_prefix = content_provider_name + 'ContentProvider'

    @classmethod
    def remove_http_service_file(cls):
        cls.http_log_file.remove_p()

    def test_01(self):
        """ Missing required 'HTTPContentProvider.source_url' property."""
        err_str = " Missing required 'HTTPContentProvider.source_url' property."
        pob = self.harvester_prop
        del pob[self.key_prefix + '.source_url']
        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_02(self):
        """No user name"""
        err_str = "Unable to download url:"
        pob = self.harvester_prop
        del pob[self.key_prefix + '.userName']
        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_03(self):
        """No pass word"""
        err_str = "Unable to download url:"
        pob = self.harvester_prop
        del pob[self.key_prefix + '.password']
        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_04(self):
        """Wrong Auth"""
        err_str = "Unable to download url:"
        pob = self.harvester_prop
        pob[self.key_prefix + '.userName'] = 'unknown'
        pob[self.key_prefix + '.password'] = 'unknown'
        pob[self.key_prefix + '.source_url'] += 'sample.txt'
        pob.write_to_file(LOCAL_PROP_FILE)

        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string found in log file.")

    def test_05(self):
        """Download text file"""
        err_str = "HTTPContentProvider.getContent Completed downloading 1 item"
        pob = self.harvester_prop
        pob[self.src_url_key] += '/sample.txt'
        pob.write_to_file(LOCAL_PROP_FILE)

        expected_md5 = '84fb7eef50905958976cd8c991b4baac'
        self.http_download_check_md5(err_str, expected_md5)

    def http_download_check_md5(self, err_str, expected_md5):
        stdoe = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name])
        assert err_str in stdoe
        downloaded_file = Path(self.files_from_stdout(stdoe)[0])
        logging.info('Downloaded file: %s' % downloaded_file)
        try:
            if not downloaded_file.isfile():
                logging.error('Unable to parse downloaded file for %s' % downloaded_file)
        except:
            logging.error('Unable to verify downloaded file - %s' % downloaded_file)
            raise
        actual_md5 = Path(downloaded_file).read_hexhash("md5")
        assert actual_md5 == expected_md5

    def test_06(self):
        """Download binary mode"""
        err_str = "HTTPContentProvider.getContent Completed downloading 1 item"
        pob = self.harvester_prop
        pob[self.src_url_key] += '/sample.tgz'
        pob['ContentExtractor.className'] = \
            'com.securecomputing.sftools.harvester.contentExtractors.TarGZContentExtractor'
        pob[self.key_prefix + '.binaryMode'] = 'true'
        pob.write_to_file(LOCAL_PROP_FILE)

        expected_md5 = '918b3e1679c0df34b67bd34ba06329ab'

        self.http_download_check_md5(err_str, expected_md5)

    # def test_07(self):
    #     """No user agent"""
    #     err_str = "HTTPContentProvider.getAgent Completed downloading 1 item"
    #     pob = self.harvester_prop
    #     pob['HTTPContentProvider.userAgent'] = 'xxxx'
    #     pob[self.src_url_key] += '/sample.txt'
    #     # pob[self.key_prefix + 'binaryMode'] = 'true'
    #     pob.write_to_file(LOCAL_PROP_FILE)
    #
    #     expected_md5 = '84fb7eef50905958976cd8c991b4baac'
    #
    #     self.http_download_check_md5(err_str, expected_md5)


class GenericMongoDB(ContentProviderBase):
    """SEO Mongo DB content provider tests"""
    content_provider_name = 'GenericMongoDB'
    content_provider_name_short = 'MongoDB'
    data_dir = runtime.data_path.joinpath('tsw/harvesters/driver/content_providers/genericmongodb')

    @classmethod
    def setUpClass(cls):
        super(GenericMongoDB, cls).setUpClass()
        #MongoDB setup
        generic_mongodb_recreate_collection('scorer_results', 'scorer_results.mongodump', 3)
        generic_mongodb_recreate_collection('secondary_scorer_results', 'secondary_scorer_results.mongodump', 524970)

    def test_01(self):
        """TS-3095:GenericMongoDBContentProvider: Bad port Number."""
        err_str = 'Bad port number.'
        propobj = self.harvester_prop

        propobj[self.content_provider_name_short + 'ContentProvider.port'] = '27i07'
        propobj.write_to_file(LOCAL_PROP_FILE)
        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string '%s' was found in log file." % err_str)

    def test_02(self):
        """TS-3096:GenericMongoDBContentProvider: Bad host name."""
        err_str = 'Bad host.'
        propobj = self.harvester_prop

        propobj[self.content_provider_name_short + 'ContentProvider.host'] = 'tsqamongodb01wsrlab'
        propobj.write_to_file(LOCAL_PROP_FILE)
        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string '%s' was found in log file." % err_str)

    def test_04(self):
        """TS-3097:GenericMongoDBContentProvider: Missing host property."""
        err_str = 'Missing required \'MongoDBContentProvider.host\' property.'
        propobj = self.harvester_prop

        del propobj['MongoDBContentProvider.host']
        propobj.write_to_file(LOCAL_PROP_FILE)
        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string '%s' was found in log file." % err_str)

    def test_05(self):
        """TS-3098:GenericMongoDBContentProvider: Missing MongoDBContentProvider.port property."""
        err_str = 'Missing required \'MongoDBContentProvider.port\' property.'
        propobj = self.harvester_prop

        del propobj['MongoDBContentProvider.port']
        propobj.write_to_file(LOCAL_PROP_FILE)
        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string '%s' was found in log file." % err_str)

    def test_06(self):
        """TS-3099:GenericMongoDBContentProvider: Missing MongoDBContentProvider.database property."""
        err_str = 'Missing required \'MongoDBContentProvider.database\' property.'
        propobj = self.harvester_prop

        del propobj['MongoDBContentProvider.database']
        propobj.write_to_file(LOCAL_PROP_FILE)
        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string '%s' was found in log file." % err_str)

    def test_07(self):
        """TS-3100:GenericMongoDBContentProvider: Missing MongoDBContentProvider.collection property."""
        err_str = 'Missing required \'MongoDBContentProvider.collection\' property.'
        propobj = self.harvester_prop

        del propobj['MongoDBContentProvider.collection']
        propobj.write_to_file(LOCAL_PROP_FILE)
        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string '%s' was found in log file." % err_str)

    def test_08(self):
        """TS-3101:GenericMongoDBContentProvider: Missing MongoDBContentProvider.mongoQuery property."""
        err_str = 'Missing required \'mongoQuery\' property.'
        propobj = self.harvester_prop

        del propobj['mongoQuery']
        propobj.write_to_file(LOCAL_PROP_FILE)
        result = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name],
                                                err_str=err_str)
        self.assertTrue(result, "Error string '%s' was found in log file." % err_str)

    def test_09(self):
        """TS-3106 : GenericMongoDBContentProvider: Missing mongoSortKey property."""
        propobj = self.harvester_prop

        del propobj['mongoSortKey']
        propobj.write_to_file(LOCAL_PROP_FILE)
        stdoe = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name])
        actual_file = self.files_from_stdout(stdoe)[0]
        generic_mongodb_remove_id_from_json(actual_file)
        expected_file = self.data_dir.joinpath('sampleout09.txt')
        self.assert_json_file_equal(expected_file, actual_file)

    def test_10(self):
        """TS-3107 : GenericMongoDBContentProvider: Missing mongoProjection property."""
        propobj = self.harvester_prop

        del propobj['mongoProjection']
        propobj.write_to_file(LOCAL_PROP_FILE)
        stdoe = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name])
        actual_file = self.files_from_stdout(stdoe)[0]
        generic_mongodb_remove_id_from_json(actual_file)
        expected_file = self.data_dir.joinpath('sampleout10.txt')
        self.assert_json_file_equal(expected_file, actual_file)

    def test_11(self):
        """TS-3105 : GenericMongoDBContentProvider: mongoQuery property is empty json."""
        propobj = self.harvester_prop

        propobj['mongoQuery'] = '{}'
        propobj.write_to_file(LOCAL_PROP_FILE)
        stdoe = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name])
        actual_file = self.files_from_stdout(stdoe)[0]
        generic_mongodb_remove_id_from_json(actual_file)
        expected_file = self.data_dir.joinpath('sampleout11.txt')
        self.assert_json_file_equal(expected_file, actual_file)

    def test_12(self):
        """TS-3102 : GenericMongoDBContentProvider: Positive test case."""
        propobj = self.harvester_prop

        propobj.write_to_file(LOCAL_PROP_FILE)
        stdoe = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name])
        actual_file = self.files_from_stdout(stdoe)[0]
        generic_mongodb_remove_id_from_json(actual_file)
        expected_file = self.data_dir.joinpath('sampleout12.txt')
        self.assert_json_file_equal(expected_file, actual_file)

    def test_13(self):
        """TS-3104 : GenericMongoDBContentProvider: No facts in mongoProjection property."""
        propobj = self.harvester_prop

        propobj['mongoProjection'] = '{ "urlString":1, "completeDate":1}'
        propobj.write_to_file(LOCAL_PROP_FILE)
        stdoe = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name])
        actual_file = self.files_from_stdout(stdoe)[0]
        generic_mongodb_remove_id_from_json(actual_file)
        expected_file = self.data_dir.joinpath('sampleout13.txt')
        self.assert_json_file_equal(expected_file, actual_file)

    def test_14(self):
        """TS-3103 : GenericMongoDBContentProvider: Positive test case for 100 records."""
        propobj = self.harvester_prop

        propobj[self.content_provider_name_short + 'ContentProvider.collection'] = 'secondary_scorer_results'
        propobj.write_to_file(LOCAL_PROP_FILE)
        stdoe = self.run_content_provider_test(LOCAL_PROP_FILE, DEFAULT_CLASS[self.content_provider_name])
        actual_file = self.files_from_stdout(stdoe)[0]
        generic_mongodb_remove_id_from_json(actual_file)
        expected_file = self.data_dir.joinpath('sampleout14.txt')
        self.assert_json_file_equal(expected_file, actual_file)
