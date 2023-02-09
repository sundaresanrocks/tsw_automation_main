__author__ = 'Anurag'
from libx.sqlwrap import mySqlHelper
import logging
from lib.exceptions import TestFailure
from framework.test import SandboxedTest
from lib.db.mssql import TsMsSqlWrap
from framework.ddt import tsadriver
from lib.sfimport import sfimport
from legacy.ticketlib import TicketingLib
import runtime


@tsadriver
class Ticketing(SandboxedTest):
    @classmethod
    def setUpClass(cls):
        ssh_con = runtime.get_ssh('localhost',user='root',password='xdr5tgb')
        ssh_con.ts_odbc_setup(runtime.DB.U2_name, runtime.DB.D2_name, runtime.DB.R2_name)
        cls.my_sql = mySqlHelper(host=runtime.DB.F2_name, user=runtime.DB.F2_user, passwd=runtime.DB.F2_pass, db="ts_web")
        cls.my_sql.query("set AUTOCOMMIT=1")
        cls.my_sql.query("delete from CustomerURLTicketingSubmits;")
        cls.ms_sql = TsMsSqlWrap('U2')


    def test_ticketing_01(self):
        """TS-1149:Anonymous Tickets with URL are processed properly.
        """
        url = "*://anonymoustests05.com"
        ticket_id = 654321

        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id="+str(ticket_id)
        ins_query  = "INSERT INTO CustomerURLTicketingSubmits(ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES("+str(ticket_id)+", 'Scott', '192.168.1.1', null, '"+url+"', 'test', NOW(), 10000,10, null, 'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"

        logging.info("Cleaning all tickets with id "+str(ticket_id))
        self.my_sql.query(del_query)
        logging.info("Inserting ticket")
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(ticket_id)
        self.my_sql.query(update)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        url_id_list = self.ms_sql.get_select_data(select_query)
        if len(url_id_list) != 1:
            raise TestFailure(" Ticket exists in URLs table " + str(len(url_id_list)) + "number of times")
        #check for change of status
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        status = self.my_sql.query(select_query)
        for i in status[1]:
            for j in i:
                if j.lower() != 'open':
                    raise TestFailure("Ticket status is not changed to OPEN")

                url_id = str(url_id_list[0]['url_id'])
        select_query = "select cat_short from u2.dbo.categories where url_id=" + url_id
        urls = [url]
        cat = """bu"""
        obj=sfimport()
        obj.append_category(urls,cat)
        cat_list = self.ms_sql.get_select_data(select_query)
        for i in cat_list :
            if  i['cat_short'] != 'sx' and i['cat_short'] != 'bu' :
                raise TestFailure(" Wrong categories given to " + url + " " + i['cat_short'])
        #run tman
        # obj = Agents('tman')
        # obj.run_agent(agent_args="-d -i -s -n 10 -D",output_file='anurag.txt')
        # #run
        # TicketingLib.updater(status='open')
        # #check for change of status
        # select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        # build_obj = Build()
        # #time.sleep(300)
        # logging.warning('starting build')
        # build_obj.build_run('migt', 'xl')
        #
        # #run
        # TicketingLib.updater(listtype='xl')
