__author__ = 'sprihaba'

import unittest
import json
import runtime

from conf.files import PROP
from runtime import data_path
from conf.properties import set_prop_application
from conf.properties import prop_securityworkflow_VirusTotal
from urldb.workflow_lib import Workflow
from conf.files import DIR
from urldb.urldb_lib import URLDB
from path import Path

APPLICATION_PROPERTY=PROP.application
DEFAULT_SOURCE_DEST = DIR.provider_sourceDirVirus
DEFAULT_ARCFILE_DEST = DIR.provider_archiveDirVirus
DEFAULT_ERROR_DEST= DIR.provider_errorDirVirus
DEFAULT_WORKFILE_DEST=DIR.provider_workingDirCleanMxVirus

class VirusTotalworkflow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Runs regex security workflow once for a group of testcases
        """

        set_prop_application()
        prop_securityworkflow_VirusTotal()
        global urldb_obj, stdo, stde
        urldb_obj = URLDB()
        dir_list = DEFAULT_ARCFILE_DEST.listdir()
        for file_path in dir_list:
            if file_path == DEFAULT_ARCFILE_DEST + "/parsedFiles.txt":
                file_path.remove_p()
            else: continue
        if not DEFAULT_WORKFILE_DEST.exists():
               DEFAULT_WORKFILE_DEST.makedirs()
        else:
            dir_list = DEFAULT_WORKFILE_DEST.listdir()
            for file_path in dir_list:
                if file_path.isfile():
                    file_path.remove_p()
                elif file_path.isdir():
                    file_path.rmtree_p()

        if not DEFAULT_SOURCE_DEST.exists():
               DEFAULT_SOURCE_DEST.makedirs()
        else:
            dir_list = DEFAULT_SOURCE_DEST.listdir()
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
        target_file = DEFAULT_SOURCE_DEST.joinpath(destfile)
        srcfile.copyfile(target_file, follow_symlinks=False)
        workflow_obj = Workflow()
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.virustotal_workflow)
        return stdo,stde

    def setUp(self):
        super(VirusTotalworkflow, self).setUp()
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
        inputfile= data_path.joinpath('urldb/VirusTotal/filtered-url-20160803T0700.txt')
        self.stage_input_files_to_srcdirectory('filtered-url-20160803T0700.txt',inputfile)
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 1
        for json_path in json_list:
            with json_path.open('r') as file:
                file_content = json.load(file)
                assert file_content['source'] == 'VirusTotalWorkflow'

    def test_workflow_run(self):
        """
        tests whether workflow runs without any error
        """
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/VirusTotal/filtered-url-20160803T0700.txt')
        stdo=self.stage_input_files_to_srcdirectory('filtered-url-20160803T0701.txt',inputfile)
        inputstream="".join(stdo)
        expected_string1 = 'Exception'
        expected_string2 = 'Error'
        assert (self.check_string_stdout(expected_string1,inputstream)== False or self.check_string_stdout(expected_string2,inputstream)== False)


    def test_json_queue(self):
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/VirusTotal/filtered-url-20160803T0700.txt')
        self.stage_input_files_to_srcdirectory('filtered-url-20160803T0702.txt',inputfile)
        sql = "select * from u2.dbo.urldb_queue (nolock) where source='VirusTotalWorkflow' and pending = 0"
        scursor = self.workflow_cobj.get_urldb_queue(sql)
        srecs = [rec for rec in scursor]
        assert len(srecs) != 0

    def test_checkerrordirectory(self):
        self.give_cleanslate()
        dir = Path(DEFAULT_ERROR_DEST)
        content = dir.listdir()
        assert len(content) == 0

    def test_archivedir(self):
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/VirusTotal/filtered-url-20160803T0700.txt')
        self.stage_input_files_to_srcdirectory('filtered-url-20160803T0703.txt',inputfile)
        Workingdir = Path(DEFAULT_WORKFILE_DEST)
        workingcontent = Workingdir.listdir()
        archivecontent =Path(DEFAULT_ARCFILE_DEST)
        assert (len(workingcontent) == 0 and len(archivecontent) != 0)


    



