__author__ = 'sprihaba'

import unittest
import json
import runtime
from conf.files import PROP
from runtime import data_path
from conf.properties import set_prop_application
from conf.properties import prop_QihooHarvestWorkflow_workflow
from urldb.workflow_lib import Workflow
from conf.files import DIR
from urldb.urldb_lib import URLDB
from lib.db.mssql import TsMsSqlWrap

APPLICATION_PROPERTY=PROP.application
DEFAULT_SRCFILE_DEST = DIR.provider_sourceDirQihooHarvestWorkflow
DEFAULT_WORKFILE_DEST = DIR.provider_workingDirQihooHarvestWorkflow
DEFAULT_ARCFILE_DEST = DIR.provider_archiveDirQihooHarvestWorkflow
DEFAULT_ERROR_DEST= DIR.provider_errorDirQihooHarvestWorkflow

class Qihoo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Runs regex security workflow once for a group of testcases
        """

        set_prop_application()
        prop_QihooHarvestWorkflow_workflow()
        if not DEFAULT_SRCFILE_DEST.exists():
               DEFAULT_SRCFILE_DEST.makedirs()
        else:
            dir_list = DEFAULT_SRCFILE_DEST.listdir()
            for file_path in dir_list:
                if file_path.isfile():
                    file_path.remove_p()
                elif file_path.isdir():
                    file_path.rmtree_p()

        if not DEFAULT_WORKFILE_DEST.exists():
               DEFAULT_WORKFILE_DEST.makedirs()
        else:
            dir_list = DEFAULT_WORKFILE_DEST.listdir()
            for file_path in dir_list:
                if file_path.isfile():
                    file_path.remove_p()
                elif file_path.isdir():
                    file_path.rmtree_p()

        if not DEFAULT_ARCFILE_DEST.exists():
               DEFAULT_ARCFILE_DEST.makedirs()
        else:
            dir_list = DEFAULT_ARCFILE_DEST.listdir()
            for file_path in dir_list:
                if file_path.isfile():
                    file_path.remove_p()
                elif file_path.isdir():
                    file_path.rmtree_p()

        if not DEFAULT_ERROR_DEST.exists():
               DEFAULT_ERROR_DEST.makedirs()
        else:
            dir_list = DEFAULT_ERROR_DEST.listdir()
            for file_path in dir_list:
                if file_path.isfile():
                    file_path.remove_p()
                elif file_path.isdir():
                    file_path.rmtree_p()

        global urldb_obj
        urldb_obj = URLDB()
        dir_list = DEFAULT_ARCFILE_DEST.listdir()
        for file_path in dir_list:
            if file_path == DEFAULT_ARCFILE_DEST + "/parsedFiles.txt":
                file_path.remove_p()
            else: continue



    def stage_input_files_to_srcdirectory(self,destfile,srcfile):
        """
        move input file to source directory
        """
        target_file = DEFAULT_SRCFILE_DEST.joinpath(destfile)
        srcfile.copyfile(target_file, follow_symlinks=False)
        workflow_obj = Workflow()
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.QihooHarvestWorkflow)
        return stdo,stde

    def setUp(self):
        super(Qihoo, self).setUp()
        self.workflow_cobj = Workflow()
        self.urldb_cobj = URLDB()
        self.u2_con = TsMsSqlWrap('U2')
        self.u2_con.execute_sql_commit("update u2.dbo.url_shorteners set is_redirect = 1 where url_shortener = 'bit.ly'")

    def check_string_stdout(self,string,output):
        """
        checks the string in shell output
        :param string:
        :param output:
        :return:
        """
        if string in output:
            return True
        else:
            return False

    def give_cleanslate(self):
        urldb_obj.clean_urldb_dir()
        urldb_obj.clean_urldb_queue_table()

    def test_json_creation(self):
        """
        tests whether items are picked or not and jsons are created
        """
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Qihoo/Qihoo_1111.txt')
        self.stage_input_files_to_srcdirectory('Qihoo_1111.txt',inputfile)
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 1
        for json_path in json_list:
            with json_path.open('r') as file:
                file_content = json.load(file)
                assert file_content['source'] == 'QihooHarvestWorkflow'

    def test_specialchar_url(self):
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Qihoo/Qihoo_2222.txt')
        self.stage_input_files_to_srcdirectory('Qihoo_2222.txt',inputfile)
        json_list = self.urldb_cobj.list_urldb_dir()
        urldb_obj.run_urldbqueue_agent()
        sql = "select * from U2.dbo.urldb_queue where source = 'QihooHarvestWorkflow' and pending=1"
        uq_cursor = self.urldb_cobj.get_urldb_queue_records(sql)
        uq_records = [record for record in uq_cursor]
        assert (len(json_list) == 1 and len(uq_records) == 0)

    def test_insert_private_ip(self):
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Qihoo/Qihoo_0000.txt')
        self.stage_input_files_to_srcdirectory('Qihoo_0000.txt',inputfile)
        stdo=self.urldb_cobj.run_urldbqueue_agent()
        oueputlog= str(stdo)
        expected_string = 'URL is a private IP'
        assert self.check_string_stdout(expected_string,oueputlog)== True

    def test_shortened_urls(self):
        """
        tests whether workflow runs without any error
        """
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Qihoo/Qihoo_3333.txt')
        stdo1=self.stage_input_files_to_srcdirectory('Qihoo_3333.txt',inputfile)
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 1
        expected_string1 = 'ExpandedUrl'
        expected_string2 = 'redirectUrl'
        inputstream="".join(stdo1)
        assert (self.check_string_stdout(expected_string1,inputstream)== True or self.check_string_stdout(expected_string2,inputstream)== True)

    def test_invalidU2DB(self):
        self.give_cleanslate()
        ap_obj=set_prop_application()
        ap_obj['mssql.u2.host']='invaliddb.wsrlab'
        ap_obj.write_to_file(APPLICATION_PROPERTY)
        inputfile= data_path.joinpath('urldb/Qihoo/Qihoo_3333.txt')
        stdo1=self.stage_input_files_to_srcdirectory('Qihoo_3111.txt',inputfile)
        inputstream="".join(stdo1)
        expected_string1 = 'Exception'
        expected_string2 = 'Error'
        assert (self.check_string_stdout(expected_string1,inputstream)== True or self.check_string_stdout(expected_string2,inputstream)== True)


    def test_data_persist_URLDB(self):
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Qihoo/Qihoo_4444.txt')
        self.stage_input_files_to_srcdirectory('Qihoo_4444.txt',inputfile)
        stdo=self.urldb_cobj.run_urldbqueue_agent()
        url_dict = self.urldb_cobj.url_coll_get_url('HTTPS://VIRUSTOTAL.COM/url/4a349cfb5e4f654cf2109542fe9005d2bb50b292250a9ec2fe502232a62d1552/analysis/1481407012')
        assert((url_dict is None)==False)






