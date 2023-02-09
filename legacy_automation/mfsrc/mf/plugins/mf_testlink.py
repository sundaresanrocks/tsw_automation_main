"""
===================
mf_testlink reports
===================

Updates test results in test link

Test link --
-- create test plan if none exists (WEB_R011)
-- query all builds and sort
-- create a new build if required - auto increment

ENV VARS --
- API key
- URL
- PROJECT

"""
import pprint

__author__ = 'M'
import os
import testlink
import pytest

class TestLink:
    # todo: move class up to module
    automated_tests = {}
    automated_tests_ref = {}
    pytest_node_ids = {}
    duplicate_pytest_nodes = set()

    def __str__(self):
        return "_mf_testlink"

    def __repr__(self):
        return "_mf_testlink"

    @staticmethod
    def get_automated_tests_for_test_plan():
        return TestLink.get_automated_tests([TestLink.test_plan_id])

    @classmethod
    def get_automated_tests(cls, test_plans_list):
        return_dict = {}
        for _tp in test_plans_list:
            _tmp_tests = cls._tl.getTestCasesForTestPlan(_tp, execution='2', active='1')
            if _tmp_tests:
                return_dict.update({key: val for key, val in _tmp_tests.items()})
        return return_dict

    @classmethod
    def lookup_pytest_node(cls, pytest_node):
        """

        :param pytest_node:
        :return:
        """
        return cls.pytest_node_ids[pytest_node]

def pytest_addoption(parser):
    parser.addini('tl_url', 'http://[test link server]/testlink/lib/api/xmlrpc.php')
    parser.addini('tl_api_key', 'Testlink->My Settings->API interface->Generate Key')
    parser.addini('tl_project', 'Project name in test link')
    parser.addini('tl_test_plan', 'Prefix $ to pick from environment variable.')
    parser.addini('tl_reference_test_plan', 'Test plan with all tests added.')
    parser.addini('tl_build_name', 'Prefix $ to pick from environment variable.')
    parser.addini('tl_custom_field', '[pytest_node]unique custom_field')

    parser.addini('tl_fail_hard', 'optional [False] True errors on testlink failures')
    parser.addini('tl_new_build', 'optional [False] True creates a new build')


def pytest_configure(config):
    tl_keys = ['tl_url', 'tl_api_key', 'tl_project', 'tl_test_plan', 'tl_build_name']
    missing_tl_keys = {k for k in tl_keys if k not in config.inicfg}

    if missing_tl_keys:
        print('ERROR: Missing testlink ini keys: %s' % missing_tl_keys)
        print('WARNING: mf_testlink plugin will be disabled!')
        return None

    TestLink.testlink_url = config.inicfg['tl_url']
    TestLink.dev_api_key = config.inicfg['tl_api_key']
    TestLink.project_name = config.inicfg['tl_project']

    if config.inicfg['tl_test_plan'].startswith('$'):
        TestLink.plan_name = os.environ[config.inicfg['tl_test_plan'][1:]]
    else:
        TestLink.plan_name = config.inicfg['tl_build_id']

    if config.inicfg['tl_build_name'].startswith('$'):
        TestLink.build_name = os.environ[config.inicfg['tl_build_name'][1:]]
    else:
        TestLink.build_name = config.inicfg['tl_build_name']

    if 'tl_reference_test_plan' in config.inicfg:
        TestLink.plan_ref = config.inicfg['tl_reference_test_plan']
    else:
        TestLink.plan_ref = None

    if 'tl_custom_field' in config.inicfg:
        TestLink.custom_field_name = config.inicfg.get('tl_custom_field')
    else:
        TestLink.custom_field_name = 'pytest_node'

    # connect to test link
    _tl = testlink.TestlinkAPIClient(server_url=TestLink.testlink_url, devKey=TestLink.dev_api_key)
    TestLink._tl = _tl

    # assert test project exists
    test_project = _tl.getTestProjectByName(TestLink.project_name)
    if not test_project:
        print('ERROR: Invalid tl_project name. Unable to find project')
        print('WARNING: mf_testlink plugin will be disabled!')
        return None

    # get project id and prefix
    TestLink.project_id = test_project['id']
    TestLink.project_prefix = test_project['prefix']

    # list of test plans
    plans = {plan['id']: plan for plan in _tl.getProjectTestPlans(TestLink.project_id)}

    # get set of automated test ids
    if TestLink.plan_ref:
        # check if reference test plan exists
        tp_ids_ref = _tl.getTestPlanByName(TestLink.plan_ref)
        if tp_ids_ref:
            tp_ids_ref = [tp_ids_ref]
        else:
            print('ERROR: Invalid tl_reference_test_plan. Unable to find reference test plan')
            print('WARNING: mf_testlink plugin will be disabled!')
            return None
    else:
        # use automated tests in all the test plans as reference
        tp_ids_ref = set(plans)

    # process all referenced tet plans
    TestLink.automated_tests_ref = TestLink.get_automated_tests(tp_ids_ref)

    # create test plan if required
    plan_name = [tp for tp in _tl.getProjectTestPlans(TestLink.project_id) if tp['name'] == TestLink.plan_name]
    if not plan_name:
        _tl.createTestPlan(TestLink.plan_name, TestLink.project_name)
        plan_name = [tp for tp in _tl.getProjectTestPlans(TestLink.project_id) if tp['name'] == TestLink.plan_name]
    TestLink.test_plan_id = plan_name[0]['id']

    # update existing automated tests in current test plan
    TestLink.automated_tests = TestLink.get_automated_tests_for_test_plan()

    # find automated tests that are missing in current test plan
    new_tests_to_add = set(TestLink.automated_tests_ref) - set(TestLink.automated_tests)

    # add test cases to test plan
    for test in new_tests_to_add:
        print(test)
        # hack: uses last item in list using -1 for version ids. #todo: change behaviour #add platform suport
        if len(TestLink.automated_tests_ref[test]) > 1:
            for _platform in TestLink.automated_tests_ref[test]:
                _old_test = TestLink.automated_tests_ref[test][_platform]
                break
        else:
            _old_test = TestLink.automated_tests_ref[test][-1]
        __external_id = TestLink.project_prefix + '-' + _old_test['external_id']
        __version = int(_old_test['version'])
        _tl.addTestCaseToTestPlan(TestLink.project_id, TestLink.test_plan_id, __external_id, __version)

    # update existing automated tests in current test plan
    TestLink.automated_tests = TestLink.get_automated_tests_for_test_plan()

    # update pytest node ids by iterating over automated tests one by one
    def update_pytest_nodes_for_tests_in_tp():
        """update pytest node ids by iterating over automated tests one by one"""
        for test in TestLink.automated_tests:
            # hack: handle platforms properly
            if len(TestLink.automated_tests[test]) > 1:
                for _platform in TestLink.automated_tests[test]:
                    _cur_test = TestLink.automated_tests[test][_platform]
                    break
            else:
                _cur_test = TestLink.automated_tests[test][-1]

            custom_field = _tl.getTestCaseCustomFieldDesignValue(
                TestLink.project_prefix + '-' + _cur_test['external_id'],
                int(_cur_test['version']),
                TestLink.project_id,
                TestLink.custom_field_name,
                'simple')
            if custom_field['value'] not in TestLink.pytest_node_ids:
                TestLink.pytest_node_ids[custom_field['value']] = _cur_test
            else:
                TestLink.duplicate_pytest_nodes.add(_cur_test)

    update_pytest_nodes_for_tests_in_tp()

    # exit if duplicates are found
    if TestLink.duplicate_pytest_nodes:
        print(TestLink.duplicate_pytest_nodes)
        raise Exception("duplicate custom field found! %s" % TestLink.duplicate_pytest_nodes)

    # create test build if required
    TestLink.test_build = [tb for tb in _tl.getBuildsForTestPlan(TestLink.test_plan_id)
                            if tb['name'] == TestLink.build_name]
    if not TestLink.test_build:
        _tl.createBuild(int(TestLink.test_plan_id), TestLink.build_name,
                        'Automated test. Created by mf_testlink plugin.')
        TestLink.test_build = [tb for tb in _tl.getBuildsForTestPlan(TestLink.test_plan_id)
                                if tb['name'] == TestLink.build_name]
    TestLink.test_build_id = TestLink.test_build[0]['id']
    print(TestLink.test_build_id)

    # #todo: move this to test case report part --> see junit plugin
    # update test results
    # get custom field value
    # assert that custom field exists
    # _cur_node = TestLink.lookup_pytest_node(r'tswsrc\urldb\test_canon.py::test_private[IPv4_class_A]')
    # _tl.reportTCResult(testplanid=TestLink.test_plan_id,
    #                    buildid=TestLink.test_build_id,
    #                    status='p',
    #                    testcaseexternalid=_cur_node['full_external_id']
    #
    # )

    config._mf_testlink = str(TestLink)
    config.pluginmanager.register(config._mf_testlink)


def pytest_unconfigure(config):
    """un configure the mf_testlink framework plugin"""
    _mf_testlink = getattr(config, '_mf_testlink', None)
    if _mf_testlink:
        del config._mf_testlink
        config.pluginmanager.unregister(_mf_testlink)


def pytest_runtest_logreport(report):
    test_details = TestLink.pytest_node_ids[report.nodeid]
    _cur_node = TestLink.lookup_pytest_node(r'tswsrc\urldb\test_canon.py::test_private[IPv4_class_A]')
    status = 'not run'
    if report.passed:
        if report.when == "call": # ignore setup/teardown
            status = 'p'
    elif report.failed:
        status = 'f'
    elif report.skipped:
        status = 's'
    TestLink._tl.reportTCResult(testplanid=TestLink.test_plan_id,
                       buildid=TestLink.test_build_id,
                       status=status,
                       testcaseexternalid=_cur_node['full_external_id'])

@pytest.mark.trylast
def pytest_collection_modifyitems(session, config, items):
    node_ids = [i.nodeid for i in items]
    print(node_ids)
    #todo: check for node ids in test link server