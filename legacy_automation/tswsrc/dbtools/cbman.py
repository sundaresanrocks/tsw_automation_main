"""
===================
CBMAN TESTS
===================
"""

from framework.test import SandboxedTest
from dbtools.agents import Agents
from framework.ddt import testdata_file, tsadriver
import runtime

@tsadriver
class CBMAN (SandboxedTest):
    testprefix = 'test'
    agent = 'cbman'

    @testdata_file(runtime.data_path + '/tsw/agents/cbman/help.txt')
    def test_cbman_help(self, search_list):
        """TS-1133:cbman help
        Help Options"""
        obj = Agents(self.agent)
        obj.tmpl_agent_stdout_check('-h', search_list)

    @testdata_file(runtime.data_path + '/tsw/agents/cbman/version.txt')
    def test_cbman_version(self, search_list):
        """TS-149:Check the version of cbman agent
        Vresion Check"""
        obj = Agents(self.agent)
        obj.tmpl_agent_stdout_check('-V', search_list)
    
    def test_cbman_default_log(self):
        """TS-1134:cbman run - default log
        Default log should get generated """
        obj = Agents(self.agent)
        args = ' -n 10 '
        obj.tmpl_agent_log(args, default_log=True, debug_log=False)

    def test_cbman_named_log(self):
        """ TS-1137:cbman run named log
        Default log should not get generated, named log should get generated """
        obj = Agents(self.agent)
        args = ' -n 10 '
        obj.tmpl_agent_log(args, default_log=False, debug_log=False)

    def test_cbman_debug_log(self):
        """TS-1135:cbman run - debug log enabled.
        Debug log should get generated """
        obj = Agents(self.agent)
        args = ' -D -n 10 '
        obj.tmpl_agent_log(args, default_log=True, debug_log=True)

    def test_cbman_without_debug_log(self):
        """TS-1136:cbman run without debug logging
        Debug log should not get generated """
        obj = Agents(self.agent)
        args = ' -n 10 '
        obj.tmpl_agent_log(args, default_log=True, debug_log=False)
 
    def test_cbman_is_running(self):
        """ TS-1138:cbman run isrunning
        During cbman run, is_running field in activeagents table should be 1. Also before and after the run,
         is_running field in activeagents table should be  0.  """
 
        obj = Agents(self.agent)
        args = ' -n 10 '

        obj.tmpl_is_running(args)

