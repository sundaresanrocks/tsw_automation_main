# coding=utf-8
"""
======================================
workflows mechanism test cases
======================================
"""

__author__ = 'abhijeet'

import json
import unittest
from conf.properties import prop_security_workflow
from conf.properties import set_prop_application
from conf.files import LOG
from conf.files import DIR
from conf.files import PROP
from urldb.workflow_lib import Workflow
from urldb.urldb_lib import URLDB
import logging


AGENTS_LOG =  LOG.agents
DEFAULT_FILE_DEST = DIR.urldb_json_dir
WORKFLOW_PROPERTY = PROP.security_workflow


class TestSecurityWorkflowMechRun1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Runs security workflow once for a group of testcases
        """
        prop_security_workflow()
        set_prop_application()
        if AGENTS_LOG.exists():
            AGENTS_LOG.remove()
        urldb_obj = URLDB()
        urldb_obj.clean_urldb_dir()
        workflow_obj = Workflow()
        workflow_obj.truncate_security_workflow_queue()
        if not DEFAULT_FILE_DEST.exists():
            DEFAULT_FILE_DEST.makedirs()

        workflow_obj.create_security_workflow_queue_record('url', 'https://google.com', 'AutoSecurityWorkflow')
        workflow_obj.create_security_workflow_queue_record('url', 'https://goorgle.com', 'AutoSecurityWorkflowTwo')
        workflow_obj.create_security_workflow_queue_record('url', 'https://googlee.com', 'AutoSecurityWorkflow',
                                                           pending=1)
        stdo,stde = workflow_obj.run_security_workflow(WORKFLOW_PROPERTY)
        logging.info(stdo)

    def setUp(self):
        super(TestSecurityWorkflowMechRun1, self).setUp()
        self.workflow_cobj = Workflow()
        self.urldb_cobj = URLDB()

    def test_positive(self):
        """
        tests whether items are picked or not and jsons are created
        """
        sql = "select * from R2.dbo.security_workflows_queue where workflow = 'AutoSecurityWorkflow' and pending = 0"
        scursor = self.workflow_cobj.get_security_workflow_queue(sql)
        srecs = [rec for rec in scursor]
        assert len(srecs) == 0
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 1
        for json_path in json_list:
            with json_path.open('r') as file:
                file_content = json.load(file)
                assert file_content['source'] == 'AutoSecurityWorkflow'

    def test_workflow_verification(self):
        """
        tests whether the workflow picks only its own tasks or not
        """
        sql = "select * from R2.dbo.security_workflows_queue where workflow = 'AutoSecurityWorkflow' and pending = 0"
        scursor = self.workflow_cobj.get_security_workflow_queue(sql)
        srecs = [rec for rec in scursor]
        assert len(srecs) == 0
        sql2 = "select * from R2.dbo.security_workflows_queue where workflow = 'AutoSecurityWorkflowTwo' and pending " \
               "= 0"
        scursor2 = self.workflow_cobj.get_security_workflow_queue(sql2)
        srecs2 = [rec for rec in scursor2]
        assert len(srecs2) == 1

    def test_pending_verification(self):
        """
        verifies that already pending records are not consumed
        """
        sql = "select * from R2.dbo.security_workflows_queue where workflow = 'AutoSecurityWorkflow' and pending = 0"
        scursor = self.workflow_cobj.get_security_workflow_queue(sql)
        srecs = [rec for rec in scursor]
        assert len(srecs) == 0
        sql2 = "select * from R2.dbo.security_workflows_queue where workflow = 'AutoSecurityWorkflow' and pending = 1"
        scursor2 = self.workflow_cobj.get_security_workflow_queue(sql2)
        srecs2 = [rec for rec in scursor2]
        assert len(srecs2) == 1
        assert srecs2[0]['task_value'] == 'https://googlee.com'

    def test_json_creation(self):
        """
        tests whether jsons are created
        """
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 1
        for json_path in json_list:
            with json_path.open('r') as file:
                file_content = json.load(file)
                assert file_content['source'] == 'AutoSecurityWorkflow'


class TestSecurityWorkflowMechRun2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        sw_prop = prop_security_workflow()
        del sw_prop['agent.sendToUrlDB']
        sw_prop.write_to_file(WORKFLOW_PROPERTY)
        if AGENTS_LOG.exists():
            AGENTS_LOG.remove()
        urldb_obj = URLDB()
        urldb_obj.clean_urldb_dir()
        workflow_obj = Workflow()
        workflow_obj.truncate_security_workflow_queue()
        if not DEFAULT_FILE_DEST.exists():
            DEFAULT_FILE_DEST.makedirs()

        workflow_obj.create_security_workflow_queue_record('url', 'https://google.com', 'AutoSecurityWorkflow')
        workflow_obj.create_security_workflow_queue_record('url', 'https://goorgle.com', 'AutoSecurityWorkflow')

        stdo,stde = workflow_obj.run_security_workflow(WORKFLOW_PROPERTY)
        logging.info(stdo)

    def setUp(self):
        super(TestSecurityWorkflowMechRun2, self).setUp()
        self.workflow_cobj = Workflow()
        self.urldb_cobj = URLDB()

    def test_no_sendtoUrldb(self):
        """
        tests that jsons are not created when sendtoUrldb is not provided
        """
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 0


class TestSecurityWorkflowMechRun3(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        sw_prop = prop_security_workflow()
        sw_prop['agent.sendToUrlDB']= 'false'
        sw_prop.write_to_file(WORKFLOW_PROPERTY)
        if AGENTS_LOG.exists():
            AGENTS_LOG.remove()
        urldb_obj = URLDB()
        urldb_obj.clean_urldb_dir()
        workflow_obj = Workflow()
        workflow_obj.truncate_security_workflow_queue()
        if not DEFAULT_FILE_DEST.exists():
            DEFAULT_FILE_DEST.makedirs()

        workflow_obj.create_security_workflow_queue_record('url', 'https://google.com', 'AutoSecurityWorkflow')
        workflow_obj.create_security_workflow_queue_record('url', 'https://goorgle.com','AutoSecurityWorkflow')

        workflow_obj.run_security_workflow(WORKFLOW_PROPERTY)


    def setUp(self):
        super(TestSecurityWorkflowMechRun3, self).setUp()
        self.workflow_cobj = Workflow()
        self.urldb_cobj = URLDB()

    def test_false_sendtoUrldb(self):
        """
        tests that jsons are not created when sendtoUrldb is false
        """
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 0

class TestSecurityWorkflowMechRun4(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        sw_prop = prop_security_workflow()
        sw_prop['agent.sendToUrlDB']= 'true'
        sw_prop.write_to_file(WORKFLOW_PROPERTY)
        if AGENTS_LOG.exists():
            AGENTS_LOG.remove()
        urldb_obj = URLDB()
        urldb_obj.clean_urldb_dir()
        workflow_obj = Workflow()
        workflow_obj.truncate_security_workflow_queue()
        if not DEFAULT_FILE_DEST.exists():
            DEFAULT_FILE_DEST.makedirs()
        workflow_obj.create_security_workflow_queue_record('url', 'https://google.com', 'AutoSecurityWorkflow')
        #workflow_obj.create_security_workflow_queue_record('url', 'https://goorgle.com', 'AutoSecurityWorkflow')
        workflow_obj.run_security_workflow(WORKFLOW_PROPERTY)


    def setUp(self):
        super(TestSecurityWorkflowMechRun4, self).setUp()
        self.workflow_cobj = Workflow()
        self.urldb_cobj = URLDB()

    def test_true_sendtoUrldb(self):
        """
        tests that jsons are created when sendtoUrldb is true
        """
        json_list = self.urldb_cobj.list_urldb_dir()
        assert len(json_list) == 1


