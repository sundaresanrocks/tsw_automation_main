import os
import time
import pytest
import subprocess
from subprocess import call
import sys
import random
import string
import datetime
import logging
from common.tsw_workflow import workflowAPI

logging.basicConfig(level=logging.DEBUG)
from common.tsw_mssql import MSSQLDBAPI

# Constants
TEST_AGENT_ID = 21
TEST_HARVESTER_NAME = "WA Maintenance"
TEST_QUEUE_NAME = "Celtic"
TEST_QUEUE_ID = 372
TEST_CAT = "cv"
SFIMPORT_WAIT = 120
URL_COUNT = 10
PROCESS_COUNT = 4
START = '*://'
TLD_LIST = [".COM", ".CO.UK", ".EDU", ".GOV.UK", ".GOV.IE"]
DIR_PREFIX = "sfimport/log_sfimport_"
SFIMPORT_PATH = "/usr2/smartfilter/import/sfimport"

# Load DB properties
workflowAPI = workflowAPI()
workflowAPI.loadApplicationProperties()

# Adding all of the properties to myvars
myvars = workflowAPI.configMap

host = myvars['mssql.u2.host']
DB = myvars['mssql.u2.db']
user = myvars['mssql.u2.username']
pwd = myvars['mssql.u2.password']

# U2 Connection
u2Conn = MSSQLDBAPI(host, DB, user, "1433", pwd)


# Add random URLs to a queue using multiple concurrent sfimport processes,
# and check that they are actually added to the queue. Also remove the test
# URLs afterwards and check that they are removed.
def testQueues():
    log = logging.getLogger('test_sfimport_queues')

    urls = []

    now = datetime.datetime.now()
    date = now.strftime("%Y%m%d%H%M")

    working_dir = DIR_PREFIX + date + "/"

    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    # Generate input files with random URLs
    for instance in range(PROCESS_COUNT):
        file = open(working_dir + "urls_" + str(instance) + ".txt", "w")

        for x in range(URL_COUNT):
            domain_len = random.randint(13, 37)
            domain = ''.join(
                random.choice(string.ascii_uppercase + string.digits)
                for _ in range(domain_len))
            end = random.choice(TLD_LIST)
            url = START + domain + end
            urls.append(url)
            file.write(url + "\n")

        file.close()

    # Start sfimport processes to queue URLs
    for instance in range(PROCESS_COUNT):
        out = open(working_dir + "stdout_queue_" + str(instance) + ".txt", "w")
        err = open(working_dir + "stderr_queue_" + str(instance) + ".txt", "w")
        cmd = SFIMPORT_PATH + " -Q -f u"
        cmd += " -a " + str(TEST_AGENT_ID)
        cmd += " -H \"" + TEST_HARVESTER_NAME
        cmd += "\" -q \"" + TEST_QUEUE_NAME + "\""
        cmd += " -c " + TEST_CAT
        cmd += " -l " + working_dir + "urls_" + str(instance) + ".txt"

        subprocess.Popen(cmd, shell = True, stdout = out, stderr = err)

    # Wait for sfimport instances to finish
    time.sleep(SFIMPORT_WAIT)

    # Get all rows from our test queue
    res = getQueueEntries(TEST_QUEUE_ID)
    assert len(res) > 0

    # Extract queued URLs
    queuedUrls = []
    for row in res:
        queuedUrls.append(row[0])
        assert row[1] == "cv"

    # Check test URLs are in the expected queue
    for url in urls:
        assert url in queuedUrls

    # Start sfimport processes to remove test data from DB
    for instance in range(PROCESS_COUNT):
        out = open(working_dir + "stdout_delete_" + str(instance) + ".txt", "w")
        err = open(working_dir + "stderr_delete_" + str(instance) + ".txt", "w")
        cmd = SFIMPORT_PATH + " -d -f u"
        cmd += " -a " + str(TEST_AGENT_ID)
        cmd += " -H \"" + TEST_HARVESTER_NAME + "\""
        cmd += " -l " + working_dir + "urls_" + str(instance) + ".txt"

        subprocess.Popen(cmd, shell = True, stdout = out, stderr = err)

    # Wait for sfimport instances to finish
    time.sleep(SFIMPORT_WAIT)

    # Check our test queue is now empty
    res = getQueueEntries(TEST_QUEUE_ID)
    assert len(res) == 0


# Retrieve information about queue entries from the specified queue.
def getQueueEntries(queueId):
    return u2Conn.selectDataQuery(
        "SELECT u.url, r.cat_short, q.url_id, q.cur_level, q.priority, q.queue"
            + " FROM U2.dbo.queue q, U2.dbo.urls u, U2.dbo.rec_categories r"
            + " WHERE q.queue = " + str(queueId) + " AND q.url_id = u.url_id"
            + " AND q.url_id = r.url_id")
