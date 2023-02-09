"""
===================================
Tasks for End to end test execution
===================================

Run agents or build process tasks

"""

import logging
import time

from framework.test import SandboxedTest
from framework.ddt import tsadriver
from lib.build import Build
from dbtools.agents import Agents


def build_run_migt(list_type):
    """ Runs migt xl/ts build """
    build_obj = Build()
    time.sleep(5)
    logging.warning('starting MIGT XL build')
    build_obj.build_run('migt', list_type)


def build_run_master():
    """ Runs Master All Build """
    build_obj = Build()
    time.sleep(5)
    logging.warning('starting MASTER build')
    build_out = build_obj.build_run('master', 'all')
    return build_out


def run_all_agents():
    """ Runs all Agents """
    tman_obj = Agents('tman')
    tman_obj.run_agent(" -l 1000 -n 5 -d -i -s ")
    wrua_obj = Agents('wrua')
    wrua_obj.run_agent("-n 500 -t 2 ")
    wrman_obj = Agents('wrman')
    wrman_obj.run_agent(" -n 500 -t 2 ")
    cbman_obj = Agents('cbman')
    cbman_obj.run_agent("-n 500 -t 2 ")
    nrua_obj = Agents('nrua')
    nrua_obj.run_agent("-n 500 -t 2 ")
    crua_obj = Agents('crua')
    crua_obj.run_agent(" -n 500 -t 2 ")


@tsadriver
class E2EAgents(SandboxedTest):
    def test_agents(self):
        run_all_agents()


@tsadriver
class E2EBuild(SandboxedTest):
    def test_migt_xl(self):
        build_run_migt("xl")

    def test_migt_ts(self):
        build_run_migt("ts")

    def test_master(self):
        build_run_master()


