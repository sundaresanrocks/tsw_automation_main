import os
import re
import sys
import logging
import pymssql
import datetime
import unittest
import subprocess

# Logging
FORMAT = '%(asctime)-15s %(message)s'
# logging.basicConfig(filename='myapp.log', level=logging.INFO, format=FORMAT)
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__name__)

agent_name = 'Load_Domains_Telemetry.PS1'
agent_location = 'C:\PowerShell'
ps = 'C:\\Windows\\System32\\system32\\WindowsPowerShell\\v1.0\\powershell.exe'

class TelemetryDomainLoader(unittest.TestCase):
    ''' Telemetry Domain Loader Test Cases '''

    @classmethod
    def setUpClass(cls):        
        pass

    def db_connect(self, host='tsqatelemetrydb01.wsrlab', user='sa ', password='4eszaq1', database='telemetry'):
        try:
            self.conn = pymssql.connect(host=host, user=user, password=password, database=database, as_dict=True)
        except Exception as e:
            print("pymssql Exception : e")
        self.cur = self.conn.cursor()
        # print(self.cur)
        return self.cur

    def run_agent(self, *args):
        ''' Run telemetry domain loader with zero or more arguments'''
        print('Running : ', os.path.join(agent_location, agent_name))
        exe = ["powershell", '-ExecutionPolicy', 'Unrestricted', '.\Load_Domains_Telemetry.PS1' ]
        # exe = ["powershell", '-ExecutionPolicy', '.\Load_Domains_Telemetry.PS1' ]
        if len(args) != 0:
            print('%s Arguments passed'%(len(args)))
            for arg in args:
                print(arg)
                exe.append(arg)
        print(exe)
        os.chdir(agent_location)
        print(os.getcwd())
        psxmlgen = subprocess.Popen(exe, stdout=subprocess.PIPE,)
        (result, error) = psxmlgen.communicate()
        print(str(result))
        print(error)
        return (result, error)

    def remove_view_table(self, date='20140429'):
        cmd = '{}{}'.format('DROP TABLE domains_telemetry_', date)
        try:
            os.rmdir("C:\Domains_Working_"+date)
            print('Directory Removed : C:\Domains_Working_'+date)
        except FileNotFoundError:
            print('Nothing to remove')
        try:
            self.cur.execute("DROP VIEW vDomainsTelemetry")
            print('VIEW Removed : vDomainsTelemetry')
            self.cur.execute(cmd)
            print('TABLE Removed : domains_telemetry_'+date)
        except Exception as e:
            print("Exception while cleaning database : ", e)


    def revert_fileName(self):
        loc = os.path.join('C:\PowerShell','AviMehenwal')
        print(os.rename(loc, '7-Zip'))

    def setUp(self):
        self.cur = self.db_connect()

    def tearDown(self):
        self.conn.close()

    def test_01(self):
        ''' 6197    Tel. Loader: The power shell scripts exists '''
        self.assertTrue(os.path.isfile(os.path.join(agent_location, agent_name)))

    def test_02(self):
        ''' 6199    Tel. Loader: Default date - when no args are passed '''
        (result, error) = self.run_agent()
        print(type(result))
        self.assertEqual(error, None)
        yesterday = datetime.datetime.now() - datetime.timedelta(hours=24)
        month = '{:02d}'.format(yesterday.month)
        day = '{:02d}'.format(yesterday.day)
        pat1 = "{}{}{}".format(yesterday.year, month, day)
        print(pat1)
        pat2 = "{}{}".format(pat1, '_domains_telemetry')
        print(pat2)
        self.assertRegex(result, bytes(pat2, 'utf-8'), pat2+'not found in output : Not processing yesterdays logs')        

    def test_03(self):
        ''' 6201    Tel. Loader: Source check - source dir check '''
        (result, error) = self.run_agent('20131214')
        self.assertRegex(result, bytes('[ERROR]', 'utf-8'), 'No error appeared in agent logs')
        self.assertRegex(result, bytes('No data available for the specifed date', 'utf-8'), 'Agent not responding properly')        

    def test_04(self):
        ''' 6203    Tel. Loader: Source check - _SUCCESS file exists '''
        (result, error) = self.run_agent('Z:\\repper_telemetry', '20140112')
        self.assertRegex(result, bytes('Two command lines specified', 'utf-8'), '2 arguments not accepted properly')
        self.assertRegex(result, bytes('[ERROR]', 'utf-8'), 'No Error appeared in agents logs')
        self.assertRegex(result, bytes('Map/Reduce data is not ready to be loaded', 'utf-8'), 'No Error appeared in agents logs')

    def test_05(self):
        ''' 6205    Tel. Loader: Source check - working dir check '''
        pass

    def test_06(self):
        ''' 6209    Tel. Loader: 7 zip executable check '''
        # loc = os.path.join('C:\PowerShell','7-Zip')
        # print(os.rename(loc, 'AviMehenwal'))
        # self.revert_fileName()
        pass

    def test_07(self):
        ''' 6205    Tel. Loader: Source check - working dir check '''
        (result, error) = self.run_agent('20140427')
        self.assertRegex(result, bytes('One command line specified', 'utf-8'), '1 arguments not accepted properly')
        self.assertRegex(result, bytes('[ERROR]', 'utf-8'), 'No Error appeared in agents logs')
        self.assertRegex(result, bytes('Working directory for the specified date already exists', 'utf-8'), 'No Error appeared in agents logs')
        self.assertTrue(os.path.isdir("C:\Domains_Working_20140427"), 'Working directory donot exist')  

    def test_08(self):
        ''' 6211    Tel. Loader: New working dir is created '''
        self.remove_view_table('20140429')
        (result, error) = self.run_agent('20140429')
        # print('RESULT\n\n')
        # print(result)
        self.assertTrue(os.path.isdir("C:\Domains_Working_20140429"), 'Working directory does not exist')
        # state = False
        # # try:

        # self.cur.execute("USE [telemetry];\
        #         SELECT TABLE_NAME FROM information_schema. tables;")
        # for row in self.cur:
        #     print(row)
        #     print(type(row))
        #     state = True
    
        # except Exception as e:
        #     print("No table created", e)
        #     state = False
        # self.assertTrue(state, "No table created ")
#            with self.assertRaises(e):
#                print("No table created", e)
        # self.cur.execute('SELECT TOP 10 * FROM telemetry.dbo.active_tables (nolock)')
        # print(self.cur)
        # for row in self.cur:
        #     print(row)
        #     print(type(row))

    def test_09(self):
        ''' 6213    Tel. Loader: Existing working directory '''
        self.assertTrue(os.path.isdir("C:\Domains_Working_20140427"), 'Working directory does not exist')
        (result, error) = self.run_agent('20140427')
        self.assertRegex(result, bytes('[ERROR]', 'utf-8'), 'No Error appeared in agents logs')
        self.assertRegex(result, bytes('Working directory for the specified date already exists', 'utf-8'), 'No Error appeared in agents logs')

    def test_10(self):
        ''' 6223    Tel. Loader: No gz files '''
        self.remove_view_table('20140429')
        (result, error) = self.run_agent('20140429')
        self.assertTrue(os.path.isdir("C:\Domains_Working_20140429"), 'Working directory does not exist')
        # try:
        #     self.cur.execute("SELECT top 1 cl_hash FROM telemetry.dbo.domains_telemetry_20140429 (nolock)")
        #     self.cur.execute("SELECT top 1 cl_hash from telemetry.dbo.vDomainsTelemetry (nolock)")
        #     state = True
        #     for row in self.cur:
        #         print(row)
        #         print(type(row))
        # except Exception as e:
        #     print("No table created", e)
        #     state = False
        # self.assertTrue(state, "No table or view created ")

if __name__ == '__main__':
    unittest.main()

# Load_Domains_Telemetry script is unable to connect to db when triggered from Python
