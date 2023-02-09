import os
import time
import pytest
import subprocess
from subprocess import call
import logging
import json
import re
import pyodbc
from common.tsw_workflow import workflowAPI

logging.basicConfig(level=logging.DEBUG)
from common.tsw_mssql import MSSQLDBAPI

# List with testCases.
# Format: URL: [sha256_hash, input rep, input cats, expected rep, expected cats, expected cat code, in WSDB]
automationUrlHash = {
    "*://AUTOMATIONTEST.COM":
        ["66FF124EDCD12738A07054D1E36EFA6CF28947955DF8B3E32EA4001A11A75B57", "0", "bu", "0", "bu", "105", True],
    "*://AUTOMATIONTEST.COM/path":
        ["BF6D2ED376FD219461D853A81F1ED413433DF63D7E2A019AEBA6110F4197A008", "", "ms", "127", "ms", "130", True],
    "*://AUTOMATIONTEST.COM/path2":
        ["3B74756F2C192DB26EFD2C1F66A0370AA06B84847F7381A0CC3DAF0D962304A8", "", "sa", "0", "sa", "-", True],
    "*://AUTOMATIONTEST.COM/path3":
        ["8F24DB2671B690197D00BDF2CA2C6D4C4436C0690B5E7CA2D3FA873BC2561F76", "", "xr", "127", "xr", "-", True],
    "*://AUTOMATIONTEST.COM/path4":
        ["D4A16F755D2F0231F95DA4448E54970F2A91E79E9BEB979457C555799E9A7D3C", "", "xy", "30", "xy", "-", True],
    "*://AUTOMATIONTEST.COM/path5":
        ["1CD30BDB5F40935FEB9654B0609C19F4BBC1D0492E7177A804FD3937225C3B2F", "", "xg", "0", "xg", "-", True],
    "*://AUTOMATIONTEST.COM/path6":
        ["869F75FF1F920CC9B56E7CD379FACBEB9BE095C970F1ACD1A54928EDE20EB818", "", "dn", "", "", "", False],
    "*://AUTOMATIONTEST.COM/path7":
        ["C87A61CD4784F90D8730DE5574D1BD6F28881BD627E7E66D9921D1E2B23FD0B6", "", "ih", "", "", "", False],
    "*://AUTOMATIONTEST.COM/path8":
        ["B8E25923F20A7C844E4E9233F45142B6FADE3C5267E1C1197377042DBC0CFD30", "127", "ms", "127", "ms", "130", True],
    "*://AUTOMATIONTEST.COM/path9":
        ["B56CEBD4DC3BB043BA818B0AA2EAC56E057F25FFF3FA601768AA60751C0EDCAC", "127", "xr", "127", "xr", "-", True],
    "*://AUTOMATIONTEST.COM/path10":
        ["2EAD6062B4BD33CB796C50B1202D14A90385D623CDDFDBF0272B6496E72FD89D", "30", "", "", "  ", "", False],
    "*://AUTOMATIONTEST.COM/path11":
        ["B61E42BF0B830B2C025779E3408845ED36DD753C791D2CA793123E2807ADEA1C", "20", "bu", "20", "bu", "105", True],
    "*://AUTOMATIONTEST.COM/path12":
        ["A1358EF529E5136CEF1890E0FE23E2446D07ECFD7B6B71261671F75C1161BF0A", "7", "", "", "", "", False]}

workflow = workflowAPI()
workflow2 = workflowAPI()
workflow.loadApplicationProperties()

# Adding all of the properties to myvars
myvars = workflow.configMap

host = myvars['mssql.streamingUpdates.host']
DB = myvars['mssql.streamingUpdates.db']
user = myvars['mssql.streamingUpdates.username']
pwd = myvars['mssql.streamingUpdates.password']

# R2 connection
r2Conn = MSSQLDBAPI(host, DB, user, "1433", pwd)

host = myvars['mssql.wsdb.host']
DB = myvars['mssql.wsdb.db']
user = myvars['mssql.wsdb.username']
pwd = myvars['mssql.wsdb.password']

# WSDB Connection
wsdbConn = MSSQLDBAPI(host, DB, user, "1433", pwd)


def test_EndToEnd():
    log = logging.getLogger('test_Marcos')

    # Inserting all of the entries of the Map
    for key in automationUrlHash:
        insertStreamingQueue(key, automationUrlHash[key][1], automationUrlHash[key][2])

    # Run the first part of the workflow (provider and activeMQ)
    workflow.run_workflowUnstoppable("", "streamingUpdatesWF1.properties", log)

    # Run the second part of the workflow
    workflow2.run_workflowUnstoppable("", "streamingUpdatesWF2.properties", log)

    # Wait for the S.U.P to run and process everything
    time.sleep(15)

    numberErrors = 0

    # Iterate through the map and get every entry from the WSDB, comparing the WSDB results with the input map results
    for key in automationUrlHash:
        res = getWSDBEntry(automationUrlHash[key][0])
        if len(res) > 0:
            for row in res:
                if str(row[1]) != str(automationUrlHash[key][3]):
                    log.error("Reputation mismatch for URL=" + key + " actual=" + str(row[1])
                              + " expected=" + str(automationUrlHash[key][3]))
                    numberErrors += 1
                if row[2] != automationUrlHash[key][4]:
                    log.error("Category mismatch for URL=" + key + " actual=" + str(row[2])
                              + " expected=" + automationUrlHash[key][4])
                    numberErrors += 1
                if row[3] != automationUrlHash[key][5]:
                    log.error("Category code mismatch for URL=" + key + " actual=" + str(row[3])
                              + " expected=" + automationUrlHash[key][5])
                    numberErrors += 1
        elif automationUrlHash[key][6] == True:
            log.error("Entry missing from WSDB for URL=" + key)
            numberErrors += 1

    # Clean the WSDB and kill the workflow processes if still alive
    cleanAutomationUrlList(automationUrlHash)

    assert (numberErrors == 0)
    log.warning('Be sure that ActiveMQ is configured in this machine. If not, change the properties file of' \
                ' the two workflows to point to one ActiveMQ')


def getWSDBEntry(sha256):
    return wsdbConn.selectDataQuery(
        "SELECT url, reputation, category, category_codes FROM url_status where sha256_hash=0x" + sha256)


def cleanAutomationUrlList(list):
    workflow.kill_workflow()
    workflow2.kill_workflow()
    urlStr = "0x"
    for val in list.itervalues():
        urlStr = urlStr + val[0] + " OR sha256_hash=0x"
    urlStr = urlStr[:-18]
    query = "DELETE from url_status where sha256_hash=" + urlStr
    wsdbConn.insertUpdateDelete(query)


def insertStreamingQueue(url, rep, cat):
    if rep == '':
        rep = "null"

    r2Conn.insertUpdateDelete(
        "insert into R2.dbo.streaming_queue (action, url, categories, reputation, queued_on, updated_on, status)" \
        " values (1, '" + url + "' , '" + cat + "' , " + rep + " , GETUTCDATE(), GETUTCDATE(), 0)")
