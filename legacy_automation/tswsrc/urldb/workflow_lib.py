"""
==========================
Workflow Utility Functions
==========================
"""

__author__ = 'abhijeet'

import datetime
from path import Path
import runtime
from lib.db.mssql import TsMsSqlWrap
from libx.process import ShellExecutor
import logging

SECURITY_WORKFLOWS_QUEUE_TABLE = 'security_workflows_queue'


class Workflow:
    """
    Utility functions related  to Workflows
    """

    def __init__(self):
        self.r2_con = TsMsSqlWrap('R2')
        self.u2_con = TsMsSqlWrap('U2')

    def get_security_workflow_queue(self, sql):
        """
        gets the records in get_workflow_queue based on the
        :return: cursor for the result of the query
        """
        return self.r2_con.get_select_cursor(sql)

    def get_urldb_queue(self, sql):
        """
        gets the records in get_workflow_queue based on the
        :return: cursor for the result of the query
        """
        return self.u2_con.get_select_cursor(sql)

    def create_security_workflow_queue_record(self, task_name, task_value, workflow, priority=5000,
                                              queued_on=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                              pending=0):
        """
        create records in security workflow queue
        :param task_name: type of entity to be worked upon by
        :param task_value: the entity to be worked by the workflow
        :param workflow: workflow name
        :param priority: priority of the item in the queue
        :param queued_on: date when queued
        :param pending: pending = 0 means the item can be picked up by the workflow
        """
        sql = "insert into R2.dbo.%s values('%s', '%s', '%s', %s, '%s', %s)" % (SECURITY_WORKFLOWS_QUEUE_TABLE,
                                                                                task_name, task_value, workflow,
                                                                                priority, queued_on, pending)
        self.r2_con.execute_sql_commit(sql)

    def truncate_security_workflow_queue(self):
        """
        truncates the security workflow queue table
        """
        sql = 'truncate table %s' % SECURITY_WORKFLOWS_QUEUE_TABLE
        self.r2_con.execute_sql_commit(sql)


    def run_security_workflow(self, workflow_property=runtime.PROP.security_workflow):
       """
       runs security workflow based on the workflow property file
       :param workflow_property: path of workflow property as Path object
       """
       if not runtime.SH.security_workflow_agent.isfile():
        raise FileNotFoundError(runtime.SH.security_workflow_agent)
       if not workflow_property.isfile():
        raise FileNotFoundError(workflow_property)
       stdo, stde = ShellExecutor.run_wait_standalone('%s %s' % (runtime.SH.security_workflow_agent, workflow_property))
       return stdo,stde

