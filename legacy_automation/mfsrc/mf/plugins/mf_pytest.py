
"""
=====================
pytest-mongodb report
=====================

Saves test results in Mongo db collection
"""

__author__ = 'M'


# import py
import os
# import re
# import sys
# import time
import datetime
from collections import ChainMap
import logging
import pytest
import mongoengine
from mongoengine.document import Document
from mongoengine.fields import IntField, FloatField, DateTimeField, StringField


class TestCaseDoc(Document):
    runid = IntField(min_value=-1, max_value=9999999, required=True)
    # runid = SequenceField()
    session = StringField(required=True)
    node_id = StringField(required=True)
    state = StringField(max_length=10, unique_with=("runid", "session", "node_id"))

    collect_time = DateTimeField()
    result = StringField(required=True)

    report_time = DateTimeField()
    duration = FloatField()
    traceback = StringField()

    start_time = DateTimeField()

    meta = {
        'db_alias': 'mf_pytest',
        'index_options': {'unique': True},
        'index_background': False,
        'index_drop_dups': True,
        'index_cls': False,
        'index_unique': True,
    }


@pytest.mark.tryfirst
def pytest_runtest_makereport(item, call, __multicall__):
    # execute all other hooks to obtain the report object
    report = __multicall__.execute()

    # skip if outcome is passed and call is setup or teardown
    if call.when in ['setup', 'teardown'] and report.outcome == 'passed' and report.passed:
        return report

    runid = item.session.config.mf_mdb_runid

    test_doc = TestCaseDoc.objects(runid=runid,
                                   session=item.session.name,
                                   node_id=report.nodeid,
                                   state='collected').first()
    if not test_doc:
        # create a new document
        new_doc = TestCaseDoc()
        new_doc["runid"] = runid
        new_doc["session"] = item.session.name
        new_doc["node_id"] = report.nodeid
        test_doc = new_doc

    # update the record
    test_doc["state"] = call.when
    test_doc["result"] = report.outcome
    test_doc["duration"] = report.duration
    test_doc["report_time"] = datetime.datetime.now()

    if report.failed:
        test_doc["traceback"] = str(report.longrepr.reprtraceback)
    if report.skipped:
        test_doc["traceback"] = str(report.longrepr[2])

    test_doc.save()
    return report


@pytest.mark.trylast
def pytest_collection_modifyitems(session, config, items):

    runid = config.mf_mdb_runid
    for item in items:
        # print(item)
        stale_doc = TestCaseDoc.objects(runid=runid, session=session.name, node_id=item.nodeid).first()
        if not stale_doc:
            # create a new document
            new_doc = TestCaseDoc()
            new_doc["runid"] = runid
            new_doc["session"] = item.session.name
            new_doc["node_id"] = item.nodeid
        else:
            new_doc = stale_doc
            logging.warning('Stale test document found for: %s' % item.nodeid)
            raise Exception('Stale test document in mongodb! run id sequence already exists %s' % locals())

        new_doc["state"] = 'collected'
        new_doc["collect_time"] = datetime.datetime.now()
        new_doc["result"] = 'not run'

        # update the record
        new_doc.save()


def pytest_addoption(parser):
    group = parser.getgroup("pytest-mongodb report")
    group.addoption('--mdb-runid', '--mongodb-runid', action="store",
                    dest="MF_RESULT_MDB_RUNID", metavar="str", default=None,
                    help="Run ID to associate test results in data collection. Defaults to -1")
    group.addoption('--mdb-url', '--mongodb-connection-url', action="store",
                    dest="MF_RESULT_MDB_URL", metavar="str", default=None,
                    help="Connection string with protocol. ex: mongodb://localhost:27017/database_name")
    group.addoption('--mdb-coll', '--mongodb-collection', action="store",
                    dest="MF_RESULT_MDB_COLL", metavar="str", default=None,
                    help="Collection name to be used")

    parser.addini('MF_RESULT_MDB_RUNID', '--mongodb-run-id')
    parser.addini('MF_RESULT_MDB_URL', '--mongodb-url')
    parser.addini('MF_RESULT_MDB_COLL', '--mongodb-collection')


def pytest_configure(config):

    # merge env and ini - env takes precedence
    env_dict = {k: os.environ[k] for k in os.environ}
    ini_dict = {k: config.getini(k) for k in config.inicfg}
    config_map = ChainMap(env_dict, ini_dict)

    # check for run id in command line args
    if config.option.MF_RESULT_MDB_URL:
        if not config.option.MF_RESULT_MDB_COLL:
            raise Exception('MF_RESULT_MDB_COLL must be present as cmd arg along with MF_RESULT_MDB_URL')
        mf_mdb_url = config.option.MF_RESULT_MDB_URL
        mf_mdb_coll = config.option.MF_RESULT_MDB_COLL

    # check for run id in ini file or environment vars
    elif 'MF_RESULT_MDB_URL' in config_map:
        if 'MF_RESULT_MDB_COLL' not in config_map:
            raise Exception('MF_RESULT_MDB_COLL is not present in environment vars or pytest.ini(env has precedence)')
        mf_mdb_url = config_map['MF_RESULT_MDB_URL']
        mf_mdb_coll = config_map['MF_RESULT_MDB_COLL']
    else:
        raise Exception('MF_RESULT_MDB_URL and MF_RESULT_MDB_COLL Mongo db arguments not found!')

    # check for runid in cmd line args
    if config.option.MF_RESULT_MDB_RUNID:
        mf_mdb_runid = config.option.MF_RESULT_MDB_RUNID
    else:
        # check for runid in env or pytest ini files
        if 'MF_RESULT_MDB_RUNID' in config_map:
            mf_mdb_runid = config_map['MF_RESULT_MDB_RUNID']
        else:
            logging.info('Creating runid. MF_RESULT_MDB_RUNID was not found in env vars or pytest.ini')

            # get new runid from mf_properties
            from pymongo import MongoClient
            client = MongoClient(mf_mdb_url)
            mdb = client[mf_mdb_url.rpartition('/')[2]]
            runid_doc = mdb.mf_properties.find_one(query={"_id": 'runid'})

            # create new runid if required (0 will not be used! find_and_modify increments 0 to 1)
            if not runid_doc:
                mdb.mf_properties.insert({"_id": 'runid', "value": 0})

            # upsert the incremented value
            runid_doc = mdb.mf_properties.find_and_modify(query={"_id": 'runid'},
                                                          update={'$inc': {"value": 1}},
                                                          new=True)
            mf_mdb_runid = runid_doc["value"]
            client.close()
    config.mf_mdb_runid = mf_mdb_runid

    # establish mongo engine connection
    config.mf_mdb_con = mongoengine.connect(mf_mdb_coll, host=mf_mdb_url, alias='mf_pytest')


def pytest_unconfigure(config):
    """un configure the mongo framework plugin"""
    _mf_pytest = getattr(config, 'mf_pytest', None)
    if _mf_pytest:
        del config._mf_pytest
        config.pluginmanager.unregister(_mf_pytest)
