"""
================
Normalizer tests
================

Tests related to normalizer
"""

import re
import pytest
import runtime
from libx.csvwrap import load_test_data
from libx.process import ShellExecutor


EXCEL_SOURCE_FILE = runtime.data_path + '/tsw/canon/normalizer.xlsx'


def assert_url_normalizer(url_d):
    if not runtime.SH.url_normalizer.isfile():
        raise FileNotFoundError(runtime.SH.url_normalizer)
    stdo, stde = ShellExecutor.run_wait_standalone(runtime.SH.url_normalizer + ' ' + url_d['url'])
    if stde:
        raise RuntimeError(stde)
    print(stdo)
    regex_t = re.findall(r'\s+(\w+):\s(.*)\r*\n', stdo)
    assert regex_t[0][0] == 'url'
    assert regex_t[1][0] == 'getStandardUrlFormat'
    assert regex_t[2][0] == 'getProtocolUrlFormat'
    assert regex_t[3][0] == 'getDomainName'
    assert regex_t[0][1] == url_d['url']
    assert regex_t[1][1] == url_d['standard_url']
    assert regex_t[2][1] == url_d['proto_url']
    assert regex_t[3][1] == url_d['domain']


@pytest.mark.parametrize("data", **(load_test_data(
    excel_or_csv=EXCEL_SOURCE_FILE,
    worksheets=['sample'],
    column_list='test url standard_url proto_url domain'.split())
))
def test_normalizer(data):
    for url_d in data:
        assert_url_normalizer(url_d)


@pytest.mark.xfail
@pytest.mark.parametrize("data", **(load_test_data(
    excel_or_csv=EXCEL_SOURCE_FILE,
    worksheets=['errors'],
    column_list='test url standard_url proto_url domain'.split())
))
def test_normalizer_known_failures(data):
    for url_d in data:
        assert_url_normalizer(url_d)
