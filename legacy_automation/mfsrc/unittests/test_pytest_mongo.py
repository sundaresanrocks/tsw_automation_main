# -*- coding: utf-8 -*-

pytest_plugins = "pytester"

__author__ = 'M'


def set_up_env(self,
               ini_runid=False, ini_url=False, ini_coll=False,
               env_runid=False, env_url=False, env_coll=False,
               cmd_runid=False, cmd_url=False, cmd_coll=False):

    pytest_ini = ['[pytest]']
    pytest_ini.append('MF_RUN_ID=1' if ini_runid else '')
    pytest_ini.append('MF_RESULT_MDB_URL=1' if ini_url else '')
    pytest_ini.append('MF_RESULT_MDB_COLL=1' if ini_coll else '')


class Option(object):
    def __init__(self, verbose=False, quiet=False):
        self.verbose = verbose
        self.quiet = quiet

    @property
    def args(self):
        # return ''
        l = ['--instafail']
        if self.verbose:
            l.append('-v')
        if self.quiet:
            l.append('-q')
        return l

def pytest_generate_tests(metafunc):
    if "option" in metafunc.fixturenames:
        metafunc.addcall()

class Tests:
    def test_no_url(self, testdir, option):
        testdir.makepyfile(
            """
            import pytest
            def test_func():
                assert 0
            """
        )
        result = testdir.runpytest(*option.args)
