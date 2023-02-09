import datetime
import time

import domip.libdwa
import runtime
from framework.test import SandboxedTest
from lib.db.mdbthreat import MongoWrapDOMIP


class DOMIP(SandboxedTest):
    """
    DWA Client TestCases

    """

    def setUp(self):
        """        Clears the DataBase
        """
        SandboxedTest.setUp(self)
        mongo_obj = MongoWrapDOMIP(runtime.Mongo.DOMIP.table)
        mongo_obj.delete_all_data_in_collection()

    def test_dwa_client_process_zone_file_01(self):
        """        tcid : TS-850
        """
        domip.libdwa.check_dwa_environment()
        zoneFileTestData = runtime.data_path + """/DWAClient/test_dwa_client_process_zone_file_01"""
        domip.libdwa.zone_file_processor(zoneFileTestData)
        time.sleep(30)
        expectedDict = [{
                            "_id": "1800woodfloors.com",
                            "first_seen": datetime.datetime.now(),
                            "ips_last_changed": datetime.datetime.now(),
                            "ips_last_checked": datetime.datetime.now(),
                            "nslookup_rcode": 0,
                            "domain_dead_count": 0,
                            "is_primary": False,
                            "exclude_from_publication": False,
                            "ip_data": [
                                {
                                    "_id": "198.71.49.114",
                                    "version": "IPv4",
                                    "seen_first": datetime.datetime.now(),
                                    "seen_last": datetime.datetime.now(),
                                    "active_last_seen": datetime.datetime.now()
                                },
                                {
                                    "_id": "2607:f1c0:1000:600f:fb1:922a:aae4:0",
                                    "version": "IPv6",
                                    "seen_first": datetime.datetime.now(),
                                    "seen_last": datetime.datetime.now(),
                                    "active_last_seen": datetime.datetime.now()
                                }
                            ],
                            "nameserver_data": [
                                {
                                    "_id": "ns51.1and1.com",
                                    "seen_first": datetime.datetime.now(),  # "seen_last" : datetime.datetime.now()
                                },
                                {
                                    "_id": "ns52.1and1.com",
                                    "seen_first": datetime.datetime.now(),  # "seen_last" : datetime.datetime.now()
                                }
                            ]
                        }]
        domip.libdwa.dwa_test_result(expectedDict)

