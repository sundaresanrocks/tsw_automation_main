__author__ = 'sprihaba'

import unittest
import json
import runtime
from conf.files import PROP
from runtime import data_path
from conf.properties import set_prop_application
from conf.properties import prop_BitDefender_workflow
from urldb.workflow_lib import Workflow
from conf.files import DIR
from urldb.urldb_lib import URLDB


APPLICATION_PROPERTY=PROP.application
DEFAULT_SRCFILE_DEST = DIR.provider_sourceDirBitDefender
DEFAULT_WORKFILE_DEST = DIR.provider_workingDirBitDefender
DEFAULT_ARCFILE_DEST = DIR.provider_archiveDirBitDefender
DEFAULT_ERROR_DEST= DIR.provider_errorDirBitDefender

class BitDefender(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Runs regex security workflow once for a group of testcases
        """

        set_prop_application()
        prop_BitDefender_workflow()
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
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.BitDefenderHarvestWorkflow)
        return stdo,stde

    def setUp(self):
        super(BitDefender, self).setUp()
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

    def give_cleanslate(self):
        urldb_obj.clean_urldb_dir()
        urldb_obj.clean_urldb_queue_table()


    def test_json_creation(self):
        """
        tests whether items are picked or not and jsons are created
        """
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Bitdefender/url_2013_08_25.txt.20130825220045')
        self.stage_input_files_to_srcdirectory('url_2013_08_25.txt.20130825220045',inputfile)
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 1
        for json_path in json_list:
            with json_path.open('r') as file:
                file_content = json.load(file)
                assert file_content['source'] == 'BitDefenderHarvestWorkflow'

    def test_json_queue(self):
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Bitdefender/url_2013_08_24.txt.20130824220505')
        self.stage_input_files_to_srcdirectory('url_2013_08_24.txt.20130824220505',inputfile)
        sql = "select * from u2.dbo.urldb_queue (nolock) where source='BitDefenderHarvestWorkflow' and pending = 0"
        scursor = self.workflow_cobj.get_urldb_queue(sql)
        srecs = [rec for rec in scursor]
        assert len(srecs) != 0

    def test_movetoarchivedir(self):
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Bitdefender/url_2013_02_15.txt.20130215221105')
        stdo,stde=self.stage_input_files_to_srcdirectory('url_2013_02_15.txt.20130215221105',inputfile)
        string='Moving /data/webcache/workflows/harvesters/BitDefenderHarvestWorkflow/working/url_2013_02_15.txt.20130215221105 to /data/webcache/workflows/harvesters/BitDefenderHarvestWorkflow/archive'
        assert self.check_string_stdout(string,str(stdo))== True

    def test_workflow_run(self):
        """
        tests whether items are picked or not and jsons are created
        """
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Bitdefender/url_2013_03_08.txt.20130311105940')
        stdo=self.stage_input_files_to_srcdirectory('url_2013_03_08.txt.20130311105940',inputfile)
        inputstream="".join(stdo)
        expected_string1 = 'Exception'
        expected_string2 = 'Error'
        assert (self.check_string_stdout(expected_string1,inputstream)== False or self.check_string_stdout(expected_string2,inputstream)== False)

    def test_data_persist_URLDB(self):
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/Bitdefender/url_2013_02_09.txt.20130209221459')
        self.stage_input_files_to_srcdirectory('url_2013_02_09.txt.20130209221459',inputfile)
        stdo=self.urldb_cobj.run_urldbqueue_agent()
        url_dict = self.urldb_cobj.url_coll_get_url('*://ARMINPFLUEGL.AR.FUNPIC.DE/adv/getfile.php')
        assert((url_dict is None)==False)

