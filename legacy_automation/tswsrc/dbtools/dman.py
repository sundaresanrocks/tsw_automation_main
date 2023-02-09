import logging

from framework.test import SandboxedTest
from dbtools.agents import Agents
from lib.exceptions import ValidationError
from lib.db.mssql import TsMsSqlWrap
from framework.ddt import testdata_file, tsadriver
import runtime



@tsadriver
class DMAN (SandboxedTest):
    testprefix = 'test'
    agent = 'dman'
    @testdata_file (runtime.data_path + '/tsw/agents/dman/help.txt')
    def test_dman_help(self, search_list):
        """ TS-1358:DMAN: Help option
        """
        obj = Agents(self.agent)
        obj.tmpl_agent_stdout_check('-h', search_list)


    @testdata_file(runtime.data_path + '/tsw/agents/dman/version.txt')
    def test_dman_version(self, search_list):
        """ TS-1359:DMAN: Version check
        """
        obj = Agents(self.agent)
        obj.tmpl_agent_stdout_check('-V', search_list)

    def test_log_default_plain(self):
        """ TS-1360:Run DMAN run - default log
        test for default plain log
        """
        obj = Agents(self.agent)
        args = ' -n 2 '
        obj.tmpl_agent_log(args, default_log=True, debug_log=False)

    def test_log_default_debug(self):
        """	 TS-1361:run DMAN - debug log enabled.
        test for default debug log
        """
        obj = Agents(self.agent)
        args = ' -n 2 -D '
        obj.tmpl_agent_log(args, default_log=True, debug_log=True)

    def test_log_named_plain(self):
        """  TS-1362:runDMAN with named log
        test for named plain log
        """
        obj = Agents(self.agent)
        args = ' -n 2 '
        obj.tmpl_agent_log(args, default_log=False, debug_log=False)
        
    def test_log_named_debug(self):
        """  TS-1363:Run DMAN with named log (with debugging enabled)
        test for named debug log
        """
        obj = Agents(self.agent)
        args = ' -n 2 -D '
        obj.tmpl_agent_log(args, default_log=False, debug_log=True)
  
    def test_is_running(self):
        """   TS-1364:DMAN is_ running flag check
        Check the activity table for is_running status before, after and When DMAN is running
        1. check status before (done automatically)
        2. check when DMAN is running
        3. check after DMAN completes
        4. verification
        """
        args = ' -n 10 '
        x = Agents(self.agent)
        x.tmpl_is_running(args)

