# coding=utf-8
"""
=====================================
Harvester framework changes for URLDB
=====================================
"""

__author__ = 'abhijeet'

import json

import pytest
from path import Path

from harvesters.harvester import Harvester
from harvesters.harvester_config import HarvesterAPWG
from urldb.urldb_lib import URLDB
from harvesters.qaharvester import HarvesterQuality
import runtime
from runtime import data_path
from conf.properties import prop_harvester
from conf.files import DIR


APWG_PROPERTY = Path('/opt/sftools/conf/APWG.properties')
APWG_SOURCE_DIRECTORY = Path('/tmp/test_auto/harvester/APWG_src/')
DEFAULT_FILE_DEST = DIR.urldb_json_dir


@pytest.fixture()
def urldbcleanup():
    """
    clean up urldb queues
    """
    urldb = URLDB()
    urldb.clean_urldb_queue_table()
    urldb.clean_urldb_dir()
    prop_harvester(harvester_name='APWG', write_file_name=APWG_PROPERTY) #writes default APWG properties for setup
    if not DEFAULT_FILE_DEST.exists():
        DEFAULT_FILE_DEST.makedirs()
    if APWG_SOURCE_DIRECTORY.exists():
        if not APWG_SOURCE_DIRECTORY.listdir() is None:
            for file in APWG_SOURCE_DIRECTORY.listdir():
                if file.isfile():
                    file.remove()
        APWG_SOURCE_DIRECTORY.removedirs()
    APWG_SOURCE_DIRECTORY.makedirs()


@pytest.mark.usefixtures("urldbcleanup")
class Test_Urldb_Harvester_Framework():
    @classmethod
    @pytest.fixture(scope='class', autouse=True)
    def common_object_references(self):
        self.har_quality = HarvesterQuality()
        self.har_obj = Harvester(HarvesterAPWG())
        self.base_data_path = (runtime.data_path + '/urldb/harvester_framework')
        #self.base_data_path = Path.joinpath(data_path, 'urldb/harvester_framework')
        self.urldb_cobj = URLDB()

    def test_json_file_generation(self):
        """
        test if json files are generated on harvester execution and the corresponding record is created in urldb_queue.
        also tests whether the source is correct: APWG.
        test data has only two urls and creates only one json
        """
        input_file = self.base_data_path.joinpath('positive-two-urls.txt')
        input_file.copy(APWG_SOURCE_DIRECTORY)
        self.har_obj.run_harvester(None, resume_mode=False, use_source_base=False)
        json_list = self.urldb_cobj.list_urldb_dir()  # check if any json files are created or not
        assert len(json_list) == 1
        for json_path in json_list:
            assert self.urldb_cobj.exists_in_urldb_queue(str(json_path), 'APWG')  # check if file exists in urldb_queue
            assert self.urldb_cobj.is_source_for_file('APWG', json_path)  # checkif the source is correct

    def test_positive_defaults(self):
        """
        tests poisitve test case and default property values for json generation
        """
        input_file = self.base_data_path.joinpath('220-urls.txt')
        input_file.copy(APWG_SOURCE_DIRECTORY)
        self.har_obj.run_harvester(None, resume_mode=False, use_source_base=False)
        json_list = self.urldb_cobj.list_urldb_dir()  # check if any json files are created or not
        assert len(json_list) == 1
        for json_path in json_list:
            assert self.urldb_cobj.exists_in_urldb_queue(str(json_path), 'APWG')  # check if file exists in urldb_queue
            assert self.urldb_cobj.is_source_for_file('APWG', json_path)  # checkif the source is correct


    def test_json_metadata(self):
        """
        tests whether the metadata generated in the json is correct or not
        """
        input_file = self.base_data_path.joinpath('metadata-check.txt')
        print(str(input_file))
        input_file.copy(APWG_SOURCE_DIRECTORY)
        self.har_obj.run_harvester(None, resume_mode=False, use_source_base=False)
        json_list = self.urldb_cobj.list_urldb_dir()  # check if any json files are created or not
        assert len(json_list) == 1

        def check_name_value_pair(dict_obj, name, value):
            if dict_obj['name'] == name and dict_obj['value'] == value:
                return True
            else:
                return False

        for json_path in json_list:
            with json_path.open() as jsonp:
                data = json.load(jsonp)
                rawmd = data['urlEvents'][0]['rawMetadata']
                assert check_name_value_pair(rawmd[0], 'date_added', '2013-01-22 05:32:44')
                assert check_name_value_pair(rawmd[1], 'harvester_name', 'APWG')
                assert check_name_value_pair(rawmd[2], 'score', '50')
                assert check_name_value_pair(rawmd[3], 'target', 'EBAY')
                assert check_name_value_pair(rawmd[4], 'type', 'URL')
                assert check_name_value_pair(rawmd[5], 'url', 'http://miketest12letsmakeitdifferent.com/testpath')
                assert check_name_value_pair(rawmd[6], 'url_encoded', 'http%3A%2F%2Fmiketest2.com%2Ftestpath')

    def test_custom_priority(self):
        """
        Tests whether the custom priority in APWG.properties affects priority in urldb_queue or not
        """
        input_file = self.base_data_path.joinpath('positive-two-urls.txt')
        apwg_prop = prop_harvester(harvester_name='APWG', write_file_name=APWG_PROPERTY)
        apwg_prop['APWG.urldb.file.priority'] = '6500'
        apwg_prop.write_to_file(APWG_PROPERTY)
        input_file.copy(APWG_SOURCE_DIRECTORY)
        self.har_obj.run_harvester(None, resume_mode=False, use_source_base=False)
        json_list = self.urldb_cobj.list_urldb_dir()  # check if any json files are created or not
        assert len(json_list) == 1
        assert self.urldb_cobj.exists_in_urldb_queue(str(json_list[0]), 'APWG', priority=6500)

    def test_custom_destination(self):
        """
        tests whether custom destination in APWG.properties takes into effect or not
        """
        input_file = self.base_data_path.joinpath('positive-two-urls.txt')
        apwg_prop = prop_harvester(harvester_name='APWG', write_file_name=APWG_PROPERTY)
        urldb_dest = Path('/data/harvesters/urldb_auto')
        apwg_prop['APWG.urldb.file.destination'] = str(urldb_dest)
        apwg_prop.write_to_file(APWG_PROPERTY)
        self.urldb_cobj.clean_urldb_dir(dir=urldb_dest)
        input_file.copy(APWG_SOURCE_DIRECTORY)
        self.har_obj.run_harvester(None, resume_mode=False, use_source_base=False)
        json_list = self.urldb_cobj.list_urldb_dir(dir=urldb_dest)  # check if any json files are created or not
        assert len(json_list) == 1
        assert self.urldb_cobj.exists_in_urldb_queue(str(json_list[0]), 'APWG')

    def test_custom_filesize_limit(self):
        """
        test whether custom file size limit in APWG.properties takes effect
        """
        input_file = self.base_data_path.joinpath('ten-urls.txt')
        apwg_prop = prop_harvester(harvester_name='APWG', write_file_name=APWG_PROPERTY)
        apwg_prop['APWG.urldb.file.sizeLimit'] = '1'
        apwg_prop.write_to_file(APWG_PROPERTY)
        input_file.copy(APWG_SOURCE_DIRECTORY)
        self.har_obj.run_harvester(None, resume_mode=False, use_source_base=False)
        json_list = self.urldb_cobj.list_urldb_dir()  # check if any json files are created or not
        assert len(json_list) == 10
        assert self.urldb_cobj.exists_in_urldb_queue(str(json_list[0]), 'APWG')

    def test_invalid_param(self):
        """
        Jsons are not created when insufficient number of arguments are inserted per line in the source file.
        Also, when the number of arguments is fine but the sequence of parameters is not correct even then the jsons would not be created.
        """
        input_file = self.base_data_path.joinpath('urls-param.txt')
        input_file.copy(APWG_SOURCE_DIRECTORY)
        self.har_obj.run_harvester(None, resume_mode=False, use_source_base=False)
        json_list = self.urldb_cobj.list_urldb_dir()  # check if any json files are created or not
        assert len(json_list) == 0
        for json_path in json_list:
            assert self.urldb_cobj.exists_in_urldb_queue(str(json_path), 'APWG')  # check if file exists in urldb_queue
            assert self.urldb_cobj.is_source_for_file('APWG', json_path)  # checkif the source is correct

    def test_create_file_dest(self):
        """
        tests whether the jsons are written when given file destination does not exists
        """
        input_file = self.base_data_path.joinpath('positive-two-urls.txt')
        apwg_prop = prop_harvester(harvester_name='APWG', write_file_name=APWG_PROPERTY)
        urldb_dest = Path('/data/harvesters/urldb_non_existent')
        apwg_prop['APWG.urldb.file.destination'] = str(urldb_dest)
        apwg_prop.write_to_file(APWG_PROPERTY)
        if urldb_dest.exists():
            self.urldb_cobj.clean_urldb_dir(urldb_dest)
            urldb_dest.removedirs_p()
        input_file.copy(APWG_SOURCE_DIRECTORY)
        self.har_obj.run_harvester(None, resume_mode=False, use_source_base=False)
        json_list = self.urldb_cobj.list_urldb_dir(dir=urldb_dest)  # check if any json files are created or not
        assert len(json_list) == 1
        assert self.urldb_cobj.exists_in_urldb_queue(str(json_list[0]), 'APWG')
        urldb_dest.removedirs_p()

    def test_jsons_urldbqueue(self):
        """
        Test whether urls are being created in u2.urldb_queue table
        """
        input_file = self.base_data_path.joinpath('positive-two-urls.txt')
        input_file.copy(APWG_SOURCE_DIRECTORY)
        self.har_obj.run_harvester(None, resume_mode=False, use_source_base=False)
        json_list = self.urldb_cobj.list_urldb_dir()  # check if any json files are created or not
        assert len(json_list) == 1
        for json_path in json_list:
            assert self.urldb_cobj.exists_in_urldb_queue(str(json_path), 'APWG')  # check if file exists in urldb_queue
            assert self.urldb_cobj.is_source_for_file('APWG', json_path)  # checkif the source is correct
