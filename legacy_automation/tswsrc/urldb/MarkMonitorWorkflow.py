__author__ = 'sprihaba'

import unittest
import json
import runtime
from conf.files import PROP
from runtime import data_path
from conf.properties import set_prop_application
from conf.properties import prop_markmonitor_workflow
from urldb.workflow_lib import Workflow
from conf.files import DIR
from urldb.urldb_lib import URLDB
from path import Path

APPLICATION_PROPERTY=PROP.application
DEFAULT_SRCFILE_DEST = DIR.provider_sourceDirMarkMonitor
DEFAULT_WORKFILE_DEST = DIR.provider_workingDirMarkMonitor
DEFAULT_ARCFILE_DEST = DIR.provider_archiveDirMarkMonitor
DEFAULT_ERROR_DEST= DIR.provider_errorDirMarkMonitor

class MarkMonitorHarvesterWorkflow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Runs regex security workflow once for a group of testcases
        """
        set_prop_application()
        prop_markmonitor_workflow()
        global urldb_obj
        urldb_obj = URLDB()
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
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.markmonitor_workflow)
        return stdo,stde

    def setUp(self):
        super(MarkMonitorHarvesterWorkflow, self).setUp()
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
        inputfile= data_path.joinpath('urldb/workflow_markmonitor/2_newfile.txt')
        self.stage_input_files_to_srcdirectory('2_jsoncreation.txt',inputfile)
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 1
        for json_path in json_list:
            with json_path.open('r') as file:
                file_content = json.load(file)
                assert file_content['source'] == 'MarkMonitorWorkflow'

    def test_workflow_run(self):
        """
        tests whether workflow runs without any error
        """
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/workflow_markmonitor/2_newfile.txt')
        stdo=self.stage_input_files_to_srcdirectory('2_logchck.txt',inputfile)
        expected_string1 = 'Exception'
        expected_string2 = 'Error'
        assert (self.check_string_stdout(expected_string1,stdo)== False | self.check_string_stdout(expected_string2,stdo)== False)


    def test_json_queue(self):
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/workflow_markmonitor/2_testqueue.txt')
        self.stage_input_files_to_srcdirectory('2_queuecheck.txt',inputfile)
        sql = "select * from u2.dbo.urldb_queue (nolock) where source='MarkMonitorWorkflow' and pending = 0"
        scursor = self.workflow_cobj.get_urldb_queue(sql)
        srecs = [rec for rec in scursor]
        assert len(srecs) != 0

    def test_filetopickup(self):
        self.give_cleanslate()
        inputfile2= data_path.joinpath('urldb/workflow_markmonitor/2_newfile.txt')
        self.stage_input_files_to_srcdirectory('filemrkmnonitor.txt',inputfile2)
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 0

    def test_checkerrordirectory(self):
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/workflow_markmonitor/2_testqueue.txt')
        self.stage_input_files_to_srcdirectory('2_checkerrdir.txt',inputfile)
        dir = Path(DEFAULT_ERROR_DEST)
        content = dir.listdir()
        assert len(content) == 0

    def test_specialchar_url(self):
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/workflow_markmonitor/2_specialchar.txt')
        self.stage_input_files_to_srcdirectory('2_specialchar.txt',inputfile)
        json_list = self.urldb_cobj.list_urldb_dir()
        urldb_obj.run_urldbqueue_agent()
        sql = "select * from U2.dbo.urldb_queue where source = 'MarkMonitorWorkflow' and pending=1"
        uq_cursor = self.urldb_cobj.get_urldb_queue_records(sql)
        uq_records = [record for record in uq_cursor]
        assert (len(json_list) == 1 and len(uq_records) == 0)

    def test_insert_private_ip(self):
        urldb_obj.clean_urldb_dir()
        inputfile= data_path.joinpath('urldb/workflow_markmonitor/2_privateIP.txt')
        self.stage_input_files_to_srcdirectory('2_privateIP.txt',inputfile)
        stdo=self.urldb_cobj.run_urldbqueue_agent()
        oueputlog= str(stdo)
        expected_string = 'URL is a private IP'
        assert self.check_string_stdout(expected_string,oueputlog)== True

    def test_data_persist_URLDB(self):
        set_prop_application()
        self.give_cleanslate()
        inputfile= data_path.joinpath('urldb/workflow_markmonitor/2_datainmongo.txt')
        self.stage_input_files_to_srcdirectory('2_datainmongo.txt',inputfile)
        stdo=self.urldb_cobj.run_urldbqueue_agent()
        url_dict = self.urldb_cobj.url_coll_get_url('*://DATA123.COM?path1.html')
        assert((url_dict is None)==False)











