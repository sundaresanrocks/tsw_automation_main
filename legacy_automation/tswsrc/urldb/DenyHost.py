__author__ = 'sprihaba'

import unittest
import runtime
from conf.files import PROP
from runtime import data_path
from conf.properties import set_prop_application
from conf.properties import prop_DenyHostHarvestWorkflow_workflow
from urldb.workflow_lib import Workflow
from conf.files import DIR
from urldb.urldb_lib import URLDB
from lib.db.mssql import TsMsSqlWrap

APPLICATION_PROPERTY=PROP.application
DEFAULT_SRCFILE_DEST = DIR.provider_sourceDirDenyHost
DEFAULT_WORKFILE_DEST = DIR.provider_workingDirDenyHost
DEFAULT_ARCFILE_DEST = DIR.provider_archiveDirDenyHost
DEFAULT_ERROR_DEST= DIR.provider_errorDirDenyHost

class DenyHostHarvesterWorkflow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Runs regex security workflow once for a group of testcases
        """

        set_prop_application()
        prop_DenyHostHarvestWorkflow_workflow()
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

        sql=""

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
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.DenyHost)
        return stdo,stde

    def setUp(self):
        super(DenyHostHarvesterWorkflow, self).setUp()
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
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/DenyHost/DenyhostsHarvestWorkflow_1482174843.txt')
        self.stage_input_files_to_srcdirectory('DenyhostsHarvestWorkflow_1482174843.txt',inputfile)
        json_list = self.urldb_cobj.list_urldb_dir()
        urldb_obj.run_urldbqueue_agent()
        sql = "select * from U2.dbo.urldb_queue where source = 'DenyhostsHarvestWorkflow' and pending=1"
        uq_cursor = self.urldb_cobj.get_urldb_queue_records(sql)
        uq_records = [record for record in uq_cursor]
        assert (len(json_list) == 1 and len(uq_records) == 0)

    def test_shortened_urls(self):
        """
        tests whether workflow runs without any error
        """
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/DenyHost/DenyhostsHarvestWorkflow_1482174811.txt')
        stdo1=self.stage_input_files_to_srcdirectory('DenyhostsHarvestWorkflow_1482174811.txt',inputfile)
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 1
        stdo2=urldb_obj.run_urldbqueue_agent()
        string3="".join(stdo2)
        expected_string1 = 'Exception'
        expected_string2 = 'Error'
        expected_string3 = 'ExpandedUrl'
        assert (self.check_string_stdout(expected_string3,string3)== True)
        assert (self.check_string_stdout(expected_string1,stdo1)== False | self.check_string_stdout(expected_string2,stdo1)== False)

    def test_specialchar_url(self):
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/DenyHost/DenyhostsHarvestWorkflow_1482174822.txt')
        self.stage_input_files_to_srcdirectory('DenyhostsHarvestWorkflow_1482174822.txt',inputfile)
        json_list = self.urldb_cobj.list_urldb_dir()
        urldb_obj.run_urldbqueue_agent()
        sql = "select * from U2.dbo.urldb_queue where source = 'DenyhostsHarvestWorkflow' and pending=1"
        uq_cursor = self.urldb_cobj.get_urldb_queue_records(sql)
        uq_records = [record for record in uq_cursor]
        assert (len(json_list) == 1 and len(uq_records) == 0)

    def test_insert_private_ip(self):
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/DenyHost/DenyhostsHarvestWorkflow_1482174800.txt')
        self.stage_input_files_to_srcdirectory('DenyhostsHarvestWorkflow_1482174800.txt',inputfile)
        stdo=self.urldb_cobj.run_urldbqueue_agent()
        oueputlog= str(stdo)
        expected_string = 'URL is a private IP'
        assert self.check_string_stdout(expected_string,oueputlog)== True














