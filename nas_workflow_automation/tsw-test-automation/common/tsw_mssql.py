import os
import time
import pytest
import subprocess
from subprocess import call
import logging
import json
import re
import pyodbc

logging.basicConfig(level=logging.DEBUG)

WF_SCRIPT = "/opt/sftools/bin/StartWorkflow.sh"
SFIMPORT_SCRIPT = "/usr2/smartfilter/import/sfimport"
WF_PROP_DIR = ""
AutomationLog = ""


class MSSQLDBAPI():
    def __init__(self, server, database, username, port, password):
        self.connection = pyodbc.connect(
            'DRIVER={FreeTDS};TDS_VERSION=7.2; SERVER=' + server + ';DB=' + database + ';PORT=' + port
            + ';UID=' + username + ';PWD=' + password)

    def insertUpdateDelete(self, queryString):
        cursor = self.connection.cursor()
        cursor.execute(queryString)
        cursor.commit()
        cursor.close()

    def selectDataQuery(self, queryString):
        cursor = self.connection.cursor()
        cursor.execute(queryString)
        rows = cursor.fetchall()
        return rows

    def cleanup(self):
        self.connection.close()
