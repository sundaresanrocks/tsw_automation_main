import time
import logging

from framework.test import SandboxedTest
from lib.db.mongowrap import MongoWrap
from libx.vm import get_snapshot_wrapper
from lib.db.railmigration import RailMig
from lib.sfimport import sfimport
from dbtools.agents import Agents
from lib.exceptions import TestFailure
from lib.build import Build
from domip.expectPubData import TestDataBP
from libx.utils import DictDiffer
import runtime
from domip.expectPubData import TestDataBPFunctional


class CallAgents:
    def call_all_agents(self):
        #   Call TMAN Agent

        tman_obj = Agents('tman')
        tman_obj.run_agent(" -l 50 -n 2 -d -i -s ")

        # Call WRUA Agent

        wrua_obj = Agents('wrua')
        wrua_obj.run_agent("-n 50 -t 2 ")

        # Call WRMAN Agent

        wrman_obj = Agents('wrman')
        wrman_obj.run_agent(" -n 50 -t 2 ")

        # Call CBMAN Agent

        cbman_obj = Agents('cbman')
        cbman_obj.run_agent("-n 50 -t 2 ")

        #  Call NRUA Agent

        nrua_obj = Agents('nrua')
        nrua_obj.run_agent("-n 50 -t 2 ")

        # Call CRUA Agent

        crua_obj = Agents('crua')
        crua_obj.run_agent(" -n 50 -t 2 ")

        # Call WRMAN Agent

        wrman_obj.run_agent(" -n 50 -t 2 ")

        #   Call  CRUA

        crua_obj.run_agent(" -n 50 -t 2 ")


class DIBPTests(SandboxedTest):
    """
    DIBP : Domain IP Build Publication
    """

    @classmethod
    def setUpClass(self):
        # Delete all the data from mongoDB 
        mwrap = MongoWrap(runtime.BuildPublicationMongoDB.table)
        mwrap.delete_all_data_in_collection()

        ##   Revert the VM image of minimal DB (MS SQL DB)

        #DB_vm_warp = get_snapshot_wrapper(envcon.Vcenter.minimal_DB_vm)
        #DB_vm_warp.revert(envcon.Vcenter.minimal_DB_vm_snap)

        DB_vm_warp = get_snapshot_wrapper(runtime.DB.vm_name)
        DB_vm_warp.revert(runtime.DB.vm_snap)

        ## Update Minimal DB with latest schema changes

        call_rail = RailMig()

        call_rail.update_MSSQL_DB()


        ##  Checking Minimal DB Setting in localhost
        runtime.get_ssh('localhost', 'root').ts_check_odbc_setup(runtime.DB.U2_name, runtime.DB.D2_name, runtime.DB.R2_name)


        ##   Reset Build System image
        build_vm_warp = get_snapshot_wrapper(runtime.BuildSys.vm_name)
        build_vm_warp.revert(runtime.BuildSys.vm_snap)

        #  Remove urls files from /usr2/smartfilter/build/publication_history.

        build_clean = Build()
        build_clean.clean_pub_history()

        ####  Temporary function

        build_clean.copy_build_script()





        ######################   Setup Complete   ##########################
        pass


    def test_01(self):
        """
        This test case is to test the entire flow of build and Url pub history

        TS-1204:End to end test for URL Publication history


        """

        # call sfimport for URLs :

        urls = ["*://BUILDTEST1.COM", "HTTPS://BUILDTEST1.COM", "*://BUILDTEST1.COM/1.html"]
        cat = """ms"""
        obj = sfimport()
        sfimportResult = obj.append_category(urls, cat)

        if not (sfimportResult["Total_Successful"] == len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (
                    sfimportResult["Total_Errors"] == 0):
            raise TestFailure

        #  Run all agents

        exe_agents = CallAgents()
        exe_agents.call_all_agents()


        #   Calling build process

        build_obj = Build()
        time.sleep(300)
        build_obj.build_run('migt', 'ts')

        while int(build_obj.is_running_URLHistoryLoader()) == 1:
            time.sleep(5)

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBP.test01_expected(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")

            #def test_02(self):
            #    ''' This is test 2'''
            #
            #    # call sfimport for URLs :
            #
            #    urls = ["*://BUILDTEST1.COM", "HTTPS://BUILDTEST1.COM", "*://BUILDTEST1.COM/1.html" ]
            #    cat = """ms"""
            #    #obj=sfimport()
            #    #sfimportResult = obj.append_category(urls,cat)
            #    #
            #    #if not (sfimportResult["Total_Successful"]== len(urls)) and (sfimportResult["Total_Canon_Errors"] == 0) and (sfimportResult["Total_Errors"] == 0):
            #    #    raise TestFailure
            #    #
            #    ##  Run all agents
            #    #
            #    #exe_agents = CallAgents()
            #    #exe_agents.call_all_agents()
            #    #
            #    #
            #    ##   Calling build process
            #    #
            #    #build_obj = Build()
            #    #
            #    #build_obj.build_run('migt', 'ts')
            #    #
            #    #while build_obj.is_running_URLHistoryLoader() == "1":
            #    #    time.sleep(5)
            #    #
            #    #if build_obj.BP_working_file_count() != "0" :
            #    #
            #    pub_mongo = MongoWrap('publication_history')
            #    for url in urls:
            #        expected_data = TestDataBP.test02_expected(url)
            #        print("expected_data :  %s"%(expected_data))
            #        print("Type of expected data : %s" %(type(expected_data)))
            #
            #        logging.debug("expected_data: %s"%(expected_data))
            #        logging.debug("Type of expected data : %s" %(type(expected_data)))
            #
            #        mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }"""%({'url' : url}))
            #
            #        print("mongoDB query result %s"%(mongo_data))
            #        print("Type of mongoDB query result : %s" %(type(mongo_data)))
            #
            #        logging.debug("mongoData %s"%(mongo_data))
            #        logging.debug("Type of mongoData : %s" %(type(mongo_data)))
            #        diff = DictDiffer(expected_data, mongo_data)
            #        print diff.partial_match()
            #        if not diff.partial_match():
            #            raise AssertionError('TEST FAIL:')
            #
            #    #else:
            #    #
            #    #    logging.error("/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            #    #    raise Exception("Not working: Check manually")            #    #
            #
            #
            #


class DIBPFunctionalTests(SandboxedTest):
    """
    DIBP : Domain IP Build Publication
    """

    @classmethod
    def setUpClass(self):
        # Delete all the data from mongoDB 
        mwrap = MongoWrap(runtime.BuildPublicationMongoDB.table)
        mwrap.delete_all_data_in_collection()


        ######################   Setup Complete   ##########################
        pass

    def setUp(self):

        SandboxedTest.setUp(self)

        bp_clean = Build()

        bp_clean.clean_pub_history()


    def test_01(self):
        """ This is test 1"""

        # call sfimport for URLs :
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test1.gz"""

        # copy the URL migt file to publication history folder
        urls = ["*://BUILDTEST1.COM", "HTTPS://BUILDTEST1.COM", "*://BUILDTEST1.COM/1.html"]

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test1.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test01_expected(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")

    def test_02(self):
        """
            This is test 2

            extra special charector - test case ID  TS-1027
        """

        # call sfimport for URLs :
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test2.gz"""

        # copy the URL migt file to publication history folder
        urls = ["*://TECNICASMENTALES.COM/el-cuadrante-de-flujo-de-dinero.htm", "*://0-PORNOGRAPHY.COM"]

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test2.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test02_expected(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")

    def test_03(self):
        """
            This is test 3
            url with curly braces - test case ID TS-1028
        """

        # call sfimport for URLs :
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test3.gz"""

        # copy the URL migt file to publication history folder
        urls = ["*://96.47.69.60?&gid&oid&aid={adcenterid}&yid={yahooid}"]

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test3.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test03_expected(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")

    def test_04(self):
        """
            This is test 4
            Update reputatiopn - test case ID  TS-1030
        """

        # call sfimport for URLs :
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test4.gz"""

        # copy the URL migt file to publication history folder
        urls = ["*://CHARIOTS-OF-FIRE.COM", "*://CASHMEL.COM", "*://DEKASTAAN.NL"]

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test4.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test04_expected(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")

    def test_05(self):
        """
            This is test 5
            Add/changecategory -test case ID TS-1032

        """

        # call sfimport for URLs :
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test5.gz"""

        # copy the URL migt file to publication history folder
        urls = ["*://199.59.149.230/McAfee", "*://199.59.150.7/McAfee"]

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test5.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test05_expected(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")
    def test_06(self):
        """
            This is test 6
            Uncat Test -test case TS-1033

        """

        # call sfimport for URLs :
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test6.gz"""

        # copy the URL migt file to publication history folder
        urls = ["*://HANDRITE.COM", "*://TAP2.NL", "*://POTOPON.COM"]

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test6.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test06_expected(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")

    def test_07(self):
        """
            This is test 7
            FTP url test -test case  TS-1203

        """

        # call sfimport for URLs :
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test7.gz"""

        # copy the URL migt file to publication history folder
        urls = ["FTP://AGEOCITIES.COM", "FTP://PAPTEST8.COM/path"]

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test7.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test07_expected(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")

    def test_08(self):
        """
           This is test 8
           HTTPS url test  TS-1202

        """

        # call sfimport for URLs :
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test8.gz"""

        # copy the URL migt file to publication history folder
        urls = ["HTTPS://PAPTEST11.COM", "HTTPS://PAPTEST11.COM:8080"]

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test8.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test08_expected(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")

    def test_09(self):
        """
            This is test 9
           	Domains with IPv4 ips check  TS-1035

        """

        # call sfimport for URLs :
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test9.gz"""

        # copy the URL migt file to publication history folder
        urls = ["*://200.55.198.67", "*://64.12.79.57/klcartao", "*://212.219.56.133/sites/ftp.simtel.net"]

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test9.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test09_expected(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")

    def test_10(self):
        """
            This is test 10
           	IPv6 domain name with HTTP   TS-1034

        """

        # call sfimport for URLs :
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test10.gz"""

        # copy the URL migt file to publication history folder
        urls = ["http://[3ffe:1900:4545:3:200:f8ff:fe21:67cf]:80/index.html"]

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test10.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test10_expected(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")

    def test_11(self):
        """
            This is test 11
           	IPv6 domain name with FTP -  TS-1205

        """

        # call sfimport for URLs :
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test11.gz"""

        # copy the URL migt file to publication history folder
        urls = ["ftp://[3ffe:1900:4545:3:200:f8ff:fe21:67cf]:80/index.html"]

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test11.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test11_expected(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")

    def test_12(self):
        """
            This is test 12
           	IPv6 domain name with HTTPS - TS-1206

        """

        # call sfimport for URLs :
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test12.gz"""

        # copy the URL migt file to publication history folder
        urls = ["https://[3ffe:1900:4545:3:200:f8ff:fe21:67cf]:80/index.html"]

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test12.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test12_expected(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")

    def test_13(self):
        """ This is test 13
             to test delete category history is updated in mongo TS-1029
        """

        # call sfimport for URLs :
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test13_1.gz"""

        # copy the URL migt file to publication history folder
        urls = ["*://BUILDTEST13.COM"]

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test13_1.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test13_expected_1(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test13_2.gz"""

        # copy the URL migt file to publication history folder

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test13_2.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test13_expected_2(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")

    def test_14(self):
        """ This is test 14
            to test delete category web reputation is updated in mongo   TS-1031
        """

        # call sfimport for URLs :
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test14_1.gz"""

        # copy the URL migt file to publication history folder
        urls = ["*://BUILDTEST14.COM"]

        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test14_1.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test14_expected_1(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")
        URLHistoryTestData = runtime.data_path + """/build_publication/urls_migt.test14_2.gz"""

        # copy the URL migt file to publication history folder


        bp_ssh = runtime.get_ssh(runtime.BuildSys.system, runtime.BuildSys.user)
        bp_ssh.put(URLHistoryTestData, runtime.BuildSys.BP_dir + '/urls_migt.test14_2.gz')

        build_obj = Build()
        build_obj.run_URLHistoryLoader()

        if int(build_obj.BP_working_file_count()) == 0:

            for url in urls:
                expected_data = TestDataBPFunctional.test14_expected_2(url)
                print(("expected_data :  %s" % (expected_data)))
                print(("Type of expected data : %s" % (type(expected_data))))

                logging.debug("expected_data: %s" % (expected_data))
                logging.debug("Type of expected data : %s" % (type(expected_data)))

                pub_mongo = MongoWrap('publication_history')
                mongo_data = pub_mongo.query_one("""{"url" : "%(url)s" }""" % ({'url': url}))

                print(("mongoDB query result %s" % (mongo_data)))
                print(("Type of mongoDB query result : %s" % (type(mongo_data))))

                logging.debug("mongoData %s" % (mongo_data))
                logging.debug("Type of mongoData : %s" % (type(mongo_data)))
                diff = DictDiffer(expected_data, mongo_data)
                print((diff.partial_match()))
                if not diff.partial_match():
                    raise AssertionError('TEST FAIL:')


        else:

            logging.error(
                "/usr2/smartfilter/build/publication_history/working/ directory is not empty. Please check Manually")
            raise Exception("Not working: Check manually")    

            