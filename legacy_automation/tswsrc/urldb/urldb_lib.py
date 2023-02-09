"""
=======================
URLDB Utility Functions
=======================
"""

__author__ = 'abhijeet'

import json
import logging
import datetime
import runtime
from path import Path
from conf.files import DIR
from lib.db.mssql import TsMsSqlWrap
from lib.db.mongowrap import get_qa_mongo_wrap
from libx.process import ShellExecutor
from runtime import data_path
from conf.properties import prop_urldb_queue_prop

URLDB_MONGODB_NAME = runtime.Mongo.URLDB.dbname
URLDB_URL_COLL = 'url'
URLDB_HARVESTER_EVENT_COLL = 'harvester_event'
URLDB_WORKFLOW_EVENT_COLL = 'workflow_event'
URLDB_QUEUE_TABLE = r'urldb_queue'
URLDB_JSON_DEFAULT_DIR = DIR.urldb_json_dir
DEFAULT_FILE_DEST = DIR.urldb_json_dir


class URLDB:
    """
    Utility functions relevant to URLDB
    """

    def __init__(self):
        self.u2_con = TsMsSqlWrap('U2')
        self.coll_url = get_qa_mongo_wrap(URLDB_URL_COLL, URLDB_MONGODB_NAME)
        self.coll_harvester_event = get_qa_mongo_wrap(URLDB_HARVESTER_EVENT_COLL, URLDB_MONGODB_NAME)
        self.coll_workflow_event = get_qa_mongo_wrap(URLDB_WORKFLOW_EVENT_COLL, URLDB_MONGODB_NAME)
        self.available_coll = {
            'url': self.coll_url,
            'harvester_event': self.coll_harvester_event,
            'workflow_event': self.coll_workflow_event}

    def collection_exists(self, coll_name):
        if not coll_name.lower() in self.available_coll.keys():
            logging.error('Collection name %s is not a valid collection name' % coll_name)
            raise
        if self.available_coll[coll_name.lower()].collection_exists():
            return True
        else:
            return False

    def drop_urldb_mongo(self):
        """
        drops the urldb mongo database if it exists
        """
        if self.coll_url.db_exists():
            self.coll_url.drop_db()

    def clean_url_coll(self):
        """
        drops url collection
        """
        if self.coll_url.collection_exists():
            self.coll_url.delete_all_data_in_collection()

    def clean_harvester_event_coll(self):
        """
        drops url collection
        """
        if self.coll_harvester_event.collection_exists():
            self.coll_harvester_event.delete_all_data_in_collection()

    def clean_workflow_event_coll(self):
        """
        drops url collection
        """
        if self.coll_workflow_event.collection_exists():
            self.coll_workflow_event.delete_all_data_in_collection()

    def urldb_exists(self):
        """
        check whether urldb exists or not
        :return: true or false based on whether urldb database exists or not
        """
        if self.coll_url.collection_exists():
            return True
        else:
            return False

    def get_harvester_sources(self):
        """
        to get distinct harvester sources from U2 database
        :return: tuple of distinct harvester names from U2 harvesters table
        """
        return self.u2_con.get_select_data('select distinct harvester_name from U2.dbo.harvesters')

    def get_workflow_sources(self):
        """
        to get distinct workflow sources from U2 database
        :return: tuple of distinct workflow names from U2 workflows table
        """
        return self.u2_con.get_select_data('select distinct workflow_name from U2.dbo.workflows')

    def clean_urldb_queue_table(self):
        """
        Cleans the urldb queue table in U2
        """
        self.u2_con.execute_sql_commit('truncate table U2.dbo.%s;' % URLDB_QUEUE_TABLE)

    def get_urldb_queue_records(self, sql):
        """
        gets cursor for all records in urldb queue
        :return: cursor for urldb queue
        """
        return self.u2_con.get_select_cursor(sql)

    def create_urldb_queue_record(self, json_filename, source_name, priority=5000,
                                  queued_on=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), pending=0):
        """
        creates record in urldb_queue table in U2
        :param json_filename: the absolute path of the json file
        :param source_name: the source of the json file
        :param priority: priortiy of the json file. Default is 5000
        :param queued_on: datetime stamp when queued('%Y-%m-%d %H:%M:%S'). Defaults to current timestamp
        :param pending: either 1 or 0. Defaults to 0
        """
        #base_data_path = data_path.joinpath('urldb/write_api_n_agent')
        #input_file = base_data_path.joinpath(filename)
        target_file = DEFAULT_FILE_DEST.joinpath(json_filename)
        self.u2_con.execute_sql_commit("insert into U2.dbo.%s values('%s', '%s', %s, '%s', %s)" %
                                       (URLDB_QUEUE_TABLE, json_filename, source_name, priority, queued_on,
                                        pending))

    def clean_urldb_dir(self, dir=URLDB_JSON_DEFAULT_DIR):
        if not isinstance(dir, Path) and dir is str:
            dir = Path(dir)
        if not dir.exists():
            return
        dir_list = dir.listdir()
        for file_path in dir_list:
            if file_path.isfile():
                file_path.remove_p()
            elif file_path.isdir():
                file_path.rmtree_p()

    def list_urldb_dir(self, dir=URLDB_JSON_DEFAULT_DIR):
        if not isinstance(dir, Path) and dir is str:
            dir = Path(dir)
        return dir.listdir()

    def exists_in_urldb_queue(self, filename, source, priority=5000, pending=0, single_match_only = True):
        """
        returns whether given record exists or not
        :param filename: filepath of the json
        :param source: source of the json
        :param priority: priority of the json; default is 5000
        :param pending: pending bit; default is 0
        :param single_match_only: returns True only if a single record matches
        :return: Boolean: true if the record exists; false if not
        """
        result = self.u2_con.get_select_data(
            "select * from U2.dbo.urldb_queue where file_path = '%(file)s' and source = '%(source)s' and priority = %(priority)s and pending = %(pend)s" % {
                'file': filename, 'source': source, 'priority': priority, 'pend': pending})
        rlen = len(result)
        if rlen == 1:
            return True
        elif rlen > 1:
            if single_match_only:
                return False
            else:
                return True
        else:
            return False

    def is_source_for_file(self, source, file):
        """
        checks if source mentioned in json file is the one which is expected
        :param source: the expected source passed as string
        :param file: the Path object of the json file
        :return: Boolean: true if the json has the expected source; false otherwise
        """
        with file.open() as f:
            data = json.load(f)
            if data['source'] == source:
                return True
            else:
                return False

    def run_urldbqueue_agent(self):
        """
        Runs the urldb_queue agent
        :raise FileNotFoundError: when StartAgent.sh or agent property file is not found
        """
        prop_urldb_queue_prop(write_file_bool=True)
        if not runtime.SH.start_agent.isfile():
            raise FileNotFoundError(runtime.SH.start_agent)
        if not runtime.PROP.urldb_queue.isfile():
            raise FileNotFoundError(runtime.PROP.urldb_queue)
        stdo, stde = ShellExecutor.run_wait_standalone('%s %s' % (runtime.SH.start_agent, runtime.PROP.urldb_queue))
        return stdo,stde
        # todo: check std streams for errors

    def url_coll_get_url(self, url):
        """
        returns dictionary for the url with field values from url collection
        :param url:
        :return: returns dictionary from url collection; None if url not found
        """
        query_string = "{'url' : '%s'}"%url
        self.coll_url.add_index('url', 1)
        url_dict = self.coll_url.query_one(query_string)
        return url_dict

    def url_coll_get_query(self, querystring, index_req_list = None):
        if index_req_list:
            for key in index_req_list:
                self.coll_url.add_index('%s'%key, 1)
        return self.coll_url.query(querystring)


    def har_event_coll_get_events_for_urlhash(self, url_hash):
        """
        returns metadata for urlhash
        :param url_hash: url hash from url collection
        :return:
        """
        query_string = "{'urlHash' : '%s'}"%url_hash
        self.coll_harvester_event.add_index('urlHash', 1)
        har_events = self.coll_harvester_event.query(query_string)
        return har_events

    def workflow_event_coll_get_events_for_urlhash(self, url_hash):
        """
        returns metadata for urlhash
        :param url_hash: url hash from url collection
        :return:
        """
        query_string = "{'urlHash' : '%s'}"%url_hash
        self.coll_workflow_event.add_index('urlHash', 1)
        workflow_events = self.coll_workflow_event.query(query_string)
        return workflow_events

    def workflow_event_coll_get_events_for_url(self, url):
        """
        returns metadata for urlhash
        :param url_hash: url hash from url collection
        :return:
        """
        print(self.coll_workflow_event)
        query_string = "{'url' : '%s'}"%url
        self.coll_workflow_event.add_index('url', 1)
        workflow_events = self.coll_workflow_event.query(query_string)
        return workflow_events