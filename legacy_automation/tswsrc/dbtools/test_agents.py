__author__ = 'manoj'


import pytest
from path import Path

import runtime
from libx.csvwrap import load_test_data

EXCEL_SOURCE_FILE = Path(runtime.data_path + '/tsw/agents/agents.xlsx')


@pytest.mark.parametrize(argnames="data", **(load_test_data(EXCEL_SOURCE_FILE, ['version'])))
def test_version(data):
    """Tests version using -V"""
    for search_dict in data:
        print(search_dict['search_string'])
    assert 0

@pytest.mark.parametrize(argnames="data", **(load_test_data(EXCEL_SOURCE_FILE, ['help'])))
def test_help(data):
    """Tests help using -h"""
    for search_dict in data:
        print(search_dict['search_string'])
    assert 0

@pytest.mark.parametrize(argnames="data", **(load_test_data(EXCEL_SOURCE_FILE, ['default-log'])))
def test_default_log(data):
    """Tests for default log location"""
    assert 0

@pytest.mark.parametrize(argnames="data", **(load_test_data(EXCEL_SOURCE_FILE, ['named-log'])))
def test_named_log(data):
    """Tests for named logs"""
    assert 0

@pytest.mark.parametrize(argnames="data", **(load_test_data(EXCEL_SOURCE_FILE, ['debug-log'])))
def test_debug_log(data):
    """Tests for debug logs"""
    assert 0

@pytest.mark.parametrize(argnames="data", **(load_test_data(EXCEL_SOURCE_FILE, ['without-debug-log'])))
def test_without_debug_log(data):
    """Tests without debug logs"""
    assert 0

@pytest.mark.parametrize(argnames="data", **(load_test_data(EXCEL_SOURCE_FILE, ['is-running'])))
def test_is_running(data):
    """Tests is running"""
    assert 0
