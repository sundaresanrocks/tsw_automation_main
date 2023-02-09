"""
todo
1.Automate IPV6 testcase
2.Zonefile with an unknown domain (Make it into 2 testcases)
"""

import datetime
import time
import runtime
import domip.libdwa
from framework.test import SandboxedTest
from lib.db.mongowrap import MongoWrap


class DWAClientTestCases(SandboxedTest):
    """
    DWA Client TestCases
    Pending
    1.tcid
    2.variable name conventions
    """

    def setUp(self):
        """        Clears the DataBase
        """
        SandboxedTest.setUp(self)
        mongo_obj = MongoWrap(runtime.Mongo.DOMIP.table)
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


    def test_dwa_client_process_zone_file_02(self):
        """        tcid-1094
        """
        domip.libdwa.check_dwa_environment()
        zoneFileTestData = runtime.data_path + """/DWAClient/test_dwa_client_process_zone_file_02"""
        domip.libdwa.zone_file_processor(zoneFileTestData)
        time.sleep(30)
        expectedDict = [{
                            "_id": "z-indexproductions.com",
                            "first_seen": datetime.datetime.now(),
                            "ips_last_changed": datetime.datetime.now(),
                            "ips_last_checked": datetime.datetime.now(),
                            "nslookup_rcode": 0,
                            "domain_dead_count": 0,
                            "is_primary": False,
                            "exclude_from_publication": False,
                            "ip_data": [{
                                            "_id": "2607:f298:5:115b:0:0:71d:345d",
                                            "version": "IPv6",
                                            "seen_first": datetime.datetime.now(),
                                            "seen_last": datetime.datetime.now(),
                                            "web_published": True,
                                            "active_last_seen": datetime.datetime.now()
                                        }, {
                                            "_id": "66.33.210.113",
                                            "version": "IPv4",
                                            "seen_first": datetime.datetime.now(),
                                            "seen_last": datetime.datetime.now(),
                                            "web_published": True,
                                            "active_last_seen": datetime.datetime.now()
                                        }],
                            "nameserver_data": [{
                                                    "_id": "ns1.dreamhost.com",
                                                    "seen_first": datetime.datetime.now()
                                                }, {
                                                    "_id": "ns2.dreamhost.com",
                                                    "seen_first": datetime.datetime.now()
                                                }, {
                                                    "_id": "ns3.dreamhost.com",
                                                    "seen_first": datetime.datetime.now()
                                                }]
                        }
        ]
        domip.libdwa.dwa_test_result(expectedDict)

    def test_dwa_client_process_zone_file_ipv4_03(self):
        """
        tcid : TS-851

        """
        domip.libdwa.check_dwa_environment()
        zoneFileTestData = runtime.data_path + """/DWAClient/test_dwa_client_process_zone_file_ipv4_03"""
        domip.libdwa.zone_file_processor(zoneFileTestData)

        time.sleep(30)
        expectedDict = [{
                            "_id": "1234help.com",
                            "first_seen": datetime.datetime.now(),
                            "ips_last_changed": datetime.datetime.now(),
                            "ips_last_checked": datetime.datetime.now(),
                            "nslookup_rcode": 0,
                            "domain_dead_count": 0,
                            "is_primary": False,
                            "exclude_from_publication": False,
                            "ip_data": [{
                                            "_id": "208.236.11.36",
                                            "version": "IPv4",
                                            "seen_first": datetime.datetime.now(),
                                            "seen_last": datetime.datetime.now(),
                                            "active_last_seen": datetime.datetime.now()
                                        }],
                            "nameserver_data"
                            : [{
                                   "_id": "ns.nationala-1advertising.com",
                                   "seen_first": datetime.datetime.now(),  # "seen_last" : datetime.datetime.now()
                               }, {
                                   "_id": "ns2.nationala-1advertising.com",
                                   "seen_first": datetime.datetime.now(),  # "seen_last" : datetime.datetime.now()
                               }, {
                                   "_id": "ns3.nationala-1advertising.com",
                                   "seen_first": datetime.datetime.now(),  # "seen_last" : datetime.datetime.now()
                               }, {
                                   "_id": "ns4.nationala-1advertising.com",
                                   "seen_first": datetime.datetime.now(),  # "seen_last" : datetime.datetime.now()

                               }
                            ]
                        }]
        domip.libdwa.dwa_test_result(expectedDict)


    def test_dwa_client_process_zone_file_04(self):
        """
        tcid : 1095

        """

        domip.libdwa.check_dwa_environment()
        zoneFileTestData = runtime.data_path + """/DWAClient/test_dwa_client_process_zone_file_04_01"""
        time.sleep(30)
        domip.libdwa.zone_file_processor(zoneFileTestData)

        time.sleep(30)
        expectedDict = [{
                            "_id": "domainiptest.com",
                            "first_seen": datetime.datetime.now(),
                            "ips_last_checked": datetime.datetime.now(),
                            "nslookup_rcode": 3,
                            "domain_dead_count": 1,
                            "is_primary": False,
                            "exclude_from_publication": False,
                            "nameserver_data": [
                                {
                                    "_id": "ns.domainiptest.com",
                                    "seen_first": datetime.datetime.now(),  # "seen_last" : datetime.datetime.now()
                                },
                                {
                                    "_id": "ns2.domainiptest.com",
                                    "seen_first": datetime.datetime.now(),  # "seen_last" : datetime.datetime.now()
                                }
                            ]
                        }]
        domip.libdwa.dwa_test_result(expectedDict)




        # Testing with 2nd Zone File    
        time.sleep(30)
        zoneFileTestData = runtime.data_path + """/DWAClient/test_dwa_client_process_zone_file_04_02"""

        domip.libdwa.zone_file_processor(zoneFileTestData)

        time.sleep(30)

        expectedDict = [{
                            "_id": "domainiptest.com",
                            "first_seen": datetime.datetime.now(),
                            "ips_last_checked": datetime.datetime.now(),
                            "nslookup_rcode": 3,
                            "domain_dead_count": 2,
                            "is_primary": False,
                            "exclude_from_publication": False,
                            "nameserver_data": [
                                {
                                    "_id": "ns.domainiptest.com",
                                    "seen_first": datetime.datetime.now(),  # "seen_last" : datetime.datetime.now()
                                },
                                {
                                    "_id": "ns2.domainiptest.com",
                                    "seen_first": datetime.datetime.now(),  # "seen_last" : datetime.datetime.now()
                                },
                                {
                                    "_id": "ns3.dominiptest.com",
                                    "seen_first": datetime.datetime.now(),  # "seen_last" : datetime.datetime.now()
                                },
                                {
                                    "_id": "ns4.domainiptest.com",
                                    "seen_first": datetime.datetime.now(),  # "seen_last" : datetime.datetime.now()
                                }
                            ]
                        }]
        domip.libdwa.dwa_test_result(expectedDict)

    def test_dwa_client_process_zone_file_05(self):
        """
           tcid : TS-851

        """

        domip.libdwa.check_dwa_environment()
        zoneFileTestData = runtime.data_path + """/DWAClient/test_dwa_client_process_zone_file_dead_count_05"""
        time.sleep(30)
        domip.libdwa.zone_file_processor(zoneFileTestData)
        time.sleep(30)
        expectedDict = [{
                            "_id": "7abi.bi",
                            "first_seen": datetime.datetime.now(),
                            "ips_last_checked": datetime.datetime.now(),
                            "nslookup_rcode": 4,
                            "domain_dead_count": 1,
                            "is_primary": False,
                            "exclude_from_publication": False,
                            "nameserver_data":
                                [{
                                     "_id": "ns1.dreamhost.com",
                                     "seen_first": datetime.datetime.now(),  # "seen_last" : datetime.datetime.now()
                                 },
                                 {
                                     "_id": "ns2.dreamhost.com",
                                     "seen_first": datetime.datetime.now(),  # "seen_last" : datetime.datetime.now()
                                 }]
                        }]

        domip.libdwa.dwa_test_result(expectedDict)