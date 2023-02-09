import runtime
import logging
from libx.process import ShellExecutor
from lib.db.mdbthreat import MongoWrapDOMIP
import lib.utils.serverstatus
from lib.exceptions import ValidationError, ProcessingError


def zone_file_processor(zonefile):
    _cmd = '/opt/sftools/bin/DWAActiveDNSQueueClient.sh  %s' % zonefile

    std_out, std_error = ShellExecutor.run_wait_standalone(_cmd)

    logging.debug("STD OUT OF DWAActiveDNSQueueClient : %s" % std_out)
    if 'Processing Domains' in std_out:
        logging.debug("DWAActiveDNSQueueClient.sh  has executed properly and submitted domains to DWA client.")
    else:
        logging.error("Problem in running DWAActiveDNSQueueClient.sh  script. Please check manually.")
        raise ProcessingError("Error in executing DWAActiveDNSQueueClient")
    if len(std_error) == 0:
        logging.error("Error in running DWAActiveDNSQueueClient.sh  : %s" % std_error)
        raise ProcessingError("Error in executing DWAActiveDNSQueueClient.sh ")
    return True


def check_dwa_environment():
    """
    Checks for DWA App Server and DWA Mongo DB
    """
    lib.utils.serverstatus.is_app_server_up(runtime.AppServer.host)
    lib.servers.is_mongodb_up()


def dwa_test_result(expectedData):
    """
    #todo:Raise ValidationError
    Usage : dwaTestResult(expectedData)
    expectedData is the list of data from DWA Client which will be compared with MongoDB
     """
    obj = MongoWrapDOMIP('domainz')
    for dataDict in expectedData:
        domainName = dataDict['_id']
        logging.info("Checking result for domain : %s " % (domainName))
        logging.debug("Expected data for %s domain = %s" % (domainName, dataDict))

        mongoDBDict = obj.dwa_fetch_all_domains(domainName)
        logging.debug("Data in mongoDB for domain - %s : %s" % (domainName, mongoDBDict))
        if len(mongoDBDict) == 1:
            logging.debug("MongoDB has got 1 record for the request which is as expected")
            result = comapre_dwa_mongo(dataDict, mongoDBDict[0])
        else:
            raise ValidationError("MongoDB has returned unexpected data for the domain")


def comapre_dwa_mongo(dataDict, mongoDBDict):
    """
    Usage : comapreDWA_withMongo(DWA_data, MongoDB_data)

    dataDict is the list of data from DWA Client
    mongoDBDict is the list of data from mongoDB

    Return :

    pass    :  If data in DWA_data & MongoDB_data is identical
    fail    :   if data in DWA_data & MongoDB_data is different.
    """
    # List of keys of domain data
    result = 'pass'
    domainMappingIds = list(dataDict.keys())
    domainName = dataDict['_id']

    if mongoDBDict is not None:
        for domainMappingId in domainMappingIds:
            if domainMappingId == "first_seen" or domainMappingId == "ips_last_changed" or domainMappingId == "ips_last_checked":
                if (dataDict[domainMappingId].date() == mongoDBDict[domainMappingId].date()):
                    logging.info("%s domain data for %s column is as expected" % (domainName, domainMappingId))
                else:
                    logging.error("For %s domain, %s column data is not as expected" % (domainName, domainMappingId))
                    result = 'fail'

            elif domainMappingId == "ip_data" or domainMappingId == "nameserver_data":
                if (len(dataDict[domainMappingId]) == len(mongoDBDict[domainMappingId])):
                    logging.debug("Comparing %s of %s domain " % (domainMappingId, domainName))
                    result = compare_data(domainName, dataDict[domainMappingId], mongoDBDict[domainMappingId])

                else:
                    logging.debug(
                        "%s length in expected Test case : %s" % (domainMappingId, len(dataDict[domainMappingId])))
                    logging.debug("%s length in mongoDB : %s" % (domainMappingId, len(mongoDBDict[domainMappingId])))
                    logging.error("For %s domain, %s column data is not as expected" % (domainName, domainMappingId))
                    result = 'fail'
            else:
                if dataDict[domainMappingId] == mongoDBDict[domainMappingId]:
                    logging.debug("%s in DWA client : %s" % (domainMappingId, dataDict[domainMappingId]))
                    logging.debug("%s in mongoDB : %s" % (domainMappingId, mongoDBDict[domainMappingId]))
                    logging.info("For %s domain, %s column data is in sync" % (domainName, domainMappingId))
                else:
                    logging.debug("%s in DWA client : %s" % (domainMappingId, dataDict[domainMappingId]))
                    logging.debug("%s in mongoDB : %s" % (domainMappingId, mongoDBDict[domainMappingId]))
                    logging.error("For %s domain, %s column data is not in sync" % (domainName, domainMappingId))
                    result = 'fail'


    else:

        logging.error("domain -  %s  - information is not present in mongoDB" % (domainName))
        result = 'fail'

    return result


def compare_data(domainName, DWA_data, MongoDB_data):
    """
        Usage : compare_Data(domainName, DWA_data, MongoDB_data)
        domainName is the name of the domain for which data is compared.
        DWA_data is the list of data from DWA Client
        MongoDB_data is the list of data from mongoDB

        Return :

        pass    :  If data in DWA_data & MongoDB_data is identical
        fail    :   if data in DWA_data & MongoDB_data is different.
    """
    result = 'pass'
    DWA_dataDict = {}
    for ipData in range(len(DWA_data)):
        DWA_dataDict[DWA_data[ipData]['_id']] = DWA_data[ipData]

    MongoDB_dataDict = {}
    for ipData in range(len(MongoDB_data)):
        MongoDB_dataDict[MongoDB_data[ipData]['_id']] = MongoDB_data[ipData]

    for key in list(DWA_dataDict.keys()):

        if key in list(MongoDB_dataDict.keys()):


            dataMappingIds = list(DWA_dataDict[key].keys())
            for dataMappingId in dataMappingIds:
                if dataMappingId == "seen_first" or dataMappingId == "seen_last" or dataMappingId == "active_last_seen":

                    logging.debug("DWAExpected data is %s" % (DWA_dataDict[key][dataMappingId]))
                    logging.debug("DWAExpected data is %s" % (MongoDB_dataDict[key][dataMappingId]))
                    time_diff = MongoDB_dataDict[key][dataMappingId] - DWA_dataDict[key][dataMappingId]
                    logging.info("%s and %s" % (MongoDB_dataDict[key][dataMappingId], DWA_dataDict[key][dataMappingId]))
                    # 18000 seconds is 5HRS which is the difference between UTC and CDT time zones
                    if time_diff.days <= 1 and time_diff.seconds <= 22000:
                        logging.info("For IP -> %s of domain %s  : data for %s column is as expected" % (
                            key, domainName, dataMappingId))
                    else:
                        logging.error("For IP -> %s of domain %s  : data for %s column is Not as expected" % (
                            key, domainName, dataMappingId))
                        result = 'fail'
                else:
                    if (DWA_dataDict[key][dataMappingId] == MongoDB_dataDict[key][dataMappingId]):
                        logging.info("For IP -> %s of domain %s  : data for %s column is as expected" % (
                            key, domainName, dataMappingId))
                    else:
                        logging.error("For IP -> %s of domain %s  : data for %s column is Not as expected" % (
                            key, domainName, dataMappingId))
                        result = 'fail'
        else:
            logging.error("Information of IP -> %s of %s is not present in mongoDB" % (key, domainName))
            result = 'fail'

    return result