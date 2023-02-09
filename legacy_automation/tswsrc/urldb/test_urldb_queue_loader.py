# coding=utf-8
"""
=============================
URLDB queue loader test cases
=============================
"""

__author__ = 'abhijeet'
import json
import unittest
from runtime import data_path
from urldb.urldb_lib import URLDB
from conf.properties import set_prop_application
from conf.files import LOG
from conf.files import PROP
from conf.files import DIR


DEFAULT_FILE_DEST = DIR.urldb_json_dir
AGENTS_LOG = LOG.agents
APPLICATION_PROP = PROP.application

def check_string_in_file(string, filename):
    with filename.open('r') as file:
        if string in file.read():
            return True
    return False

class TestUrldbQueueLoaderRun1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        will run queue loader once for a few different test cases and take care of clean up for the run
        """
        set_prop_application() # set application properties from properties.py
        if AGENTS_LOG.exists():
            f=open(AGENTS_LOG,"w")
            f.seek(0)
            f.truncate()
        #     AGENTS_LOG.remove() # remove agents.log
        urldb_obj = URLDB()
        urldb_obj.clean_urldb_queue_table()
        urldb_obj.clean_urldb_dir()
        urldb_obj.clean_url_coll()
        urldb_obj.clean_harvester_event_coll()
        urldb_obj.clean_workflow_event_coll()
        if not DEFAULT_FILE_DEST.exists():
            DEFAULT_FILE_DEST.makedirs()

        def stage_input_files_to_urldb_queue(filename):
            base_data_path = data_path.joinpath('urldb/write_api_n_agent')
            input_file = base_data_path.joinpath(filename)
            target_file = DEFAULT_FILE_DEST.joinpath(filename)
            input_file.copyfile(target_file, follow_symlinks=False)
            urldb_obj.create_urldb_queue_record(str(target_file), 'APWG')

        stage_input_files_to_urldb_queue('urldb_invalidsource.json') # stage invalid source json
        stage_input_files_to_urldb_queue('urldb-harvester.json') # stage valid json
        stage_input_files_to_urldb_queue('urldb-supported-shortened-url.json') # stage shortened url
        stage_input_files_to_urldb_queue('urldb-securityworkflow.json')# stage workflow json
        stage_input_files_to_urldb_queue('urldb-supported-shortened-url.json')
        stage_input_files_to_urldb_queue('urldb-unsupported-shortened-url.json')
        urldb_obj.create_urldb_queue_record('non-existent.json', 'APWG') # stage non existent file
        urldb_obj.run_urldbqueue_agent()

    def setUp(self):
        """
        setup for any common initialization before each test case
        """
        super(TestUrldbQueueLoaderRun1, self).setUp()
        self.urldb_cobj = URLDB()

    def test_create_collection(self):
        """
        tests whether the collections are created or not
        """
        assert self.urldb_cobj.collection_exists('url')
        assert self.urldb_cobj.collection_exists('harvester_event')
        assert self.urldb_cobj.collection_exists('workflow_event')

    def test_create_collection2(self):
        """
        tests whether the collections are created or not
        """
        assert self.urldb_cobj.collection_exists('url')
        assert self.urldb_cobj.collection_exists('harvester_event')
        assert self.urldb_cobj.collection_exists('workflow_event')


    def test_metadata_validation_harv(self):
        """
        tests whether metadata is correctly persisted in url and harvester event collections
        """
        url_dict = self.urldb_cobj.url_coll_get_url('*://DEFAULTRULE.COM')
        assert url_dict # assert that the url dict is not None; URL is present in url collection
        # assert fixed metadata in url collection
        assert url_dict['_id'] == '0X01960061847b0177f236a9a3'
        assert url_dict['url'] == '*://DEFAULTRULE.COM'
        assert url_dict['rootDomain'] == 'defaultrule.com'

        # harvester event metadata
        url_hash = url_dict['_id']
        har_event_cursor = self.urldb_cobj.har_event_coll_get_events_for_urlhash(url_hash)
        har_events = [doc for doc in har_event_cursor]
        assert len(har_events) == 1 # assert there is only one harvester event for the url
        event = har_events[0]
        assert event['source'] == 'APWG'
        assert event['urlHash'] == '0X01960061847b0177f236a9a3'

        def check_name_value_pair(dict_obj, name, value):
            if dict_obj['name'] == name and dict_obj['value'] == value:
                return True
            else:
                return False


        assert check_name_value_pair(event['metadata'][0], 'date_added', '2013-01-22 05:32:44')
        assert check_name_value_pair(event['metadata'][1], 'harvester_name', 'APWG')
        assert check_name_value_pair(event['metadata'][2], 'score', '10')
        assert check_name_value_pair(event['metadata'][3], 'target', 'EBAY')
        assert check_name_value_pair(event['metadata'][4], 'type', 'URL')
        assert check_name_value_pair(event['metadata'][5], 'url', 'http://defaultrule.com')
        assert check_name_value_pair(event['metadata'][6], 'url_encoded', '')

    def test_metadata_validation_harv2(self):
        """
        tests whether metadata is correctly persisted in url and harvester event collections
        """
        url_dict = self.urldb_cobj.url_coll_get_url('*://DEFAULTRULE.COM')
        assert url_dict # assert that the url dict is not None; URL is present in url collection
        # assert fixed metadata in url collection
        assert url_dict['_id'] == '0X01960061847b0177f236a9a3'
        assert url_dict['url'] == '*://DEFAULTRULE.COM'
        assert url_dict['rootDomain'] == 'defaultrule.com'

        # harvester event metadata
        url_hash = url_dict['_id']
        har_event_cursor = self.urldb_cobj.har_event_coll_get_events_for_urlhash(url_hash)
        har_events = [doc for doc in har_event_cursor]
        assert len(har_events) == 1 # assert there is only one harvester event for the url
        event = har_events[0]
        assert event['source'] == 'APWG'
        assert event['urlHash'] == '0X01960061847b0177f236a9a3'

        def check_name_value_pair(dict_obj, name, value):
            if dict_obj['name'] == name and dict_obj['value'] == value:
                return True
            else:
                return False


        assert check_name_value_pair(event['metadata'][0], 'date_added', '2013-01-22 05:32:44')
        assert check_name_value_pair(event['metadata'][1], 'harvester_name', 'APWG')
        assert check_name_value_pair(event['metadata'][2], 'score', '10')
        assert check_name_value_pair(event['metadata'][3], 'target', 'EBAY')
        assert check_name_value_pair(event['metadata'][4], 'type', 'URL')
        assert check_name_value_pair(event['metadata'][5], 'url', 'http://defaultrule.com')
        assert check_name_value_pair(event['metadata'][6], 'url_encoded', '')

    def test_metadata_validation_workflow(self):
        """
        tests whether the workflow events are written properly
        """
        url_dict = self.urldb_cobj.url_coll_get_url('FTP://GOOGLE.COM')
        assert url_dict
        assert url_dict['_id'] == '0Xb1c4015a0eff96d05844f92a'
        assert url_dict['url'] == 'FTP://GOOGLE.COM'
        assert url_dict['rootDomain'] == 'google.com'
        # workflow event metadata
        url_hash = url_dict['_id']
        workflow_events_cursor = self.urldb_cobj.workflow_event_coll_get_events_for_urlhash(url_hash)
        workflow_events = [doc for doc in workflow_events_cursor]
        assert  len(workflow_events) == 1
        event = workflow_events[0]
        assert event['source'] == 'SecurityWorkflow'
        assert event['urlHash'] == '0Xb1c4015a0eff96d05844f92a'

        def check_name_value_pair(dict_obj, name, value):
            if dict_obj['name'] == name and dict_obj['value'] == value:
                return True
            else:
                return False

        def make_dict_from_nv_pairs(nv_list):
            res_dict = {}
            for pair in nv_list:
                res_dict['%s' % pair['name']] = pair['value']
            return res_dict

        input_file = data_path.joinpath('urldb/write_api_n_agent/urldb-securityworkflow.json')
        with open(input_file, 'r') as file:
            input_json = json.load(file)
        validation_dict = make_dict_from_nv_pairs(input_json['urlEvents'][0]['rawMetadata'])
        assert make_dict_from_nv_pairs(event['metadata']) == validation_dict
        """
        assert check_name_value_pair(event['metadata'][0], 'httpReturnCode', '0')
        assert check_name_value_pair(event['metadata'][1], 'SampleDBWorkerExitStatus',
                                     'Failure: No Record ID found for the content')
        assert check_name_value_pair(event['metadata'][2], 'gsbExitStatus', 'Success')
        assert check_name_value_pair(event['metadata'][3], 'endUrl', '')
        assert check_name_value_pair(event['metadata'][4], 'recordId', None)
        assert check_name_value_pair(event['metadata'][5], 'WebFetcherScorerMessage',
                                     'Unable to crawl URL. Content path not populated')
        assert check_name_value_pair(event['metadata'][6], 'fetchedUrl', 'ftp://google.com')
        assert check_name_value_pair(event['metadata'][7], 'gsbIsMalware', 'false')
        assert check_name_value_pair(event['metadata'][8], 'gsbIsPhishing', 'false')
        """

    def test_raw_url_validation(self):
        """
        tests whether the raw url is preserved
        """
        url_dict = self.urldb_cobj.url_coll_get_url('*://DEFAULTRULE.COM')
        assert url_dict
        value=url_dict['rawUrlInfo']
        assert value[0]['rawUrl'] == 'http://defaultrule.com'\

    def test_create_new_record(self):
        """
        tests whether the raw url is preserved
        """
        url_dict = self.urldb_cobj.url_coll_get_url('*://DEFAULTRULE.COM')
        assert url_dict
        value=url_dict['rawUrlInfo']
        assert value[0]['rawUrl'] == 'http://defaultrule.com'

    def test_validate_root_domain(self):
        """
        check whether root domain is correctly recorded
        """
        url_dict = self.urldb_cobj.url_coll_get_url('*://TEST.COM/pathstring')
        assert url_dict['rootDomain'] == 'test.com'
        url_dict = self.urldb_cobj.url_coll_get_url('*://DEFAULTRULE.COM')
        assert url_dict['rootDomain'] == 'defaultrule.com'

    def test_skip_pending_records(self):
        """
        tests whether the agent skips already pending records
        """
        sql = "select * from U2.dbo.urldb_queue where file_path = 'non-existent.json'"
        uq_cursor = self.urldb_cobj.get_urldb_queue_records(sql)
        uq_records = [record for record in uq_cursor]
        assert len(uq_records) == 1
        assert uq_records[0]['pending'] == True

    def test_urldb_queue_records_clearance(self):
        """
        tests whether records from urldb_queue are removed after execution
        """
        uq_cursor = self.urldb_cobj.get_urldb_queue_records('select * from urldb_queue')
        uq_records = [record for record in uq_cursor]
        assert len(uq_records) == 2 #all records except for two expected records which 1)is already set to pending
        # 2)has invalid source

    def test_urldb_queue_pending0(self):
        """
        tests whether records from urldb_queue are removed after execution
        """
        uq_cursor = self.urldb_cobj.get_urldb_queue_records('select * from urldb_queue')
        uq_records = [record for record in uq_cursor]
        assert len(uq_records) == 2 #all records except for two expected records which 1)is already set to pending
        # 2)has invalid source
        uq_cursor = self.urldb_cobj.get_urldb_queue_records('select * from urldb_queue where pending = 0')
        uq_records = [record for record in uq_cursor]
        assert len(uq_records) == 0 #all records with pending =0 are sucessfully processed



    def test_urldb_queue_processing_sucessfull(self):
        """
        tests whether agent is processing all the files sucessfully
        """
        uq_cursor = self.urldb_cobj.get_urldb_queue_records('select * from urldb_queue')
        uq_records = [record for record in uq_cursor]
        assert len(uq_records) == 2 #all records except for two expected records which 1)is already set to pending
        # 2)has invalid source

    def test_protocol_port_trims(self):
        """
        tests whether standard protocols are being trimmed
        """

        def url_x_is_y_in_url_coll(x, y):
            url_dict = self.urldb_cobj.url_coll_get_url(x)
            assert url_dict is None
            url_dict = self.urldb_cobj.url_coll_get_url(y)
            assert url_dict is not None

        url_x_is_y_in_url_coll('http://facebook.com', '*://FACEBOOK.COM')
        url_x_is_y_in_url_coll('www.mcafee.com', '*://MCAFEE.COM')
        url_x_is_y_in_url_coll('google.com:80', '*://GOOGLE.COM')
        url_x_is_y_in_url_coll('www.testtwo.com:443', '*://TESTTWO.COM')


    def test_seen_count(self):
        """
        tests whether seen count increases if same url is referred
        """
        url_dict = self.urldb_cobj.url_coll_get_url('*://TESTTHREE.COM')
        assert url_dict['seenCount'] == 2

    def test_update_existing_record(self):
        """
        tests whether existing records gets updated if same url is referred
        """
        url_dict = self.urldb_cobj.url_coll_get_url('*://TESTTHREE.COM')
        assert url_dict['seenCount'] == 2

    def test_last_seen_change(self):
        """
        tests whether last seen changes when same url is referred again
        """

        base_data_path = data_path.joinpath('urldb/write_api_n_agent')
        input_file = base_data_path.joinpath('urldb_jsontocreatetimedifference.json')
        target_file = DEFAULT_FILE_DEST.joinpath('urldb_jsontocreatetimedifference.json')
        input_file.copyfile(target_file, follow_symlinks=False)
        self.urldb_cobj.create_urldb_queue_record(str(target_file), 'APWG')
        self.urldb_cobj.run_urldbqueue_agent()

        url_dict = self.urldb_cobj.url_coll_get_url('*://TESTTHREE.COM')
        ls = url_dict['lastSeen']
        fs = url_dict['firstSeen']
        assert ls != fs
        assert ls > fs



    def test_skip_invalid_urls(self):
        """
        tests whether invalid/malformed urls are skipped from being written to URLDB
        """
        with open(AGENTS_LOG, 'r') as agentslog:
            query_string = " Unable to canonicalize the URL. url=!http://invalidurl.com"
            assert query_string in agentslog.read()

    def test_skip_malformed_urls(self):
        """
        tests whether invalid/malformed urls are skipped from being written to URLDB
        """
        with open(AGENTS_LOG, 'r') as agentslog:
            query_string = " Unable to canonicalize the URL. url=!http://invalidurl.com"
            assert query_string in agentslog.read()

    def test_error_recorded(self):
        """
        tests whether invalid/malformed urls are skipped from being written to URLDB
        """
        with open(AGENTS_LOG, 'r') as agentslog:
            query_string = " Unable to canonicalize the URL. url=!http://invalidurl.com"
            assert query_string in agentslog.read()

    def test_keep_unworked_files(self):
        """
        tests whether unworked files are preserved in file system
        """
        sql = "select * from U2.dbo.urldb_queue where file_path like '%urldb_invalidsource.json'"
        uq_cursor = self.urldb_cobj.get_urldb_queue_records(sql)
        uq_records = [record for record in uq_cursor]
        assert len(uq_records) == 1
        assert uq_records[0]['pending'] == True

    def test_shortened_url_not_skipped(self):
        """
        test whether supported shortened url is not skipped
        """
        warning_string = 'Skipping shortened URL. url=http://goo.gl/lwjKRN'
        assert check_string_in_file(warning_string, AGENTS_LOG) == False

    def test_unsupported_shortened_url_skipped(self):
        """
        tests whether unsupported shortened urls are skipped or not
        """
        warning_string = 'Unable to expand url=*://hsblinks.com/falslnk Message: Shortening service is currently ' \
                         'unsupported for getting the full URL. shorteningService=hsblinks.com'
        assert check_string_in_file(warning_string, AGENTS_LOG) == True


class TestUrldbQueueLoaderRun2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        will run queue loader once for a few different test cases and take care of clean up for the run
        """
        app_prop_dict = set_prop_application() # set application properties from properties.py
        del app_prop_dict['urldb.expandShortenedUrls']
        app_prop_dict.write_to_file(APPLICATION_PROP)
        if AGENTS_LOG.exists():
            f=open(AGENTS_LOG,"w")
            f.seek(0)
            f.truncate()

            # AGENTS_LOG.remove() # remove agents.log
        urldb_obj = URLDB()
        urldb_obj.clean_urldb_queue_table()
        urldb_obj.clean_urldb_dir()
        urldb_obj.clean_url_coll()
        urldb_obj.clean_harvester_event_coll()
        urldb_obj.clean_workflow_event_coll()
        if not DEFAULT_FILE_DEST.exists():
            DEFAULT_FILE_DEST.makedirs()

        def stage_input_files_to_urldb_queue(filename):
            base_data_path = data_path.joinpath('urldb/write_api_n_agent')
            input_file = base_data_path.joinpath(filename)
            target_file = DEFAULT_FILE_DEST.joinpath(filename)
            input_file.copyfile(target_file, follow_symlinks=False)
            urldb_obj.create_urldb_queue_record(str(target_file), 'APWG')

        stage_input_files_to_urldb_queue('urldb-supported-shortened-url.json')
        urldb_obj.run_urldbqueue_agent()

    def setUp(self):
        """
        setup for any common initialization before each test case
        """
        super(TestUrldbQueueLoaderRun2, self).setUp()
        self.urldb_cobj = URLDB()

    def test_shortened_url_skipped(self):
        """
        tests whether shortened urls are skipped when urldb.expandShortenedUrls property is not defined
        """
        warning_string = 'Skipping shortened URL. url=http://goo.gl/lwjKRN'
        assert check_string_in_file(warning_string, AGENTS_LOG) == True