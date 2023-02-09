"""
===================
Wrua TestCases
===================
"""
import logging
from lib.exceptions import TestFailure, ProcessingError
from framework.test import SandboxedTest
from dbtools.agents import Agents
from framework.ddt import testdata_file, tsadriver
from lib.sfimport import sfimport
from dbtools.agents import AgentsUtils
from lib.db.mssql import TsMsSqlWrap
from lib.utils import db_reset

from libx.vm import get_snapshot_wrapper
import runtime


@tsadriver
class WRUA(SandboxedTest):
    agent = "WRUA"

    def test_wrua_is_running(self):  # Verified

        """TS-1131:wrua run isrunning
        Check the activity table for is_running status before, after and When WRUA is running
        1. check status before (done automatically)
        2. check when WRUA is running
        3. check after WRUA completes
        4. verification
        """

        # 1. check status before (done automatically)
        args = ' -n 10 '
        x = Agents(self.agent)

        #2. check when WRUA is running
        #3. check after WRUA completes
        #2 & 3 done by test_agent_run
        x.tmpl_is_running(args)

    @testdata_file('../res/tsw/agents/wrua/help.txt')
    def test_wrua_help(self, search_list):
        """TS-1096:wrua help
        tcid-
        Help Options
        """
        obj = Agents(self.agent)
        obj.tmpl_agent_stdout_check('-h', search_list)


    @testdata_file('../res/tsw/agents/wrua/version.txt')
    def test_wrua_version(self, search_list):
        """TS-216:WRUA:Version Check
         tcid-
         Version Check
        """
        obj = Agents(self.agent)
        obj.tmpl_agent_stdout_check('-V', search_list)


    def test_log_default_plain(self):
        """TS-1098:Default Plain Log
        test for default plain log """
        obj = Agents(self.agent)
        args = ' -n 2 '
        obj.tmpl_agent_log(args, default_log=True, debug_log=False)

    def test_log_default_debug(self):
        """TS-1097:wrua run - debug log enabled.
        test for default debug log """
        obj = Agents(self.agent)
        args = ' -n 2 -D '
        obj.tmpl_agent_log(args, default_log=True, debug_log=True)

    def test_log_named_plain(self):
        """TS-1099:wrua run named log
        test for named plain log """
        obj = Agents(self.agent)
        args = ' -n 2 '
        obj.tmpl_agent_log(args, default_log=False, debug_log=False)

    def test_log_named_debug(self):
        """TS-1100:wrua run named log (with debugging enabled)
        test for named debug log """
        obj = Agents(self.agent)
        args = ' -n 2 -D '
        obj.tmpl_agent_log(args, default_log=False, debug_log=True)




@tsadriver
class WRUAFunc(SandboxedTest):
    """

    """
    agent = "WRUA"

    @classmethod
    def setUpClass(cls):
        db_reset.db_reset()

    def setUp(self):
        """
        """
        SandboxedTest.setUp(self)


    def tearDown(self):
        """
        """
        SandboxedTest.tearDown(self)

    @testdata_file(runtime.data_path + '/tsw/agents/wrua/url_list.txt')
    def test_processed_urls(self, search_list):
        url = search_list
        urls = [url]
        sfobj = sfimport()
        u2_obj = TsMsSqlWrap('U2')
        d2_obj = TsMsSqlWrap('D2')
        cat = "ms"
        for individual_url in urls:
            sfobj.append_category(individual_url, cat)
        url_dict = sfobj.url_dict()

        for key in list(url_dict.keys()):
            logging.warning(key)
            update_query = "update u2.dbo.queue set priority = 99999 where url_id=" + key
            u2_obj.execute_sql_commit(update_query)
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -n 10 -D",output_file='tman_out.txt')

        obj = Agents(self.agent)
        obj.run_agent(agent_args="-n 5 -D", output_file='out.txt')

        query = "select * from d2.dbo.wrqueue where agent_name = 'WRUA'"
        count = d2_obj.get_row_count(query)
        print(count)
        if count != 4:
            msg = ("WRUA did not processed for desired number of urls")
            raise TestFailure(msg)


    def test_new_domain(self):
        # Web reputation calculation for a new domain

        test_url = 'http://www.wruanewdom231new.com'
        autil_obj = AgentsUtils("*://WRUANEWDOM231NEW.COM")
        logging.info("Running sfimport append category")
        # Run sfimport on a new domain/url - append ms category
        sfobj = sfimport()
        cat = "ms"
        sfimportResult = sfobj.append_category([test_url], cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport run not successful for url [%s]' % test_url)

        #run wrua agent
        autil_obj.execute_wr_agent_workflow()
        webrep = autil_obj.webrep

        if webrep != 127:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching "
                   "expected value [127]  !!" % (webrep, test_url))
            raise TestFailure(msg)

    def test_existing_domain(self):

        """TS-218:WRUA:Change in web reputation score of an existing domain """

        test_url = 'http://www.wruaauto16.com'
        autil_obj = AgentsUtils("*://WRUAAUTO16.COM")

        # Check if the domain is new
        ##autil_obj.execute_wrua_workflowurl_exists = autil_obj.url_exists_in_db()

        logging.info("Running sfimport append category")
        # Run sfimport on a new domain/url - append ph category
        sfobj = sfimport()
        cat = "ph"
        new_cat = "is"
        sfimportResult = sfobj.append_category([test_url], cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport append category not successful for url [%s]' % test_url)

        #Run wrua workflow, so that new url/domain gets updated 

        autil_obj.execute_wr_agent_workflow()

        # Run sfimport on a existing domain/url - append ms category

        sfimportResult = sfobj.modify([test_url], new_cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport update category successful for url [%s]' % test_url)

        #run wrua agent
        autil_obj.execute_wr_agent_workflow()
        webrep = autil_obj.webrep

        if webrep != 3:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching "
                   "expected value [3]  !!" % (webrep, test_url))
            raise TestFailure(msg)


    def test_new_ipv4(self):

        """TS-219:WRUA:Add a new ipv4 IP address for calculating web Reputation Score """

        test_url = 'http://75.75.75.75'
        autil_obj = AgentsUtils("*://75.75.75.75")

        #Check if the domain is new
        #autil_obj.execute_wrua_workflowurl_exists = autil_obj.url_exists_in_db()

        logging.info("Running sfimport append category")
        # Run sfimport on a new domain/url - append ms category
        sfobj = sfimport()
        cat = "ms"
        sfimportResult = sfobj.append_category([test_url], cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport append category not successful for url [%s]' % test_url)

        #run wrua agent
        autil_obj.execute_wr_agent_workflow()
        webrep = autil_obj.webrep

        if webrep != 127:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching "
                   "expected value [127]  !!" % (webrep, test_url))
            raise TestFailure(msg)


    def test_existing_ipv4(self):

        """TS-220:WRUA:Change in web reputation score of a existing IPv4 Address. """

        test_url = 'http://75.75.75.76'
        autil_obj = AgentsUtils("*://75.75.75.76")

        # Check if the domain is new
        #autil_obj.execute_wrua_workflowurl_exists = autil_obj.url_exists_in_db()

        logging.info("Running sfimport append category")
        # Run sfimport on a new domain/url - append sa category
        sfobj = sfimport()
        cat = "is"
        new_cat = "ms"
        sfimportResult = sfobj.append_category([test_url], cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport append category not successful for url [%s]' % test_url)

        #Run wrua workflow, so that new url/domain gets updated 

        autil_obj.execute_wrua_workflowurl_ewebrep1 = autil_obj.execute_wr_agent_workflow()

        #sfimportResult = sfobj.update_category([test_url],new_cat)
        sfimportResult = sfobj.modify([test_url], new_cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport update category successful for url [%s]' % test_url)

        #run wrua agent
        autil_obj.execute_wr_agent_workflow()
        webrep = autil_obj.webrep

        if webrep != 127:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching "
                   "expected value [127]  !!" % (webrep, test_url))
            raise TestFailure(msg)


    def test_new_ipv6(self):

        """TS-221:WRUA:Add a new ipv6 IP address for calculating web Reputation Score."""


        # test_url = 'http://[2001:cdba::3257:9652]'
        #test_url = 'http://[3ffe:2a00:100:7031::1]'
        test_url = 'http://[3FFE:2A00:100:7031:0:0:0:1]'
        autil_obj = AgentsUtils("*://[3FFE:2A00:100:7031:0:0:0:1]")

        #Check if the domain is new
        #autil_obj.execute_wrua_workflowurl_exists = autil_obj.url_exists_in_db()

        logging.info("Running sfimport append category")
        # Run sfimport on a new domain/url - append ms category
        sfobj = sfimport()
        cat = "ms"
        sfimportResult = sfobj.append_category([test_url], cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport append category not successful for url [%s]' % test_url)

        #run wrua agent
        autil_obj.execute_wr_agent_workflow()
        webrep = autil_obj.webrep

        if webrep != 127:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching "
                   "expected value [127]  !!" % (webrep, test_url))
            raise TestFailure(msg)

    def test_existing_ipv6(self):

        """ TS-222:WRUA:Change in web reputation score of a existing IPv6 Address. """

        test_url = 'http://[1080:0:0:0:8:800:200C:417A]/index.html'
        autil_obj = AgentsUtils("*://[1080:0:0:0:8:800:200C:417A]/index.html")

        # Check if the domain is new
        #autil_obj.execute_wrua_workflowurl_exists = autil_obj.url_exists_in_db()

        logging.info("Running sfimport append category")
        # Run sfimport on a new domain/url - append sa category
        sfobj = sfimport()
        cat = "ph"
        new_cat = "ms"
        sfimportResult = sfobj.append_category([test_url], cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport append category not successful for url [%s]' % test_url)

        #Run wrua workflow, so that new url/domain gets updated 

        autil_obj.execute_wr_agent_workflow()

        #sfimportResult = sfobj.update_category([test_url],new_cat)
        sfimportResult = sfobj.modify([test_url], new_cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport update category successful for url [%s]' % test_url)

        #run wrua agent
        autil_obj.execute_wr_agent_workflow()
        webrep = autil_obj.webrep

        if webrep != 127:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching "
                   "expected value [127]  !!" % (webrep, test_url))
            raise TestFailure(msg)


    def test_new_url_with_path(self):

        """TS-223:WRUA:Add a new URL (path level ) """
        test_url = 'http://www.wruaauto19new.com/abc.html'
        autil_obj = AgentsUtils("*://WRUAAUTO19NEW.COM/ABC.HTML")

        # Check if the domain is new
        #autil_obj.execute_wrua_workflowurl_exists = autil_obj.url_exists_in_db()

        logging.info("Running sfimport append category")
        # Run sfimport on a new domain/url - append ms category
        sfobj = sfimport()
        cat = "ms"
        sfimportResult = sfobj.append_category([test_url], cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport run not successful for url [%s]' % test_url)

        #run wrua agent
        autil_obj.execute_wr_agent_workflow()
        webrep = autil_obj.webrep

        if webrep != 127:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching "
                   "expected value [127]  !!" % (webrep, test_url))
            raise TestFailure(msg)


    def test_new_url_existing_domain(self):

        """ TS-224:WRUA:Add a new URL for existing domain """

        test_url = 'http://www.wruaauto17.com'
        autil_obj = AgentsUtils("*://WRUAAUTO17.COM")

        # Check if the domain is new
        #autil_obj.execute_wrua_workflowurl_exists = autil_obj.url_exists_in_db()

        logging.info("Running sfimport append category")
        # Run sfimport on a new domain/url - append sa category
        sfobj = sfimport()
        cat = "ph"
        new_cat = "ms"
        sfimportResult = sfobj.append_category([test_url], cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport append category not successful for url [%s]' % test_url)

        #Run wrua workflow, so that new url/domain gets updated 

        autil_obj.execute_wr_agent_workflow()

        # new url - same domain

        test_url = 'http://www.wruaauto17.com/abcd.html'
        autil_obj = AgentsUtils("*://WRUAAUTO17.COM/abcd.html")

        #sfimportResult = sfobj.update_category([test_url],new_cat)
        sfimportResult = sfobj.modify([test_url], new_cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport update category successful for url [%s]' % test_url)

        #run wrua agent
        autil_obj.execute_wr_agent_workflow()
        webrep = autil_obj.webrep

        if webrep != 127:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching "
                   "expected value [127]  !!" % (webrep, test_url))
            raise TestFailure(msg)


    def test_new_url_domain(self):

        """TS-225:Verify a new domain and it's URL is rated differernt reputation score
        at the same time (Assign different categories to main domains and it's URL """


        # #New url
        test_domain = 'http://www.wruaauto17.com'
        test_url = 'http://www.wruaauto17.com/abc.html'
        autil_obj = AgentsUtils("*://WRUAAUTO17.COM", "*://WRUAAUTO17.COM/abc.html")

        #Check if the domain is new
        ##autil_obj.execute_wrua_workflowurl_exists = autil_obj.url_exists_in_db()

        logging.info("Running sfimport append category for domain")
        # Run sfimport on a new domain/url - append ms category
        sfobj = sfimport()
        domain_cat = "ms"  #webrep - 127
        #cat = "bl" #webrep - 16
        cat = "is"  #webrep - 4

        sfimportResult = sfobj.append_category([test_domain], domain_cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport run not successful for url [%s]' % test_domain)


        ##New Domain


        #autil_obj = AgentsUtils("*://WRUAAUTO17.COM")

        #Check if the domain is new
        ##autil_obj.execute_wrua_workflowurl_exists = autil_obj.url_exists_in_db()

        logging.info("Running sfimport append category for url")
        # Run sfimport on a new domain/url - append ms category
        #sfobj = sfimport()

        sfimportResult = sfobj.append_category([test_url], cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport run not successful for url [%s]' % test_url)




        #run wrua agent
        autil_obj.execute_wr_agent_workflow()

        webrep = autil_obj.webrep

        webrep1 = autil_obj.webrep1

        if webrep != 127:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching "
                   "expected value [127]  !!" % (webrep, test_domain))
            raise TestFailure(msg)

        #Query 

        logging.info("webrep1 - %d" % (webrep1,))
        logging.info("test_domain - %s" % (test_domain,))

        #Clarification by Scott 
        #Based on the algorithm for web reputation calculation. A children URL, such as test_url can never have a better web reputation than its parent, test_domain.
        #So, I would expect both test_url and test_domain to a 127 webrep.

        # if (webrep1 != 4):
        if webrep1 != 127:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching "
                   "expected value [127]  !!" % (webrep1, test_url))

            #msg = ("Web repuation value [%d] of url/domain [%s] not matching expected value [16]  !!" % (webrep1,test_domain))
            raise TestFailure(msg)


    def test_two_urls_and_domain(self):

        """TS-226: WRUA: two different urls of same domain is categorised differently """


        # #Two urls

        test_url1 = 'http://www.wruaauto18.com/abc.html'
        test_url2 = 'http://www.wruaauto18.com/def.html'
        test_domain = 'http://www.wruaauto18.com'


        cat1 = "is"  #webrep - 5
        cat2 = "ph"  #webrep - 127
        #domain_cat = "se" #webrep - 5 (to be confirmed)
        domain_cat = "bl"  #webrep - 10
        logging.info("Running sfimport append category for url1")
        # Run sfimport on a new domain/url - append is category
        sfobj = sfimport()

        sfimportResult = sfobj.append_category([test_url1], cat1)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport run not successful for url [%s]' % test_url1)


        ##url2
        logging.info("Running sfimport append category for url")
        # Run sfimport on a new domain/url - append ms category
        #sfobj = sfimport()

        sfimportResult = sfobj.append_category([test_url2], cat2)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport run not successful for url [%s]' % test_url2)


        #run wrua agent
        autil_obj = AgentsUtils("*://WRUAAUTO18.COM/abc.html", "*://WRUAAUTO18.COM/def.html")
        autil_obj.execute_wr_agent_workflow()

        webrep = autil_obj.webrep

        webrep1 = autil_obj.webrep1

        #Verify webrep of two urls


        if webrep != 4:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching "
                   "expected value [4]  !!" % (webrep, test_url1))
            raise TestFailure(msg)

        #Query 



        if webrep1 != 127:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching "
                   "expected value [127]  !!" % (webrep1, test_url2))
            raise TestFailure(msg)


        #Run sfimport on domain & wrua workflow 

        sfimportResult = sfobj.append_category([test_domain], domain_cat)

        if ((sfimportResult["Total_Successful"] == 1) and
                (sfimportResult["Total_Canon_Errors"] == 0) and
                    (sfimportResult["Total_Errors"] == 0) == False):
            raise ProcessingError('sfimport run not successful for url [%s]' % test_domain)

        autil_obj2 = AgentsUtils("*://WRUAAUTO18.COM")


        #run wrua agent
        autil_obj2.execute_wr_agent_workflow()

        webrep = autil_obj.webrep

        #if (webrep != 16):
        if webrep != 4:
            msg = ("Web repuation value [%d] of url/domain [%s] not matching "
                   "expected value [4]  !!" % (webrep, test_domain))
            raise TestFailure(msg)
