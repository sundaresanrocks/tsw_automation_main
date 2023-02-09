import os
import time
import pytest
import subprocess
from subprocess import call
import logging
import json
import re
import pyodbc
from tsw_workflow import workflowAPI
logging.basicConfig(level=logging.DEBUG)
from tsw_mssql import MSSQLDBAPI

 #                                                                                                                   Input Data        Expected Data      in WSDB
 #                                                                                                               ---------------    ---------------
#List with testCases           URL                                      sha256_hash                                        Rep  Cat    Rep   Cat  CatCode
automationUrlHash ={"*://AUTOMATIONTEST.COM" :     ["66FF124EDCD12738A07054D1E36EFA6CF28947955DF8B3E32EA4001A11A75B57",    "0"  ,"bu", "0" ,  "bu", "105",     True] ,
                     "*://AUTOMATIONTEST.COM/PATH" :  ["9378028436FEC076D1EF5AD7479B5B33722E3179D754CDBEA8C1434C3BCE5366", "",   "ms", "127" ,"ms" ,"130",   True] ,
                     "*://AUTOMATIONTEST.COM/PATH2" : ["CD1FE13887D3ADBEE9440D3F17AEA103CE2B6A309FBDC3EC7917DB4E26EEF433", "",   "sa", "16" ,  "sa" ,"-",     True] ,
                     "*://AUTOMATIONTEST.COM/PATH3" : ["B42A4A78CCE1D7C6288E73D80F1980B0816985D8C01FA629D652BB81E0935963", "",   "xr", "127" ,"xr", "-",     True] ,
                     "*://AUTOMATIONTEST.COM/PATH4" : ["3C0F4A9A7EC30AA9EAAC61F67A77396E5A6D8BB6EE6A6CB7D819F76A8B5A5BEF", "",   "xy", "30" , "xy", "-",     True] ,
                     "*://AUTOMATIONTEST.COM/PATH5" : ["0F6BDB4FE0812F02B5F3CFE07963DF41B3E517F1DC3731317BA82BEBA32D9B5A", "",   "xg", "16","xg", "-",     True] ,
                     "*://AUTOMATIONTEST.COM/PATH6" : ["980C3CA2CCC43EA28B3BDF281F83CF1088DA5BB6BEEDB5FAFCFDB15B594DE750", "",   "dn", ""     ,"",   "",     False] ,
                     "*://AUTOMATIONTEST.COM/PATH7" : ["30F7A3951D3AE927F9082ACC669C69519F62FD2D0585623F5E1ADE79192D11B2", "",   "ih", "" ,    "",   "",     False] ,
                     "*://AUTOMATIONTEST.COM/PATH8" : ["BEDE56823225AC4D811203135761ACADDAAA12B8F201937BF5CFEE85EC46F27E", "127","ms", "127" ,"ms", "130",   True] ,
                     "*://AUTOMATIONTEST.COM/PATH9" : ["0FCE98047839BCB17147E9BE119C41004DC77F512D07D7900262F5CEF52B0A49", "127","xr", "127" ,"xr", "-",     True] ,
                     "*://AUTOMATIONTEST.COM/PATH10" : ["1DD1B1356A5D4C1C9A743F115C5CFA592D7115BB7191EFD7E612258292D84745", "30", "",  "" ,"  ", "",        False] ,
                     "*://AUTOMATIONTEST.COM/PATH11" : ["3D7684FC39F01BBE1B5B1FB0FDCF458D3525E68AAC8B9EF268B7872921639951", "20","bu", "20" , "bu", "105",  True] ,
                     "*://AUTOMATIONTEST.COM/PATH12" : ["8288AFAE30AB0AB3E9C7815994B870A80F410A379A2BEED1043ED90BEA1AF43F", "7",  "",   "" ,   "",  "",     False] }




workflow = workflowAPI()
workflow2 = workflowAPI()
workflow.loadApplicationProperties()

#Adding all of the properties to myvars
myvars = workflow.configMap

host = myvars['mssql.streamingUpdates.host']
DB = myvars['mssql.streamingUpdates.db']
user = myvars['mssql.streamingUpdates.username']
pwd = myvars['mssql.streamingUpdates.password']
#R2 connection
r2Conn = MSSQLDBAPI(host, DB, user, "1433", pwd)




host = myvars['mssql.wsdb.host']
DB = myvars['mssql.wsdb.db']
user = myvars['mssql.wsdb.username']
pwd = myvars['mssql.wsdb.password']
#WSDB Connection
wsdbConn = MSSQLDBAPI(host, DB, user, "1433", pwd)


def test_EndToEnd():
   log = logging.getLogger('test_Marcos')

#Inserting all of the entries of the Map
   for key in automationUrlHash:
      insertStreamingQueue(key,automationUrlHash[key][1], automationUrlHash[key][2])

#Running the first part of the workflow, (provider and activeMQ) 
   workflow.run_workflowUnstoppable("", "streamingUpdatesWF1.properties", log)
   workflow2.run_workflowUnstoppable("", "streamingUpdatesWF2.properties", log)

#Waiting 15 seconds to the S.U.P to run and process everything
   time.sleep(15)


   numberErrors = 0

#Iterating in the map and getting every entry from the WSDB, comparing the WSDB results with the input map results
   for key in automationUrlHash:
      res = getWSDBEntry(automationUrlHash[key][0])
      if len(res) > 0:  
       for row in res:
         if (str(row[1]) != str(automationUrlHash[key][3])):
           log.error("In entry" + key + " WSDB rep==" +str(row[1]) + " and the expectedValue=" + str(automationUrlHash[key][3])) 
           numberErrors = numberErrors + 1
         if row[2] != automationUrlHash[key][4]:
           log.error("In entry " + key + " WSDB cat=="+str(row[2]) + " and the expectedValue=" + automationUrlHash[key][4])
           numberErrors = numberErrors + 1
         if row[3] != automationUrlHash[key][5]:
           log.error("In entry " + key + " WSDB categoryCode=="+ str(row[3]) + " and the expectedValue=" + automationUrlHash[key][5]) 
           numberErrors = numberErrors + 1
      elif automationUrlHash[key][6] == True:
        log.error("In entry " +key+ " WSDB has not data and it should")
        numberErrors = numberErrors + 1

#Cleaning the WSDB and killing the Workflow processes if still alive
   cleanAutomationUrlList(automationUrlHash)

   assert(numberErrors == 0)
   log.warning('Be sure than ActiveMQ is configured in this machine, if not, change the properties file of the two workflows to point to one ActiveMQ')
def getWSDBEntry(sha256):
   return wsdbConn.selectDataQuery("SELECT url, reputation, category, category_codes  FROM url_status where sha256_hash =0x" +sha256)


def cleanAutomationUrlList(list):
   workflow.kill_workflow()
   workflow2.kill_workflow()
   urlStr = "0x"
   for val in list.itervalues():
     urlStr =   urlStr + val[0] + " OR sha256_hash=0x"
   urlStr = urlStr[:-18]
   query = "DELETE from url_status where sha256_hash="+urlStr
   wsdbConn.insertUpdateDelete(query) 



def insertStreamingQueue(url, rep, cat):
 if rep == '':
   rep = "null"
  
 r2Conn.insertUpdateDelete("insert into R2.dbo.streaming_queue (action, url, categories, reputation, queued_on, updated_on, status) values  (1, '"+ url + "' , '" + cat + "' , " + rep + " , GETUTCDATE(), GETUTCDATE(), 0)")

