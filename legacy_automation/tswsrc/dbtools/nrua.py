"""
===================
NRUA TESTS
===================
"""
from framework.test import SandboxedTest
from dbtools.agents import Agents
from framework.ddt import testdata_file, tsadriver
import runtime


@tsadriver
class NRUA(SandboxedTest):
    testprefix = 'test'
    agent = 'nrua'
    @testdata_file(runtime.data_path + '/tsw/agents/nrua/help.txt')
    def test_help(self, search_list):
        """ TS-1093:NRUA: Help message
        Help Options"""
        obj = Agents(self.agent)
        obj.tmpl_agent_stdout_check('-h', search_list)

    @testdata_file(runtime.data_path + '/tsw/agents/nrua/version.txt')
    def test_version(self, search_list):
        """ TS-1092:NRUA: Version Check
        Vresion Check"""
        obj = Agents(self.agent)
        obj.tmpl_agent_stdout_check('-V', search_list)

    def test_nrua_is_running(self):
        """TS-1143:nrua run isrunning
        Check the activity table for is_running status before, after and When NRUA is running
        1. check status before (done automatically)
        2. check when WRUA is running
        3. check after WRUA completes
        4. verification
        """
        
        #1. check status before (done automatically)
        args = ' -n 10 '
        x = Agents(self.agent)

        #2. check when WRUA is running
        #3. check after WRUA completes
        #2 & 3 done by test_agent_run
        x.tmpl_is_running(args)
         
    def test_log_default_plain(self):
        """TS-1139:nrua run - default log
        test for default plain log """
        obj = Agents(self.agent)
        args = ' -n 2 '
        obj.tmpl_agent_log(args, default_log=True, debug_log=False)

    def test_log_default_debug(self):
        """TS-1140:nrua run - debug log enabled.
        test for default debug log """
        obj = Agents(self.agent)
        args = ' -n 2 -D '
        obj.tmpl_agent_log(args, default_log=True, debug_log=True)

    def test_log_named_plain(self):
        """TS-1141:nrua run named log
        test for named plain log """
        obj = Agents(self.agent)
        args = ' -n 2 '
        obj.tmpl_agent_log(args, default_log=False, debug_log=False)
        
    def test_log_named_debug(self):
        """ TS-1142:nrua run named log (with debugging enabled)
        test for named debug log """
        obj = Agents(self.agent)
        args = ' -n 2 -D '
        obj.tmpl_agent_log(args, default_log=False, debug_log=True)