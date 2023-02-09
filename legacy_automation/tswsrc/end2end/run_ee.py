"""
=====================
End to end test cases
=====================

"""
import logging
import pprint
import runtime
from libx.vm import get_snapshot_wrapper
from libx.csvwrap import load_and_parse_csv_as_dict


E2E_CSV_FILE = runtime.data_path + '/end2end/end2end.csv'
PRE_TEST_PREFIX = 'tsa.end2end.tests.pre.'
POST_TEST_PREFIX = 'end2end/tests/post/'
BUILD_TEST_PREFIX = 'tsa.end2end.tests.build.'

suites = []

#### Parse csv file
class E2E:
    pass
runtime.e2e = E2E

## read the csv file
expected_head_list = 'test_func,url,Category,Reputation group,error_result,Category Provided By'.split(',')
runtime.e2e.csv = load_and_parse_csv_as_dict(E2E_CSV_FILE,
                                                column_list=expected_head_list,
                                                group_by_list=['test_func'])



logging.error(pprint.pformat(runtime.e2e.csv))



#### Reset Environment including VM if any
DB_vm_warp = get_snapshot_wrapper(runtime.DB.vm_name)
DB_vm_warp.revert(runtime.DB.vm_snap)
#### Check environment
#### Make all ssh connections
#tsa.e2e.ssh_build_sfcontrol = runtime.get_ssh()
#tsa.e2e.ssh_build_root = runtime.get_ssh()



#### Run all test suites
#suites.extend([PRE_TEST_PREFIX+test for test in tsa.e2e.csv])
suites.extend(["end2end/tests/sfimport.SFImport.test"])
suites.extend(["end2end/tests/ticketing.Ticketing.test"])
suites.extend(["end2end/tests/sfoh_harvester.SFOH.test"])
suites.extend(["end2end/tests/domip.DOMIP.test"])

#### U2 checks before agents execution
suites.extend(["end2end/e2echecks.U2DBCheck"])
#### Run all agents
suites.extend(["end2end/e2etasks.E2EAgents"])
#### D2 checks after agents execution
suites.extend(["end2end/e2echecks.D2DBCheck"])
#
#
#### MIGT Build
suites.extend(["end2end/e2etasks.E2EBuild.test_migt_xl",
               "end2end/e2etasks.E2EBuild.test_migt_ts"])
#### Verify the test from csv files in migt build
suites.extend(["end2end/e2echecks.SFv4Check"])

#### Master build
#suites.extend(["end2end/e2etasks.E2EBuild.test_master"])
#### Verify the test from csv files in master build
suites.extend(["end2end/e2echecks.SFv4Check"])
#

#### execute all the test suites
logging.critical(pprint.pformat(suites))

run_suite([{'title': 'End to End Tests',
            'desc:': 'end to end test execution',
            'suites': suites}])

print("All done")