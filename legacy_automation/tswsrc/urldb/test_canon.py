"""
============================
Canonicalizer REST API tests
============================

Tests related to canonicalizer REST API
"""


import copy
import logging
import os
from path import Path
import pprint
import unittest

import json_tools
import pytest
import requests

import runtime
from libx.csvwrap import load_test_data
from lib.canon import CanonURL


EXCEL_SOURCE_FILE = Path(runtime.data_path + '/tsw/canon/canonicalizer.xlsx')
CANON_OBJ = CanonURL(runtime.AppServer.fqdn)
CANON_B64_OBJ = CanonURL(runtime.AppServer.fqdn, base64_flag=True)


def setUpModule():
    """
    Module level fixture for Canonicalizer tests. Will be run once.
    :return:
    """
    # Construct REST API and make a test REST call
    rest_test_url = CANON_OBJ.request_url
    try:
        response = requests.get(rest_test_url)
    except Exception:
        msg = 'REST URL is not reachable. Locals: %s' % locals()
        logging.error(msg)
        raise unittest.SkipTest(msg)

    # Must get response of 200 only
    if response.status_code != 200:
        error_message = 'Status code is not 200 in setUpModule. Status code: %s' % response.status_code
        logging.error(error_message)
        raise Exception(error_message)

    # Data excel file is present
    if not os.path.isfile(EXCEL_SOURCE_FILE):
        raise Exception('Source excel file not found at %s' % EXCEL_SOURCE_FILE)


def construct_expected_dict(csv_row):
    """
    Constructs expected dict from csv row data. Helpful for direct json/dict comparison. Converts empty cell to None
    :param csv_row: dict
    :return: expected data
    """
    return {'error': None if csv_row['error'] is '' else csv_row['error'],
            'domain': None if csv_row['domain'] is '' else csv_row['domain'],
            'clhash': None if csv_row['clhash'] is '' else csv_row['clhash'],
            'dbhash': None if csv_row['clhash'] is '' else csv_row['dbhash'],
            'origURL': csv_row['origURL'].strip(),
            'canonicalizedURL': None if csv_row['canonicalizedURL'] is '' else csv_row['canonicalizedURL']}


def assert_canon_dicts(actual_from_json, expected_dict, failures, remove_original_url=None):
    """
    Assertion function for canonicalizer REST API
    :param actual_from_json: parsed JSON from response
    :param expected_dict: generated expected dict
    :param failures: Any failures/exceptions will be appended
    :return: None
    """
    original_url = expected_dict['origURL']
    if remove_original_url:
        new_actual = copy.deepcopy(actual_from_json)
        del new_actual['origURL']
        new_expected = copy.deepcopy(expected_dict)
        del new_expected['origURL']
        diff = json_tools.diff(new_actual, new_expected)
    else:
        diff = json_tools.diff(actual_from_json, expected_dict)
    if diff:
        logging.error('Failure in URL: %s' % original_url + '\nDiff: %s' % diff)
        failures.append(diff)


def action_validate(actual_from_json, csv_row, failures):
    """
    Hook to validate actual and expected data
    :param actual_from_json: parsed JSON from response
    :param csv_row: dict with empty strings
    :param failures:  Any failures/exceptions will be appended
    :return: None
    """
    assert_canon_dicts(actual_from_json, construct_expected_dict(csv_row), failures)


def action_validate_skip_original(actual_from_json, csv_row, failures):
    """
    Hook to validate actual and expected data
    :param actual_from_json: parsed JSON from response
    :param csv_row: dict with empty strings
    :param failures:  Any failures/exceptions will be appended
    :return: None
    """
    assert_canon_dicts(actual_from_json, construct_expected_dict(csv_row), failures, remove_original_url=True)


def action_multiple_errors(actual_from_json, csv_row, failures):
    """
    Hook to assert presence of multiple error strings. Hook will also assert dicts without error key.
    :param actual_from_json: parsed JSON from response
    :param csv_row: dict with empty strings
    :param failures:  Any failures/exceptions will be appended
    :return: None
    """

    # Copy the dict and remove error key
    actual_without_error = copy.deepcopy(actual_from_json)
    actual_without_error.pop('error')
    expected_without_error = copy.deepcopy(construct_expected_dict(csv_row))
    expected_without_error.pop('error')

    # Assert the dicts without key - error
    assert_canon_dicts(actual_without_error, expected_without_error, failures)

    # Error messages are separated by pipe - |
    error_search_strings = csv_row['error'].split('|')

    # Assert the presence of error messages in error field
    for error_string in error_search_strings:
        if error_string not in actual_from_json['error']:
            failures.append('Failure: Error search string "%s" not found in "%s" for URL "%s"' % (
                error_string, actual_from_json['error'], csv_row['origURL']))


def canon_test_template(canon_obj, test_data, action_hook, *, input_key):
    """
    Template for canonicalizer tests
    :param test_data:
    :param action_hook:
    :return:
    """
    # holds failures across assertions
    failures = []
    input_keys_for_removal_from_csv = ['url-input', 'b64-input']
    input_keys_for_removal_from_csv.remove(input_key)
    for row in test_data:
        url = row[input_key]
        for key in input_keys_for_removal_from_csv:
            del row[key]
        logging.info('Processing URL: %s' % url)
        try:
            canon_dict = canon_obj.canon_url(url)
            action_hook(canon_dict, row, failures)
        except Exception as exc:
            err_msg = 'Error in URL: {}\n\t{}'.format(url, exc)
            logging.exception(err_msg)
            failures.append(err_msg)

    # Fail the test if required
    if failures:
        logging.error(pprint.pformat(failures))
        pytest.fail('%s failures encountered. See log for details' % len(failures))

		
# @pytest.mark.parametrize("data", **(load_test_data(EXCEL_SOURCE_FILE, ['test'])))#'URL'])))
# def test_url(data):
#     # canon_test_template(CANON_OBJ, data, action_validate_skip_original, input_key='url-input')
#     canon_test_template(CANON_B64_OBJ, data, action_validate_skip_original, input_key='b64-input')
#     # pass
# # import logging
# # logging.getLogger().setLevel(logging.CRITICAL)
# #
# # url_list, ids = load_test_data(EXCEL_SOURCE_FILE, ['test']).items()
# # for data in url_list[1]:
# #
#     # pprint.pprint(data)
#     # import base64
#     # b = bytes(data[0]['url-input'], encoding='utf-8')
#     # s = base64.urlsafe_b64encode(b).decode(encoding='utf-8')
#     # print(CANON_OBJ.canon_url(data[0]['url-input'])['dbhash'])


@pytest.mark.parametrize("data", **(load_test_data(EXCEL_SOURCE_FILE, ['URL'])))
def test_url(data):
    canon_test_template(data, action_validate_skip_original)


@pytest.mark.parametrize("data", **(load_test_data(EXCEL_SOURCE_FILE, ['IP', 'Google', 'Errors', 'REST'])))
def test_validate(data):
    canon_test_template(CANON_OBJ, data, action_validate, input_key='url-input')


@pytest.mark.xfail
@pytest.mark.parametrize("data", **(load_test_data(EXCEL_SOURCE_FILE, ['KnownFailures'])))
def test_known_failures(data):
    canon_test_template(CANON_OBJ, data, action_validate, input_key='url-input')


@pytest.mark.parametrize("data", **(load_test_data(EXCEL_SOURCE_FILE, ['TLD'])))
def test_errors(data):
    canon_test_template(CANON_OBJ, data, action_multiple_errors, input_key='url-input')


@pytest.mark.parametrize("data", **(load_test_data(EXCEL_SOURCE_FILE, ['IP', 'Google', 'Errors', 'REST'])))
def test_b64_validate(data):
    canon_test_template(CANON_B64_OBJ, data, action_validate, input_key='b64-input')


@pytest.mark.parametrize("data", **(load_test_data(EXCEL_SOURCE_FILE, ['b64'])))
def test_b64_errors_1(data):
    canon_test_template(CANON_B64_OBJ, data, action_validate_skip_original, input_key='b64-input')


@pytest.mark.parametrize("data", **(load_test_data(EXCEL_SOURCE_FILE, ['TLD'])))
def test_b64_errors_2(data):
    canon_test_template(CANON_B64_OBJ, data, action_multiple_errors, input_key='b64-input')
