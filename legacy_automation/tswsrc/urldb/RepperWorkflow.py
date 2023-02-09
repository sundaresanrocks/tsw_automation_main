__author__ = 'sprihaba'

import unittest
import json
import runtime
from conf.files import PROP
from runtime import data_path
from conf.properties import set_prop_application
from conf.properties import prop_RepperHarvest_workflow
from urldb.workflow_lib import Workflow
from conf.files import DIR
from urldb.urldb_lib import URLDB

APPLICATION_PROPERTY=PROP.application
DEFAULT_SRCFILE_DEST = DIR.provider_sourceDirRepper
DEFAULT_WORKFILE_DEST = DIR.provider_workingDirRepper
DEFAULT_ARCFILE_DEST = DIR.provider_archiveDirRepper
DEFAULT_ERROR_DEST= DIR.provider_errorDirRepper

class RepperHarvesterWorkflow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Runs regex security workflow once for a group of testcases
        """
        set_prop_application()
        prop_RepperHarvest_workflow()
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
        print('hello')
        target_file = DEFAULT_SRCFILE_DEST.joinpath(destfile)
        print(target_file)
        srcfile.copyfile(target_file, follow_symlinks=False)
        workflow_obj = Workflow()
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.RepperHarvestWorkflow)
        return stdo,stde

    def setUp(self):
        super(RepperHarvesterWorkflow, self).setUp()
        self.workflow_cobj = Workflow()
        self.urldb_cobj = URLDB()

    def give_cleanslate(self):
        urldb_obj.clean_urldb_dir()
        urldb_obj.clean_urldb_queue_table()

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
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Repper/repper_rule_processing_20161110_213009.txt')
        self.stage_input_files_to_srcdirectory('repper_rule_processing_20161110_213009.txt',inputfile)
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 1
        for json_path in json_list:
            with json_path.open('r') as file:
                file_content = json.load(file)
                assert file_content['source'] == 'RepperHarvestWorkflow'

    def test_source_regex(self):
        """
        test matching source regex
        """
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Repper/repper_processing_20161110_213009.txt')
        stdo=self.stage_input_files_to_srcdirectory('repper_processing_20161110_213009.txt',inputfile)
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 0

    def test_workflow_run(self):
        """
        tests whether workflow runs without any error
        """
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Repper/repper_rule_processing_20161110_213010.txt')
        stdo=self.stage_input_files_to_srcdirectory('repper_rule_processing_20161110_213010.txt',inputfile)
        expected_string1 = 'Exception'
        expected_string2 = 'Error'
        assert (self.check_string_stdout(expected_string1,stdo)== False or self.check_string_stdout(expected_string2,stdo)== False)


    def test_json_queue(self):
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Repper/repper_rule_processing_20161110_213011.txt')
        self.stage_input_files_to_srcdirectory('repper_rule_processing_20161110_213011.txt',inputfile)
        sql = "select * from u2.dbo.urldb_queue (nolock) where source='RepperHarvestWorkflow' and pending = 0"
        scursor = self.workflow_cobj.get_urldb_queue(sql)
        srecs = [rec for rec in scursor]
        assert len(srecs) != 0

    def test_movetoarchivedir(self):
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Repper/repper_rule_processing_20161110_213012.txt')
        stdo,stde=self.stage_input_files_to_srcdirectory('repper_rule_processing_20161110_213012.txt',inputfile)
        string='values to /data/webcache/workflows/harvesters/RepperHarvestWorkflow/archive/parsedFiles.txt'
        assert self.check_string_stdout(string,str(stdo))== True

    def test_insert_private_ip(self):
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Repper/repper_rule_processing_20161110_213013.txt')
        stdo,stde=self.stage_input_files_to_srcdirectory('repper_rule_processing_20161110_213013.txt',inputfile)
        inputstream="".join(stdo)
        expected_string = 'URL is a private IP'
        assert self.check_string_stdout(expected_string,inputstream)== True












