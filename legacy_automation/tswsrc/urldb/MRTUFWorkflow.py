__author__ = 'sprihaba'

import unittest
import json
import runtime
from conf.files import PROP
from runtime import data_path
from conf.properties import set_prop_application
from conf.properties import prop_MRTUF_workflow
from urldb.workflow_lib import Workflow
from conf.files import DIR
from urldb.urldb_lib import URLDB
from path import Path

APPLICATION_PROPERTY=PROP.application
DEFAULT_SRCFILE_DEST = DIR.provider_sourceDirMRTUF
DEFAULT_WORKFILE_DEST = DIR.provider_workingDirMRTUF
DEFAULT_ARCFILE_DEST = DIR.provider_archiveDirMRTUF
DEFAULT_ERROR_DEST= DIR.provider_errorDirMRTUF

class MRTUFHarvesterWorkflow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Runs regex security workflow once for a group of testcases
        """
        set_prop_application()
        prop_MRTUF_workflow()
        global urldb_obj
        urldb_obj = URLDB()
        dir_list = DEFAULT_ARCFILE_DEST.listdir()
        for file_path in dir_list:
            print(file_path)
            if file_path == DEFAULT_ARCFILE_DEST + "/parsedFiles.txt":
                file_path.remove_p()
            else: continue
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


    def stage_input_files_to_srcdirectory(self,destfile,srcfile):
        """
        move input file to source directory
        """
        target_file = DEFAULT_SRCFILE_DEST.joinpath(destfile)
        srcfile.copyfile(target_file, follow_symlinks=False)
        workflow_obj = Workflow()
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.MRTUF_workflow)
        return stdo,stde

    def give_cleanslate(self):
        urldb_obj.clean_urldb_dir()
        urldb_obj.clean_urldb_queue_table()

    def setUp(self):
        super(MRTUFHarvesterWorkflow, self).setUp()
        self.workflow_cobj = Workflow()
        self.urldb_cobj = URLDB()

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

    def test_json_creation(self):
        """
        tests whether items are picked or not and jsons are created
        """
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/MRTUF/Hashes-1463129177.txt')
        self.stage_input_files_to_srcdirectory('Hashes-1463129177.txt',inputfile)
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 1
        for json_path in json_list:
            with json_path.open('r') as file:
                file_content = json.load(file)
                assert file_content['source'] == 'MRTUFHarvestWorkflow'

    def test_workflow_run(self):
        """
        tests whether workflow runs without any error
        """
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/MRTUF/Hashes-1462972278.txt')
        stdo=self.stage_input_files_to_srcdirectory('Hashes-1462972278.txt',inputfile)
        expected_string1 = 'Exception'
        expected_string2 = 'Error'
        assert (self.check_string_stdout(expected_string1,stdo)== False or self.check_string_stdout(expected_string2,stdo)== False)

    def test_filetopickup(self):
        set_prop_application()
        self.give_cleanslate()
        inputfile2= data_path.joinpath('urldb/MRTUF/hellotest.txt')
        self.stage_input_files_to_srcdirectory('hellotest.txt',inputfile2)
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 0

    def test_movetoworkingdir(self):
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/MRTUF/Hashes-1463424072.txt')
        stdo,stde=self.stage_input_files_to_srcdirectory('Hashes-1463424072.txt',inputfile)
        string='/data/webcache/workflows/harvesters/MRTUFHarvestWorkflow/source/Hashes-1463424072.txt'
        assert self.check_string_stdout(string,str(stdo))== True

    def test_checkerrordirectory(self):
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/MRTUF/Hashes-1463275873.txt')
        self.stage_input_files_to_srcdirectory('Hashes-1463275111.txt',inputfile)
        dir = Path(DEFAULT_ERROR_DEST)
        content = dir.listdir()
        assert len(content) == 0

    def test_specialchar_url(self):
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/MRTUF/Hashes-1463424111.txt')
        self.stage_input_files_to_srcdirectory('Hashes-1463424111.txt',inputfile)
        json_list = self.urldb_cobj.list_urldb_dir()
        urldb_obj.run_urldbqueue_agent()
        sql = "select * from U2.dbo.urldb_queue where source = 'MRTUFHarvestWorkflow' and pending=1"
        uq_cursor = self.urldb_cobj.get_urldb_queue_records(sql)
        uq_records = [record for record in uq_cursor]
        assert (len(json_list) == 1 and len(uq_records) == 0)

    def test_insert_private_ip(self):
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/MRTUF/Hashes-1463275222.txt')
        stdo=self.stage_input_files_to_srcdirectory('Hashes-1463275222.txt',inputfile)
        oueputlog= str(stdo)
        expected_string = 'URL is a private IP'
        assert self.check_string_stdout(expected_string,oueputlog)== True


    def test_invalidU2DB(self):
        self.give_cleanslate()
        ap_obj=set_prop_application()
        ap_obj['mssql.u2.host']='invaliddb.wsrlab'
        ap_obj.write_to_file(APPLICATION_PROPERTY)
        inputfile= data_path.joinpath('urldb/MRTUF/Hashes-1463275222.txt')
        stdo1=self.stage_input_files_to_srcdirectory('Hashes-1463275222.txt',inputfile)
        inputstream="".join(stdo1)
        expected_string1 = 'Exception'
        expected_string2 = 'Error'
        assert (self.check_string_stdout(expected_string1,inputstream)== True or self.check_string_stdout(expected_string2,inputstream)== True)











