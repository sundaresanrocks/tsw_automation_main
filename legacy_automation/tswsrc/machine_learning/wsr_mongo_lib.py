#######################################
# Web Security Research Mongo Library #
# Copyright should go here            #
#######################################
# Imports
import pandas as pd
import wsr_main_lib
import dateutil.parser
from pymongo import MongoClient


# This needs to be updated with every release that is not backwards compatible.
__version__ = "1.2"

# Private internal variables
_mongo_handle = ""
_mongo_client = ""

# Load required feature mapping file.
feature_mapping = wsr_main_lib.load_feature_mapping(wsr_main_lib.FEATURE_MAP_RAW_TO_ML)


#######################################
# Create Mongo Client                 #
# Returns: Handle to mongo database
#######################################
def initialize_mongo_client(username, password, hostname, port):
    global _mongo_client, _mongo_conn
    # mongo_client = MongoClient('mongodb://hst-wsr-p-pxy01.scur.colo:4000/')
    _mongo_client = MongoClient("mongodb://" + hostname + ":" + port + "/")
    _mongo_conn = _mongo_client.urldb
    _mongo_conn.authenticate(username, password)
    return _mongo_conn


#######################################
# Cleanup Mongo Client                #
# Returns: Mongo Client
#######################################
def cleanup():
    global _mongo_client, _mongo_conn
    _mongo_conn.logout()
    _mongo_client.close()


#######################################
# Extract Records from Mongo
# start_date_str    ex: "2017-11-05T00:00:00.000Z"
# end_date_str      ex: "2017-11-05T01:00:00.000Z"
# source            Source name ex: "TelemetryProcessorWorkflow"
# limit             Number of items to return.  Default is 100
# Returns           data frame
# NOTE: This flattens out mongo name/value pairs.
#######################################
def extract_records_to_df(mongo_handle, start_date_str, end_date_str, source="TelemetryProcessorWorkflow", limit=100):
    # Convert Dates to String
    start_date = dateutil.parser.parse(start_date_str)
    end_date = dateutil.parser.parse(end_date_str)
    # Need to tie together the last seen with the actual telemetry record.
    df = pd.DataFrame()

    query = dict()
    query['source'] = source
    query['lastSeen'] = {'$gt': start_date, '$lt' : end_date}

    # ''"{\"source\" : " + source + ", \"lastSeen\" : {\"$gt\": " + str(start_date) +
    # ", \"$lt\": " + str(end_date) + "} }"
    record_list = extract_records_to_list(mongo_handle, query, limit)
    # Create data frame
    df = pd.DataFrame.from_dict(record_list)
    return df


#######################################
# Extract Records from Mongo
# query             Query to run
# limit             Number of items to return.  Default is 100
# Returns           data frame
# NOTE: This flattens out mongo name/value pairs.
#######################################
def extract_records_to_list(mongo_handle, query, limit=100):
    # Example queries:
    # {"source":"TelemetryProcessorWorkflow","urlHash":"0X407c26915b7ebf04615aa85b"}

    # Results
    record_list = []
    for record in mongo_handle.workflow_event.find(query).limit(limit):

        # TODO Figure out how to properly encode these.
        if '{' in str(record['url']):
            print ('warning URL contains { invalid character ' + record['url'])
            continue
        if '}' in str(record['url']):
            print ('warning URL contains } invalid character ' + record['url'])
            continue

        metadata_list = record.get("metadata")
        # Replace fact name from UrlDB with mapped feature name
        # Eg. alexaRanking -> tsAlexaRanking
        for metadata in metadata_list:
            key = metadata["name"]
            # jn:added to avoid adding extra columns with &
            if '&' in key:
                print ('warning the key contains & invalid character ' + record['url'] + ' ' + key) 
                continue
            if 'mlpFailure' == metadata["value"]:
                print ('warning URL contains mlpExitStatus=mlpFailure ' + record['url'])
                continue
            mappedkey = feature_mapping[key] if key in feature_mapping else key
            record[mappedkey] = metadata["value"]
        # Remove fields, if exists.
        record.pop("metadata", None)
        record.pop("label", None)
        record.pop("labelConfidence", None)
        # Fix mapping of fields out of metadata
        for key in record:
            mappedkey = feature_mapping[key] if key in feature_mapping else key
            record[mappedkey] = record[key]
            if key != mappedkey:
                record.pop(key, None)
        # pp = pprint.PrettyPrinter(depth=6)
        # pp.pprint (record)
        
        record_list.append(record)
    
    return record_list


# TODO Do I need this?
# extract URLDB records to DF without mapping fact to ML names
def extract_records_to_df_nomapping(mongo_handle, start_date_str, end_date_str, source="TelemetryProcessorWorkflow", limit=100):
    # Convert Dates to String
    start_date = dateutil.parser.parse(start_date_str) 
    end_date = dateutil.parser.parse(end_date_str) 

    # Need to tie together the last seen with the actual telemtry record.
    df = pd.DataFrame()
    record_list = []
    for record in mongo_handle.workflow_event.find({"source" : source, "lastSeen" : {"$gt": start_date, "$lt": end_date} } ).limit(limit): 
        metadata_list = record.get("metadata")
        for metadata in metadata_list: 
            record[metadata["name"]] = metadata["value"]
        # Remove fields, if exists.
        record.pop("metadata", None)
        record.pop("label", None)
        record.pop("labelConfidence", None)
        # pp = pprint.PrettyPrinter(depth=6)
        # pp.pprint (record)
        
        record_list.append(record)
    
    # Create data frame
    df = pd.DataFrame.from_dict(record_list)

    return df      
