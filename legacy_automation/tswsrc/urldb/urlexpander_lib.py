""""
=======================
URLExpander Utility Functions
=======================
"""

__author__ = 'sumeet'


import json
import logging
import datetime
import runtime
from path import Path
from conf.files import DIR
from lib.db.mssql import TsMsSqlWrap
from lib.db.mongowrap import get_qa_mongo_wrap
from libx.process import ShellExecutor




class URLExpander:
    """
    Utility functions relevant to URLExpander
    """

    def __init__(self):
        pass


    def run_urlexpander_agent(self,shortened_url):
        """
        Runs the urldb_expander agent

        """
        if not runtime.SH.urlexpander_client.isfile():
            raise FileNotFoundError(runtime.SH.urlexpander_client)
        if not shortened_url:
            logging.error('shortened Url should not be null %s '% shortened_url)
            raise

        stdo, stde = ShellExecutor.run_wait_standalone('%s %s' % (runtime.SH.urlexpander_client,shortened_url))
        return stdo,stde
