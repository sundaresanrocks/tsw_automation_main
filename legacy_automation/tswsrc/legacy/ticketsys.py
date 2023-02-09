# -*- coding: utf-8 -*-
__author__ = 'Anurag'

from random import choice
import logging

from libx.sqlwrap import mySqlHelper
from lib.exceptions import TestFailure
from framework.test import SandboxedTest
from libx.process import ShellExecutor as ShellExecutor
from lib.db.mssql import TsMsSqlWrap
from dbtools.agents import Agents
from lib.build import Build
from lib.sfimport import sfimport
from libx.vm import get_snapshot_wrapper
from legacy.ticketlib import TicketingLib
import runtime
from lib.db.d2_tables import D2
from tests.end2end.e2etasks import run_all_agents


class Ticketing(SandboxedTest):
    policy_cats = ['al', 'an', 'ap', 'au', 'be', 'cc', 'co', 'cp', 'cs', 'cv',
                   'dl', 'dr', 'ex', 'gb', 'gr', 'hk', 'hr', 'hs', 'il', 'ml', 'mn', 'ms',
                   'nd', 'pa', 'pc', 'ph', 'pr', 'pu', 'qd', 'sc', 'sd', 'sm', 'su', 'sx',
                   'sy', 'tb', 'tg', 'uk', 'vi', 'we']  #picked up from tikcet_updater.properties

    @classmethod
    def setUpClass(cls):
        ssh_con = runtime.get_ssh('localhost', user='root', password='xdr5tgb')
        ssh_con.ts_odbc_setup(runtime.DB.U2_name, runtime.DB.D2_name, runtime.DB.R2_name)
        DB_vm_warp = get_snapshot_wrapper(runtime.DB.vm_name)
        DB_vm_warp.revert(runtime.DB.vm_snap)
        cls.my_sql = mySqlHelper(host=runtime.DB.F2_name, user=runtime.DB.F2_user, passwd=runtime.DB.F2_pass, db="ts_web")
        cls.my_sql.query("set AUTOCOMMIT=1")
        cls.my_sql.query("delete from CustomerURLTicketingSubmits;")
        cls.ms_sql = TsMsSqlWrap('U2')
        #using the below URL to directly login to Frameset
        cls.frameset_url = "http://kmark:12secure@172.22.81.102/cgi-bin/tools/sf_frameset?url_id=-1&level=-1&act=l&rowcol=rows&agent_id=11&Priority_Class=A&Queue_Level=-1&From_Queue=1&url=*%3A%2F%2FXZUAMD.PE&view_url=&framerows=430&xinfo=&Memo=&lang=Unspecified&Ignore_Children=on&Send_To_Queue=1&manualWhichList=No"


    def test_01(self):
        """TS-184:Test Customer URL Ticket Submits working properly or not for inserting the dupli
        """
        url = "*://test011.com"
        ms_sql = TsMsSqlWrap('U2')
        ticket_id = 123451
        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(to_email,ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, suggested_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES('anurag_vemuri@mcafee.com'," + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10, 'bu','New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        logging.info(ins_query)
        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        logging.info("Inserting the same ticket 5 times")
        for i in range(5):
            self.my_sql.query(ins_query)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        url_id_list = ms_sql.get_select_data(select_query)
        if len(url_id_list) != 1:
            raise TestFailure(" Ticket exists in URLs table " + str(len(url_id_list)) + "number of times")
        #check for change of status
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        status = self.my_sql.query(select_query)
        for i in status[1]:
            for j in i:
                if j.lower() != 'open':
                    raise TestFailure("Ticket status is not changed to OPEN")

    def test_02(self):
        """ TS-185:Check the run_Ticketing_status _main.sh working properly or not on the duplica
        """
        url = '*://test02.com'
        ticket_id = 123452
        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(to_email,ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, suggested_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES('anurag_vemuri@mcafee.com'," + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10, 'bu','New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        logging.info(ins_query)
        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        logging.info("Inserting the same ticket 5 times")
        for i in range(5):
            self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        url_id_list = self.ms_sql.get_select_data(select_query)
        if len(url_id_list) != 1:
            raise TestFailure(" Ticket exists in URLs table " + str(len(url_id_list)) + "number of times")
        url_id = str(url_id_list[0]['url_id'])
        #check for change of status
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        status = self.my_sql.query(select_query)
        for i in status[1]:
            for j in i:
                if j.lower() != 'open':
                    raise TestFailure("Ticket status is not changed to OPEN")
        select_query = "select cat_short from u2.dbo.categories where url_id=" + url_id
        #categorize
        urls = [url]
        cat = """pd"""
        obj = sfimport()
        obj.append_category(urls, cat)
        cat_list = self.ms_sql.get_select_data(select_query)
        for i in cat_list:
            if i['cat_short'] != 'pd' and i['cat_short'] != 'bu':
                raise TestFailure(" Wrong categories given to " + url + i['cat_short'])

        #run tman
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -n 10 -D", output_file='anurag.txt')
        #run
        TicketingLib.updater(status='open')
        #check for change of status
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        status = self.my_sql.query(select_query)
        for i in status[1]:
            # logging.warning(i)
            for j in i:
                if j.lower() != 'reviewed':
                    raise TestFailure("Ticket status is not changed to REVIEWED")


    def test_03(self):
        """TS-186:Check the run_Ticketing_status _main.sh working properly or not on the ticket
        """
        url = '*://test03.com'
        ticket_id = 123453
        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(to_email,ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES('anurag_vemuri@mcafee.com'," + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10, null,'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        logging.info(ins_query)
        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        logging.info("Inserting the same ticket 5 times")
        for i in range(5):
            self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
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
        cat = """sx"""
        obj = sfimport()
        obj.append_category(urls, cat)
        cat_list = self.ms_sql.get_select_data(select_query)
        for i in cat_list:
            if i['cat_short'] != 'sx' and i['cat_short'] != 'bu':
                raise TestFailure(" Wrong categories given to " + url + i['cat_short'])

        #run tman
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -n 10 -D", output_file='anurag.txt')
        #run
        TicketingLib.updater(status='open')
        #check for change of status
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        status = self.my_sql.query(select_query)
        for i in status[1]:
            # logging.warning(i)
            for j in i:
                if j.lower() != 'reviewed':
                    raise TestFailure("Ticket status is not changed to REVIEWED")

        #running build
        build_obj = Build()
        #time.sleep(300)
        logging.info('starting build')
        build_obj.build_run('migt', 'xl')

        #run
        TicketingLib.updater(listtype='xl')
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        status = self.my_sql.query(select_query)
        for i in status[1]:
            # logging.warning(i)
            for j in i:
                if j.lower() != 'closed':
                    logging.warning("Ticket status is not changed to CLOSED because of CATSERVER MISMATCH")

    def test_04(self):
        """TS-1154:Verify that Anonymous Tickets are not present in the delinquent open reports
        """
        url = "http://test04.com"
        ticket_id = 400000
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, suggested_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES(" + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10, null, 'os', 'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        update_query = "update CustomerURLTicketingSubmits set opened_on= NOW() - INTERVAL 2 HOUR where ticket_id=" + str(
            ticket_id)
        logging.info(ins_query)
        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)

        logging.info("Inserting ticket")
        self.my_sql.query(ins_query)

        logging.info("running new to open")
        TicketingLib.updater(status='new')

        logging.info("updating open time")
        self.my_sql.query(update_query)

        logging.info("Running delinquent")

        stdout, stderr = TicketingLib.delinquent('open', 1, 'anurag_vemuri@mcafee.com')
        if url in stdout:
            raise TestFailure(url + "not present in delinquent")

    def test_05(self):
        """TS-1149:Anonymous Tickets with URL are processed properly.
        """
        url = "*://anonymoustests05.com"
        ticket_id = 654321

        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES(" + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10, null, 'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"

        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        logging.info("Inserting ticket")
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
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
        cat = """sx"""
        obj = sfimport()
        obj.append_category(urls, cat)
        cat_list = self.ms_sql.get_select_data(select_query)
        for i in cat_list:
            if i['cat_short'] != 'sx' and i['cat_short'] != 'bu':
                raise TestFailure(" Wrong categories given to " + url + " " + i['cat_short'])
        #run tman
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -n 10 -D", output_file='anurag.txt')
        #run
        TicketingLib.updater(status='open')
        #check for change of status
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        build_obj = Build()
        #time.sleep(300)
        logging.build('starting build')
        build_obj.build_run('migt', 'xl')

        #run
        TicketingLib.updater(listtype='xl')

    def test_06(self):
        """TS-1150:Anonymous Tickets with IPv4 Address are processed properly.
        """
        url = "*://173.194.77.121"
        ticket_id = 141414

        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES(" + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10, null, 'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"

        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        logging.info("Inserting ticket")
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        select_query = "select url_id from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        url_id = self.my_sql.query(select_query)
        for i in url_id[1]:
            for j in i:
                url_id = int(j)
        select_query = "select * from u2.dbo.urls where url_id = " + str(url_id)
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
        cat = """sx"""
        obj = sfimport()
        obj.append_category(urls, cat)
        cat_list = self.ms_sql.get_select_data(select_query)
        for i in cat_list:
            if i['cat_short'] != 'sx' and i['cat_short'] != 'bu':
                raise TestFailure(" Wrong categories given to " + url + " " + i['cat_short'])
        #run tman
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -n 10 -D", output_file='anurag.txt')
        #run
        TicketingLib.updater(status='open')
        #check for change of status
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        build_obj = Build()
        #time.sleep(300)
        logging.info('starting build')
        build_obj.build_run('migt', 'xl')

        #run
        ShellExecutor.run_wait_standalone("/usr2/smartfilter/dbtools/run_ticket_status.pl --updater --listtype xl")

    def test_07(self):
        """TS-1151:Anonymous Tickets with IPv6 Address are processed properly.
        """
        url = "*://[FEDC:BA98:7654:3210:FEDC:BA98:7654:3210]:80/index.html"
        ticket_id = 161616

        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES(" + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10, null, 'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"

        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        logging.info("Inserting ticket")
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        select_query = "select url_id from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        url_id = self.my_sql.query(select_query)
        for i in url_id[1]:
            for j in i:
                url_id = int(j)
        select_query = "select * from u2.dbo.urls where url_id = " + str(url_id)
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
        cat = """sx"""
        obj = sfimport()
        obj.append_category(urls, cat)
        cat_list = self.ms_sql.get_select_data(select_query)
        for i in cat_list:
            if i['cat_short'] != 'sx' and i['cat_short'] != 'bu':
                raise TestFailure(" Wrong categories given to " + url + " " + i['cat_short'])
        #run tman
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -n 10 -D", output_file='anurag.txt')
        #run
        TicketingLib.updater(status='open')
        #check for change of status
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        build_obj = Build()
        #time.sleep(300)
        logging.info('starting build')
        build_obj.build_run('migt', 'xl')

        #run
        TicketingLib.updater(listtype='xl')

    def test_08(self):
        """TS-1403:Check the open status ticket should be present in the delinquer open reports.
        """
        url = "http://test08.com"
        ticket_id = 800000
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(to_email,ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES('anurag_vemuri@mcafee.com'," + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10, null,'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        update_query = "update CustomerURLTicketingSubmits set opened_on= NOW() - INTERVAL 2 HOUR where ticket_id=" + str(
            ticket_id)
        logging.info(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        logging.info("Inserting ticket")
        self.my_sql.query(ins_query)
        logging.info("running new to open")
        TicketingLib.updater(status='new')
        logging.info("updating open time")
        self.my_sql.query(update_query)
        logging.info("Running delinquent")
        stdout, stderr = TicketingLib.delinquent('open', 1, 'anurag_vemuri@mcafee.com')
        logging.info(stdout)

    def test_09(self):
        """TS-187:Check the Reviewed status ticket should not present in the delinquer open reports
        """
        url = "http://test09.com"
        ticket_id = 141414

        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(to_email,ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES('anurag_vemuri@mcafee.com'," + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10, null,'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        update_query = "update CustomerURLTicketingSubmits set opened_on= NOW() - INTERVAL 2 HOUR where ticket_id=" + str(
            ticket_id)
        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        logging.info("Inserting ticket")
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        select_query = "select url_id from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        url_id = self.my_sql.query(select_query)
        for i in url_id[1]:
            for j in i:
                url_id = int(j)
        select_query = "select * from u2.dbo.urls where url_id = " + str(url_id)
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

        ##
        self.my_sql.query(update_query)
        url_id = str(url_id_list[0]['url_id'])
        select_query = "select cat_short from u2.dbo.categories where url_id=" + url_id
        urls = [url]
        cat = """sx"""
        obj = sfimport()
        obj.append_category(urls, cat)
        cat_list = self.ms_sql.get_select_data(select_query)
        for i in cat_list:
            if i['cat_short'] != 'sx' and i['cat_short'] != 'bu':
                raise TestFailure(" Wrong categories given to " + url + " " + i['cat_short'])
        #run tman
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -n 10 -D", output_file='anurag.txt')
        #run
        TicketingLib.updater(status='open')
        #check for change of status
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        status = self.my_sql.query(select_query)
        for i in status[1]:
            for j in i:
                if j.lower() != 'reviewed':
                    raise TestFailure("Ticket status is not changed to REVIEWED")

        logging.info("Running delinquent")
        stdout, stderr = TicketingLib.delinquent('open', 1, 'anurag_vemuri@mcafee.com')
        logging.info(stdout)

        if url in stdout:
            raise TestFailure(url + "is REVIWED but present in OPEN delinquent")

    def test_10(self):
        """TS-188:Check the Reviewed status ticket should present in the delinquer Reviewed reports
        """
        url = "http://redtube.com"
        ticket_id = 101010

        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(to_email,ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES('anurag_vemuri@mcafee.com'," + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10, null,'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        update_query = "update CustomerURLTicketingSubmits set reviewed_on= NOW() - INTERVAL 2 HOUR where ticket_id=" + str(
            ticket_id)

        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        logging.info("Inserting ticket")
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        select_query = "select url_id from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        url_id = self.my_sql.query(select_query)
        for i in url_id[1]:
            for j in i:
                url_id = int(j)
        select_query = "select * from u2.dbo.urls where url_id = " + str(url_id)
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
        cat = """sx"""
        obj = sfimport()
        obj.append_category(urls, cat)
        cat_list = self.ms_sql.get_select_data(select_query)
        for i in cat_list:
            if i['cat_short'] != 'sx' and i['cat_short'] != 'bu':
                raise TestFailure(" Wrong categories given to " + url + " " + i['cat_short'])
        #run tman
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -n 10 -D", output_file='anurag.txt')
        #run
        TicketingLib.updater(status='open')
        #check for change of status
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        status = self.my_sql.query(select_query)
        for i in status[1]:
            for j in i:
                if j.lower() != 'reviewed':
                    raise TestFailure("Ticket status is not changed to REVIEWED")
        ##
        self.my_sql.query(update_query)

        logging.info("Running delinquent")
        stdout, stderr = TicketingLib.delinquent('reviewed', 1, 'anurag_vemuri@mcafee.com')
        logging.info(stdout)

        if url not in stdout:
            raise TestFailure(url + "is REVIWED and is not present in REVIEWED delinquent")

    def test_11(self):
        """TS-1155:Verify that Anonymous Tickets are not present in the delinquent reviewed reports.
        """
        url = "http://test11.com"
        normalised_url = '*' + url[4:]
        d2_obj = D2(url)
        ticket_id = 110011
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES(" + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10, null, 'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        update_query = "update CustomerURLTicketingSubmits set opened_on= NOW() - INTERVAL 2 HOUR where ticket_id=" + str(
            ticket_id)
        logging.info(ins_query)
        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)

        logging.info("Inserting ticket")
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("running new to open")
        TicketingLib.updater(status='new')
        logging.info("updating open time")
        self.my_sql.query(update_query)
        logging.info("Running delinquent")
        stdout, stderr = TicketingLib.delinquent('open', 1, 'anurag_vemuri@mcafee.com')
        if url in stdout:
            raise TestFailure(url + "anyonymous URL present in open delinquent")
        url_id = "select url_id from u2.dbo.urls where url like '" + normalised_url + "'"
        url_id = self.ms_sql.get_select_data(url_id)
        url_id = str(url_id[0]['url_id'])
        select_query = "select cat_short from u2.dbo.categories where url_id=" + url_id
        urls = [url]
        cat = """sx"""
        obj = sfimport()
        obj.append_category(urls, cat)
        cat_list = self.ms_sql.get_select_data(select_query)
        for i in cat_list:
            if i['cat_short'] != 'sx' and i['cat_short'] != 'bu':
                raise TestFailure(" Wrong categories given to " + url + " " + i['cat_short'])
        update_query = 'update u2.dbo.queue set priority=9999 where url_id=' + url_id
        self.ms_sql.execute_sql_commit(update_query)
        #run tman
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -l 10 -D", output_file='anurag.txt')
        #run
        TicketingLib.updater(status='open')
        stdout, stderr = TicketingLib.delinquent('reviewed', 1, 'anurag_vemuri@mcafee.com')
        if url in stdout:
            raise TestFailure(url + "anyonymous URL present in reviewed delinquent")
        result = d2_obj.check_build_table()
        if result is not None:
            logging.info('url_id is %s ' % result)
        else:
            raise TestFailure('URL not present in build table after running agents')

    def test_12(self):
        """TS-1153:Anonymous Tickets with domain split urls
        """
        url = "http://www.example.com/düsseldorf?neighbourhood=Löric"
        ticket_id = 121212

        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, suggested_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES(" + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10, null, 'os', 'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        logging.info(ins_query)
        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        logging.info("Inserting ticket")
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        select_query = "select url_id from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        url_id = self.my_sql.query(select_query)
        for i in url_id[1]:
            for j in i:
                url_id = int(j)
        select_query = "select * from u2.dbo.urls where url_id = " + str(url_id)
        logging.info("Check " + select_query)
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
        #run tman
        run_all_agents()
        #run
        TicketingLib.updater(status='open')
        #check for change of status
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        build_obj = Build()
        #time.sleep(300)
        logging.info('starting build')
        build_obj.build_run('migt', 'xl')

        #run
        TicketingLib.updater(listtype='xl')

    def test_13(self):
        """ TS-1152:Anonymous Tickets with URL having cgi parameters are processed properly.
        """
        url = "*://testingdata1.com/?abc=1&xyz=abc&string=en-us"
        ticket_id = 131313

        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES(" + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10, null, 'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"

        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        logging.info("Inserting ticket")
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        select_query = "select url_id from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        url_id = self.my_sql.query(select_query)
        for i in url_id[1]:
            for j in i:
                url_id = int(j)
        select_query = "select * from u2.dbo.urls where url_id = " + str(url_id)
        logging.info("Check " + select_query)
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
        cat = """sx"""
        obj = sfimport()
        obj.append_category(urls, cat)
        cat_list = self.ms_sql.get_select_data(select_query)
        for i in cat_list:
            if i['cat_short'] != 'sx' and i['cat_short'] != 'bu':
                raise TestFailure(" Wrong categories given to " + url + " " + i['cat_short'])
        #run tman
        obj = Agents('tman')
        obj.run_agent(agent_args="-d -i -s -n 10 -D", output_file='anurag.txt')
        #run
        TicketingLib.updater(status='open')
        #check for change of status
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        build_obj = Build()
        #time.sleep(300)
        logging.info('starting build')
        build_obj.build_run('migt', 'xl')

        #run
        TicketingLib.updater(listtype='xl')

    def test_14(self):
        """TS-1428:Check for update of user suggeseted category for a URL when initial category is NULL
        """
        url = '*://test14.com'
        ticket_id = 1231414
        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(to_email,ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, suggested_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES('anurag_vemuri@mcafee.com'," + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10, null, 'bu', 'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        logging.info(ins_query)
        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        url_id_list = self.ms_sql.get_select_data(select_query)
        if len(url_id_list) != 1:
            raise TestFailure(" Ticket exists in URLs table " + str(len(url_id_list)) + "number of times")
        url_id = str(url_id_list[0]['url_id'])
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        status = self.my_sql.query(select_query)
        for i in status[1]:
            for j in i:
                if j.lower() != 'open':
                    raise TestFailure("Ticket status is not changed to OPEN")
        cat_query = "select cat_short from u2.dbo.categories where url_id=" + url_id
        cat_list = self.ms_sql.get_select_data(cat_query)
        if len(cat_list) == 0:
            raise TestFailure('bu category is not appended to URL ' + url)
        for i in cat_list:
            # logging.warning(i['cat_short'])
            if i['cat_short'] != 'bu':
                raise TestFailure("Business category is suggested but not present in categories table for" + url)

    def test_15(self):
        """TS-1427:Check for update of categories suggested by Customer for URLs that do not have security categories"""
        url = '*://test15.com'
        ticket_id = 1231415
        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(to_email,ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, suggested_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES('anurag_vemuri@mcafee.com'," + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10,'', 'bu', 'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        logging.info(ins_query)
        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        url_id_list = self.ms_sql.get_select_data(select_query)
        logging.info(url_id_list[0]['url_id'])
        if len(url_id_list) != 1:
            raise TestFailure(" Ticket exists in URLs table " + str(len(url_id_list)) + "number of times")
        url_id = str(url_id_list[0]['url_id'])
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        status = self.my_sql.query(select_query)
        for i in status[1]:
            for j in i:
                if j.lower() != 'open':
                    raise TestFailure("Ticket status is not changed to OPEN")
        cat_query = "select cat_short from u2.dbo.categories where url_id=" + url_id
        cat_list = self.ms_sql.get_select_data(cat_query)
        if len(cat_list) == 0:
            raise TestFailure('bu category is not appended to URL ' + url)
        for i in cat_list:
            if i['cat_short'] != 'bu':
                raise TestFailure("Business category is suggested but not present in categories table for" + url)

    def test_16(self):
        """TS-1611:Check that a policy category should not get appended to the url if suggested by the user"""
        url = '*://test16.com'
        ticket_id = 1231416
        policy_cat = choice(self.policy_cats)
        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(to_email,ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, suggested_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES('anurag_vemuri@mcafee.com'," + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10,'','" + policy_cat + "', 'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        logging.info(ins_query)
        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        url_id_list = self.ms_sql.get_select_data(select_query)
        logging.info(url_id_list[0]['url_id'])
        if len(url_id_list) != 1:
            raise TestFailure(" Ticket exists in URLs table " + str(len(url_id_list)) + "number of times")
        url_id = str(url_id_list[0]['url_id'])
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        status = self.my_sql.query(select_query)
        for i in status[1]:
            for j in i:
                if j.lower() != 'open':
                    raise TestFailure("Ticket status is not changed to OPEN")
        cat_query = "select cat_short from u2.dbo.categories where url_id=" + url_id
        cat_list = self.ms_sql.get_select_data(cat_query)
        for i in cat_list:
            if i['cat_short'] == policy_cat and i['cat_short'] != 'bu':
                raise TestFailure(
                    policy_cat + " Policy category is suggested and is present in categories table for" + url)

    def test_17(self):
        """TS-1157:Check that a URL with initial categories should not be categorised again"""
        url = '*://test17.com'
        ticket_id = 1231417
        initial_cat = 'bu'
        suggested_cat = 'ac'
        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(to_email,ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, suggested_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES('anurag_vemuri@mcafee.com'," + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10,'" + initial_cat + "','" + suggested_cat + "', 'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        logging.info(ins_query)
        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        url_id_list = self.ms_sql.get_select_data(select_query)
        logging.info(url_id_list[0]['url_id'])
        if len(url_id_list) != 1:
            raise TestFailure(" Ticket exists in URLs table " + str(len(url_id_list)) + "number of times")
        url_id = str(url_id_list[0]['url_id'])
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        status = self.my_sql.query(select_query)
        for i in status[1]:
            for j in i:
                if j.lower() != 'open':
                    raise TestFailure("Ticket status is not changed to OPEN")
        cat_query = "select cat_short from u2.dbo.categories where url_id=" + url_id
        cat_list = self.ms_sql.get_select_data(cat_query)
        for i in cat_list:
            if i['cat_short'] == suggested_cat and i['cat_short'] != 'bu':
                raise TestFailure(suggested_cat + " is appended to already categorised " + url + " as " + initial_cat)

    def test_18(self):
        """TS-1426:Check for update of url_id for anonymous ticket in mysql DB after a ticket changes from NEW to OPEN"""
        url = '*://test178.com'
        ticket_id = 1231418
        initial_cat = 'bu'
        suggested_cat = 'ac'
        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(to_email,ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, suggested_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES('anurag_vemuri@mcafee.com'," + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10,'" + initial_cat + "','" + suggested_cat + "', 'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        logging.info(ins_query)
        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        url_id_list = self.ms_sql.get_select_data(select_query)
        url_id = str(url_id_list[0]['url_id'])
        select_query = "select url_id from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        mysql_id = self.my_sql.query(select_query)
        for i in mysql_id[1]:
            for j in i:
                if str(j) == str(0):
                    raise TestFailure('URL id is recoreded as 0 (Zero)')
                elif str(j) == url_id:
                    logging.info('URL ID in MYSQL DB is ' + url_id)

    def test_19(self):
        """TS-1429:Test for update of user suggested categories when the initial category is EMPTY"""
        url = '*://test19.com'
        ticket_id = 1231419
        select_query = "select url_id from u2.dbo.urls where url like '" + url + "'"
        del_query = "delete from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        ins_query = "INSERT INTO CustomerURLTicketingSubmits(to_email,ticket_id, partner_id, remote_ip, cc_email, url, comments,submitted_on, submitted_list_id, priority, initial_categories, suggested_categories, status, expected_categories, opened_on,reviewed_on, closed_on, closed_list_id,send_open_email, send_reviewed_email, send_closed_email, database_type, cat_set_version)VALUES('anurag_vemuri@mcafee.com'," + str(
            ticket_id) + ", 'Scott', '192.168.1.1', null, '" + url + "', 'test', NOW(), 10000,10,'', 'bu', 'New',null, null, null, null, null, 1, 1, 1,'xl', -1);"
        logging.info(ins_query)
        logging.info("Cleaning all tickets with id " + str(ticket_id))
        self.my_sql.query(del_query)
        self.my_sql.query(ins_query)
        update = "update CustomerURLTicketingSubmits set suggested_categories = 'bu'  where ticket_id = " + str(
            ticket_id)
        self.my_sql.query(update)
        logging.info("Running updater from NEW to OPEN")
        TicketingLib.updater(status='new')
        url_id_list = self.ms_sql.get_select_data(select_query)
        if len(url_id_list) != 1:
            raise TestFailure(" Ticket exists in URLs table " + str(len(url_id_list)) + "number of times")
        url_id = str(url_id_list[0]['url_id'])
        select_query = "select status from CustomerURLTicketingSubmits where ticket_id=" + str(ticket_id)
        status = self.my_sql.query(select_query)
        for i in status[1]:
            for j in i:
                if j.lower() != 'open':
                    raise TestFailure("Ticket status is not changed to OPEN")
        cat_query = "select cat_short from u2.dbo.categories where url_id=" + url_id
        cat_list = self.ms_sql.get_select_data(cat_query)
        if len(cat_list) == 0:
            raise TestFailure('bu category is not appended to URL ' + url)
        for i in cat_list:
            logging.info(i['cat_short'])
            if i['cat_short'] != 'bu':
                raise TestFailure("Business category is suggested but not present in categories table for" + url)

