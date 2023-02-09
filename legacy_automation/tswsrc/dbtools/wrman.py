"""
===================
WRMAN TESTS
===================
"""

import logging

#from tsa.common import logger as logging
from framework.test import SandboxedTest
from lib.exceptions import TestFailure
from dbtools.agents import Agents
from lib.exceptions import ProcessingError
from framework.ddt import testdata_file, tsadriver
from dbtools.agents import AgentsUtils
from libx.vm import get_snapshot_wrapper
import runtime
from lib.sfimport import sfimport
from lib.utils import db_reset

@tsadriver
class WRMAN (SandboxedTest):
    testprefix = 'test'
    agent = 'wrman'

    @testdata_file(runtime.data_path + '/tsw/agents/wrman/help.txt')
    def test_wrman_help(self, search_list):
        """TS-1132:wrman help
        Help Options"""
        obj = Agents(self.agent)
        obj.tmpl_agent_stdout_check('-h', search_list)

    @testdata_file(runtime.data_path + '/tsw/agents/wrman/version.txt')
    def test_wrman_version(self, search_list):
        """TS-102:WRMAN:Check the version of wrman agent
        Vresion Check"""
        obj = Agents(self.agent)
        obj.tmpl_agent_stdout_check('-V', search_list)
        
    def test_wrman_default_log(self):
        """TS-1144:wrman run - default log
        Default log should get generated """
        obj = Agents(self.agent)
        args = ' -n 10 '
        obj.tmpl_agent_log(args, default_log=True, debug_log=False)

    def test_wrman_named_log(self):
        """ TS-1147:wrman run named log
        Default log should not get generated, named log should get generated """
        obj = Agents(self.agent)
        args = ' -n 10 '
        obj.tmpl_agent_log(args, default_log=False, debug_log=False)

    def test_wrman_debug_log(self):
        """TS-1145:wrman run - debug log enabled.
        Debug log should get generated """
        obj = Agents(self.agent)
        args = ' -D -n 10 '
        obj.tmpl_agent_log(args, default_log=True, debug_log=True)

    def test_wrman_without_debug_log(self):
        """TS-1146:wrman run without debug logging
        Debug log should not get generated """
        obj = Agents(self.agent)
        args = ' -n 10 '
        obj.tmpl_agent_log(args, default_log=True, debug_log=False)
 
 
    def test_wrman_is_running(self):
        """ TS-1148:wrman run isrunning
        During wrman run, is_running field in activeagents table should be 1. Also before and after the run,  is_running field in activeagents table should be  0.  """
 
        obj = Agents(self.agent)
        args = ' -n 10 '

        obj.tmpl_is_running(args)
 

class WRMANFunc(SandboxedTest):

    """

    """

    @classmethod
    def setUpClass(cls):
        ##   Revert the VM image of minimal DB (MS SQL DB)
        db_reset.db_reset()

        pass

    def setUp(self):
        """
        """
        SandboxedTest.setUp(self)
        
        
    def tearDown(self):
        """
        """
        SandboxedTest.tearDown(self)
    

    def test_mod_webrep(self):

        """TS-106:WRMAN:Check the effect of webreputation change in child URLs. """

       
        test_url = 'http://www.wrmanautotest103tail.com'
        autil_obj = AgentsUtils("*://WRMANAUTOTEST103TAIL.COM","*://WRMANAUTOTEST103TAIL.COM/abc.html")

        child = 'http://www.wrmanautotest103tail.com/abc.html'

        logging.info ("Running sfimport append category")
        # Run sfimport on a new url & child - append hw category
        sfobj = sfimport()
        cat = "hw" #safe category
        new_cat = "ms" #or ph #bad category


        #parent url
        sfimportResult = sfobj.append_category([test_url],cat)
        
        if ((sfimportResult["Total_Successful"] == 1) and 
            (sfimportResult["Total_Canon_Errors"] == 0) and 
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport append category not successful for url [%s]'%test_url) 

        #child url
        sfimportResult = sfobj.append_category([child],cat)
        
        if ((sfimportResult["Total_Successful"] == 1) and 
            (sfimportResult["Total_Canon_Errors"] == 0) and 
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport append category not successful for url [%s]'%child) 


        #Run wrua workflow (tman+wrua)

        #Post this,WebReputation is updated
         
        autil_obj.execute_wr_agent_workflow()

        #Modify parent url to ms cat

        sfimportResult = sfobj.modify([test_url],new_cat)

        if ((sfimportResult["Total_Successful"] == 1) and 
            (sfimportResult["Total_Canon_Errors"] == 0) and 
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport update category successful for url [%s]'%test_url)

        #Run wrua workflow (tman+wrua)
        

        autil_obj.execute_wr_agent_workflow()
        webrep= autil_obj.webrep
        webrep1= autil_obj.webrep1
        logging.info("After wrua run, parent url webrep is [%s]"%webrep)
        logging.info("After wrua run, child webrep is [%s]"%webrep1)


        if webrep != 127:
            msg = ("Pre wrman check: Web repuation value [%d] of url/domain [%s] not matching " 
                  "expected value [127]  !!" % (webrep,test_url))
            raise TestFailure(msg)

        #if (webrep1 != -4):
        #    msg = ("Pre wrman check: Web repuation value [%d] of url/domain [%s] not matching " 
        #          "expected value [-4]  !!" % (webrep1,child))
        #    raise TestFailure(msg)

        autil_obj = AgentsUtils("*://WRMANAUTOTEST103TAIL.COM/abc.html")
        autil_obj.execute_wrman()
      

        #Run wrman (new function in agent_lib)
        webrep= autil_obj.webrep
        logging.info("After wrman run, child webrep is [%s]"%webrep)
      
        #After wrman run, 
        #child url should have web reputation of 127 (corresponding to category - ms)
        if webrep != 127:
            msg = ("Post wrman check: Web repuation value [%d] of url/domain [%s] not matching " 
                  "expected value [127]  !!" % (webrep,test_url))
            raise TestFailure(msg)



    def test_ip_mod_webrep(self):

        """TS-1402: WRMAN:Check the effect of webreputation change in child ipv4 urls. """

       
        test_url = 'http://172.2.3.34'
        autil_obj = AgentsUtils("*://172.2.3.34","*://172.2.3.34/abc.html")

        child = 'http://172.2.3.34/abc.html'

        logging.info ("Running sfimport append category")
        # Run sfimport on a new url & child - append hw category
        sfobj = sfimport()
        cat = "hw" #safe category
        new_cat = "ms" #or ph #bad category


        #parent url
        sfimportResult = sfobj.append_category([test_url],cat)
        
        if ((sfimportResult["Total_Successful"] == 1) and 
            (sfimportResult["Total_Canon_Errors"] == 0) and 
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport append category not successful for url [%s]'%test_url) 

        #child url
        sfimportResult = sfobj.append_category([child],cat)
        
        if ((sfimportResult["Total_Successful"] == 1) and 
            (sfimportResult["Total_Canon_Errors"] == 0) and 
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport append category not successful for url [%s]'%child) 


        #Run wrua workflow (tman+wrua)
        #Post this,WebReputation is updated
         
        autil_obj.execute_wr_agent_workflow()

        #Modify parent url to ms cat

        sfimportResult = sfobj.modify([test_url],new_cat)

        if ((sfimportResult["Total_Successful"] == 1) and 
            (sfimportResult["Total_Canon_Errors"] == 0) and 
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport update category successful for url [%s]'%test_url)

        #Run wrua workflow (tman+wrua)
        

        autil_obj.execute_wr_agent_workflow()
        webrep= autil_obj.webrep
        webrep1= autil_obj.webrep1
        logging.info("After wrua run, parent url webrep is [%s]"%webrep)
        logging.info("After wrua run, child webrep is [%s]"%webrep1)


        if webrep != 127:
            msg = ("Pre wrman check: Web repuation value [%d] of url/domain [%s] not matching " 
                  "expected value [127]  !!" % (webrep,test_url))
            raise TestFailure(msg)

        #if (webrep1 != -4):
        #    msg = ("Pre wrman check: Web repuation value [%d] of url/domain [%s] not matching " 
        #          "expected value [-4]  !!" % (webrep1,child))
        #    raise TestFailure(msg)

        autil_obj = AgentsUtils("*://172.2.3.34/abc.html")
        autil_obj.execute_wrman()
      

        #Run wrman (new function in agent_lib)
        webrep= autil_obj.webrep
        logging.info("After wrman run, child webrep is [%s]"%webrep)
      
        #After wrman run, 
        #child url should have web reputation of 127 (corresponding to category - ms)
        if webrep != 127:
            msg = ("Post wrman check: Web repuation value [%d] of url/domain [%s] not matching " 
                  "expected value [127]  !!" % (webrep,test_url))
            raise TestFailure(msg)
