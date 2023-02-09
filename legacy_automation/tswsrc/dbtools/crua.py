"""
===================
CRUA TESTS
===================
"""
import logging

import runtime
from framework.test import SandboxedTest
from dbtools.agents import Agents
from framework.ddt import testdata_file, tsadriver
from lib.sfimport import sfimport
from dbtools.agents import AgentsUtils
from lib.exceptions import ProcessingError, ValidationError, TestFailure
from lib.utils import db_reset
import os

@tsadriver
class CRUA (SandboxedTest):
    testprefix = 'test'
    agent = 'crua'

    @testdata_file(runtime.data_path + '/tsw/agents/crua/help.txt')
    def test_crua_help(self, search_list):
        """TS-1101:crua - help
        Help Options"""
        obj = Agents(self.agent)
        obj.tmpl_agent_stdout_check('-h', search_list)

    @testdata_file(runtime.data_path + '/tsw/agents/crua/version.txt')
    def test_crua_version(self, search_list):
        """TS-1102:crua - version
        Vresion Check"""
        obj = Agents(self.agent)
        obj.tmpl_agent_stdout_check('-V', search_list)
    
    def test_crua_default_log(self):
        """ TS-1130:crua run default log
        Default log should get generated """
        obj = Agents(self.agent)
        args = ' -n 10 '
        obj.tmpl_agent_log(args, default_log=True, debug_log=False)

    def test_crua_named_log(self):
        """TS-1125:crua run with shutdown_now check and number of items
        Default log should not get generated, named log should get generated """
        obj = Agents(self.agent)
        args = ' -n 10 '
        obj.tmpl_agent_log(args, default_log=False, debug_log=False)

    def test_crua_debug_log(self):
        """TS-1121:crua run default log
        Debug log should get generated """
        obj = Agents(self.agent)
        args = ' -D -n 10 '
        obj.tmpl_agent_log(args, default_log=True, debug_log=True)

    def test_crua_without_debug_log(self):
        """TS-1129:crua run without debug logging enabled .
        Debug log should not get generated """
        obj = Agents(self.agent)
        args = ' -n 10 '
        obj.tmpl_agent_log(args, default_log=True, debug_log=False)
 
 
    def test_crua_is_running(self):
        """ TS-1115:crua run isrunning
        During crua run, is_running field in activeagents table should be 1. Also before and after the run,  is_running field in activeagents table should be  0.  """
 
        obj = Agents(self.agent)
        args = ' -n 100 '

        obj.tmpl_is_running(args)



class CRUAFunc(SandboxedTest):

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


    def test_child_url_rep(self):

        """TS-631:CRUA : Changing a child url webrep that will affect the parent url &nbsp;web reputation."""

        
        ##New url
        test_domain = 'http://www.cruaauto4.com'
        test_url = 'http://www.cruaauto4.com/abc.html'
        autil_obj = AgentsUtils("*://CRUAAUTO4.COM","*://CRUAAUTO4.COM/abc.html")
        logging.info ("Running sfimport append category for domain")
        # Run sfimport on a new domain/url - append ms category
        sfobj = sfimport()
        bad_cat = "ms" #webrep - 127
 
        cat = "is" #webrep - 4
        
        sfimportResult = sfobj.append_category([test_domain],cat)
        

        #if ((sfimportResult["Total_Successful"] == 1) and 
        #    (sfimportResult["Total_Canon_Errors"] == 0) and 
        #    (sfimportResult["Total_Errors"] == 0) == False):

        #    raise ProcessingError('sfimport run not successful for url [%s]'%test_domain

        if ((sfimportResult["Total_Successful"] == 1) and 
            (sfimportResult["Total_Canon_Errors"] == 0) and 
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport append category not successful for url [%s]'%test_domain)
         
        #logging.info("Running sfimport append category for url")
       
                 
        sfimportResult = sfobj.append_category([test_url],cat)

        if ((sfimportResult["Total_Successful"] == 1) and 
            (sfimportResult["Total_Canon_Errors"] == 0) and 
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport run not successful for url [%s]'%test_url)

        #run wrua agent
        autil_obj.execute_wr_agent_workflow()

        webrep = autil_obj.webrep

        webrep1 = autil_obj.webrep1

        #if (webrep != -4):
        if webrep != 4 and webrep!=3:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching " 
                   "expected value [3 or 4]  !!" % (webrep,test_domain))
            raise TestFailure(msg)

        #if (webrep1 != -4):
        if webrep1 != 4 and webrep1 !=3:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching " 
                   "expected value [3 or 4]  !!" % (webrep1,test_url))

            
            raise TestFailure(msg)

        #Now crua test starts

        #change child url cat to ms

        logging.info("sfimport to modify parent url to ms")

        #sfimportResult = sfobj.modify([test_url],bad_cat)
        sfimportResult = sfobj.modify([test_domain],bad_cat)

        if ((sfimportResult["Total_Successful"] == 1) and 
            (sfimportResult["Total_Canon_Errors"] == 0) and 
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport run not successful for url [%s]'%test_url)

        #sfimport
        #wrua workflow

        #autil_obj = AgentsUtils("*://CRUAAUTO4.COM/abc.html")
        autil_obj = AgentsUtils("*://CRUAAUTO4.COM")

        autil_obj.execute_wr_agent_workflow()

        webrep = autil_obj.webrep

        #check of webrep for child url - 127
        if webrep != 127:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching " 
                   "expected value [127]  !!" % (webrep1,test_domain))

            #msg = ("Web repuation value [%d] of url/domain [%s] not matching expected value [16]  !!" % (webrep1,test_domain))
            raise TestFailure(msg)

        
        logging.info("running crua on parent")


        autil_obj = AgentsUtils("*://CRUAAUTO4.COM","","crua")
        #run crua
        autil_obj.execute_crua()
        webrep = autil_obj.webrep
        #check of webrep for parent url - it should be 127

        if webrep != 127:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching " 
                   "expected value [127]  !!" % (webrep,test_url))

            #msg = ("Web repuation value [%d] of url/domain [%s] not matching expected value [16]  !!" % (webrep1,test_domain))
            raise TestFailure(msg)




    def test_child_ipv4_rep(self):

        """TS-631:CRUA : Changing a child url webrep that will affect the parent url &nbsp;web reputation."""

        
        ##New url
        test_domain = 'http://77.77.75.76'
        test_url = 'http://77.77.75.76/abc.html'
        autil_obj = AgentsUtils("*://77.77.75.76","*://77.77.75.76/abc.html")
        logging.info ("Running sfimport append category for domain")
        # Run sfimport on a new domain/url - append ms category
        sfobj = sfimport()
        bad_cat = "ms" #webrep - 127
 
        cat = "is" #webrep - 4
        
        sfimportResult = sfobj.append_category([test_domain],cat)
        

        #if ((sfimportResult["Total_Successful"] == 1) and 
        #    (sfimportResult["Total_Canon_Errors"] == 0) and 
        #    (sfimportResult["Total_Errors"] == 0) == False):

        #    raise ProcessingError('sfimport run not successful for url [%s]'%test_domain

        if ((sfimportResult["Total_Successful"] == 1) and 
            (sfimportResult["Total_Canon_Errors"] == 0) and 
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport append category not successful for url [%s]'%test_domain)
         
        #logging.info("Running sfimport append category for url")
       
                 
        sfimportResult = sfobj.append_category([test_url],cat)

        
        
        if ((sfimportResult["Total_Successful"] == 1) and 
            (sfimportResult["Total_Canon_Errors"] == 0) and 
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport run not successful for url [%s]'%test_url)

        #run wrua agent
        autil_obj.execute_wr_agent_workflow()

        webrep = autil_obj.webrep

        webrep1 = autil_obj.webrep1

        #if (webrep != -4):
        if webrep != 4 and webrep!=3:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching " 
                   "expected value [3 or 4]  !!" % (webrep,test_domain))
            raise TestFailure(msg)

        #if (webrep1 != -4):
        if webrep1 != 4 and webrep1 !=3:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching " 
                   "expected value [3 or 4]  !!" % (webrep1,test_url))

            raise TestFailure(msg)

        #Now crua test starts

        #change child url cat to ms

        logging.info("sfimport to modify parent url to ms")

        #sfimportResult = sfobj.modify([test_url],bad_cat)
        sfimportResult = sfobj.modify([test_domain],bad_cat)

        if ((sfimportResult["Total_Successful"] == 1) and 
            (sfimportResult["Total_Canon_Errors"] == 0) and 
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport run not successful for url [%s]'%test_url)

        #sfimport
        #wrua workflow

        #autil_obj = AgentsUtils("*://CRUAAUTO4.COM/abc.html")
        autil_obj = AgentsUtils("*://77.77.75.76")

        autil_obj.execute_wr_agent_workflow()

        webrep = autil_obj.webrep

        #check of webrep for child url - 127
        if webrep != 127:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching " 
                   "expected value [127]  !!" % (webrep1,test_domain))

            #msg = ("Web repuation value [%d] of url/domain [%s] not matching expected value [16]  !!" % (webrep1,test_domain))
            raise TestFailure(msg)
        
        logging.info("running crua on parent")

        autil_obj = AgentsUtils("*://77.77.75.76","","crua")

        #run crua 
        autil_obj.execute_crua()

        webrep = autil_obj.webrep

        #check of webrep for parent url - it should be 127

        if webrep != 127:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching " 
                   "expected value [127]  !!" % (webrep,test_url))

            #msg = ("Web repuation value [%d] of url/domain [%s] not matching expected value [16]  !!" % (webrep1,test_domain))
            raise TestFailure(msg)

    def test_child_rep_check(self):

        """ TS-633:CRUA : Verify that CRUA Agent is Correctly calculating the Child_rep for newly inserted url through sfimport."""

        
        ##New url
        test_parent = 'http://www.cruaauto4.com'
        test_child = 'http://www.cruaauto4.com/abc.html'
        test_child2 = 'http://www.cruaauto4.com/def.html'
       
        autil_obj = AgentsUtils("*://CRUAAUTO4.COM")
        logging.info ("Running sfimport append category for domain")
        # Run sfimport on a new domain/url - append ms category
        sfobj = sfimport()

        cat = "is" #webrep - 4
        
        sfimportResult = sfobj.append_category([test_parent,test_child,test_child2],cat)

        if ((sfimportResult["Total_Successful"] == 1) and 
            (sfimportResult["Total_Canon_Errors"] == 0) and 
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport append category not successful for url [%s]'%test_parent)

        #run wrua agent
        autil_obj.execute_wr_agent_workflow()

        webrep = autil_obj.webrep

        #Check if parent url got the webreputation
        #if (webrep != -4):
        if webrep != 4 and webrep!=3:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching " 
                   "expected value [3 or 4]  !!" % (webrep,test_parent))
            raise TestFailure(msg)
        #Now crua run starts

        logging.info("running crua on parent")

        autil_obj = AgentsUtils("*://CRUAAUTO4.COM","","crua")

        #run crua 
        autil_obj.execute_crua()

        webrep = autil_obj.webrep
        child_webrep = autil_obj.child_webrep

        #check of webrep for parent url - it should be updated and should not be null

        if child_webrep is None or child_webrep == "":
            msg = ("Web repuation value of parent url [%s] not updated with " 
                   "child repuation value  !!" % test_parent)

            raise TestFailure(msg)





    def test_ipv4_child_rep_check(self):

        """	TS-634:CRUA : Verify that CRUA Agent is Correctly calculating the Child_rep for newly inserted IPV4 address through sfimport """

        
        ##New url
    
        test_parent = 'http://34.34.34.34'
        test_child = 'http://34.34.34.34/abc.html'
        test_child2 = 'http://34.34.34.34/def.html'
       
        autil_obj = AgentsUtils("*://34.34.34.34")
        logging.info ("Running sfimport append category for domain")
        # Run sfimport on a new domain/url - append ms category
        sfobj = sfimport()

        cat = "is" #webrep - 4
        
        sfimportResult = sfobj.append_category([test_parent,test_child,test_child2],cat)

        if ((sfimportResult["Total_Successful"] == 1) and 
            (sfimportResult["Total_Canon_Errors"] == 0) and 
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport append category not successful for url [%s]'%test_parent)

        #run wrua agent
        autil_obj.execute_wr_agent_workflow()

        webrep = autil_obj.webrep
        print(webrep)

        #Check if parent url got the webreputation
        #if (webrep != -4):
        if webrep != 4 and webrep!=3:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching " 
                   "expected value [3 or 4]  !!" % (webrep,test_parent))
            raise TestFailure(msg)

        #Now crua run starts
        
        logging.info("running crua on parent")
        autil_obj = AgentsUtils("*://34.34.34.34","","crua")

        #run crua 
        autil_obj.execute_crua()

        webrep = autil_obj.webrep
        child_webrep = autil_obj.child_webrep

        #check of webrep for parent url - it should be updated and should not be null
        print(child_webrep)
        if child_webrep is None or child_webrep == "":
            msg = ("Web repuation value of parent url [%s] not updated with " 
                   "child repuation value  !!" % test_parent)

           
            raise TestFailure(msg)


    def test_child_count_check(self):

        '''	'''

        test_parent = 'http://www.cruaauto5.com'
        test_child1 = 'http://www.cruaauto5.com/abc.html'
        test_child2 = 'http://www.cruaauto5.com/def.html'
        test_child3 = 'http://www.cruaauto5.com/xyz.html'

        autil_obj = AgentsUtils("*://CRUAAUTO5.COM")
        logging.info ("Running sfimport append category for domain")
        # Run sfimport on a new domain/url - append ms category
        sfobj = sfimport()

        cat = "is" #webrep - 4
        
        sfimportResult = sfobj.append_category([test_parent,test_child1,test_child2,test_child3],cat)

        if ((sfimportResult["Total_Successful"] == 4) and
            (sfimportResult["Total_Canon_Errors"] == 0) and
            (sfimportResult["Total_Errors"] == 0) == False):

            raise ProcessingError('sfimport append category not successful for url [%s]'%test_parent)

        #run wrua agent
        autil_obj.execute_wr_agent_workflow()

        webrep = autil_obj.webrep

        #Check if parent url got the webreputation
        
        if (webrep != 4 and webrep!=3 ):
            msg = ("Web repuation value [%d] of url/domain [%s] not matching "
                   "expected value [3 or 4]  !!" % (webrep,test_parent))
            raise TestFailure(msg)

        logging.info("running crua on parent")
        autil_obj = AgentsUtils("*://CRUAAUTO5.COM","","crua")

    #    #run crua 
        autil_obj.execute_crua()
        
        child_webrep = autil_obj.child_webrep

    #    #check of child webrep for parent url - it should be updated and should not be null

        if (child_webrep is None or child_webrep == "" ):
            msg = ("Web repuation value of parent url [%s] not updated with "
                   "child repuation value  !!" % (test_parent))
            raise TestFailure(msg)

        #run dman

        dman_obj = Agents("DMAN")

        args = ' -n 50'
        dman_obj.tmpl_agent_log(args, default_log=False, debug_log=False) #named plain

        lfile = os.path.abspath(dman_obj.output_file) # log

        # Verify dman log file for error msg if any
        sstr = "ERROR"

        with open(lfile) as fpr:
            if sstr in fpr.read():
                raise ValidationError('DMAN log file: %s' %lfile \
                   + ' has errors !!' )


