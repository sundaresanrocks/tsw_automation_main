################################################################################
# wsr_main_lib.py
#
# Library of common routines found in the python code.
#
# @author jwagener
# @version $Id$
# Copyright 2018 McAfee, Inc.
################################################################################
import os
import sys
import logging
import logging.handlers as handlers
import pandas as pd
import ujson as json
import time

# Module version.  Increment this when changes are make that
# makes this module backwards incompatible.
__version__ = "1.2"

######################
# Global Defines
######################
# Maps raw workflow data to ML feature names (until wagener un-does the mapping)
FEATURE_MAP_RAW_TO_ML = "mlfeaturemapping.properties"
FEATURE_MAP_RAW_TO_SQL = "../../../../../human_in_loop/sources/MLWebTool/src/main/resources/hitl_data_loader/workflow-hitl-mapping.properties"


######################
# add_module_path
# Adds a path to the python classpath
# Input: Path to add
# Output: Nothing
######################
def add_module_path(new_path):
    sys.path.append(os.path.abspath(new_path))


######################
# initialize_logging
# Setup logging for all modules.  This is automatically called at the end of this script.
# Anyone importing this library will get loggins setup.
# Note: use "log" variable, not "logger".
# Input: Nothing
# Output: Log Handle
######################
def initialize_logging():
    # Default log level ins INFO.
    log_level = logging.getLevelName(logging.INFO)
    FORMAT = '%(asctime)s %(levelname)-8s (%(threadName)-10s) %(message)s'
    logging.basicConfig(level=log_level, format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
    # Add syslog formatting for splunk
    syslog_handler = handlers.SysLogHandler(address='/dev/log')
    syslog_handler.setFormatter(logging.Formatter(FORMAT))
    logging.getLogger().addHandler(syslog_handler)
    return logging

######################
# get_module_version_information
# Dump out all the module versions python has installed.
# Input: Nothing
# Output: List of all packages installed.  One per line.
######################
def get_module_version_information():
    result = "-- Module Versions --------------------------------------------------\n"
    for name, module in sorted(sys.modules.items()):
        if hasattr(module, '__version__'):
            result = result + name + "=" + str(module.__version__) + "\n"
    result = result + "/////////////////////////////////////////////////////////////////////"
    return result


######################
# load_feature_mapping
# Load mappping file to convert feature names.
# Input: Mapping filename
# Output: Dictionary that can be used for mapping
######################
def load_feature_mapping(filepath):
    results = {}
    with open(filepath) as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) <= 0 or line[0] == "#":
                continue
            k, v = line.split("=")
            results[k] = v
    return results


######################
# unmap
# Swaps key an value paris.
# NOTE: This can be an issue if there is more than one value in the dictionary.
# Input: Dictionary to unmap.
# Output: New dictionary where the value is now the key.
######################
def unmap(dictionary):
    return (dict([[v, k] for k, v in dictionary.items()]))


######################
# write_df_to_json_file
# Read a Json file to a DF
# Input: Json file location
# Output: DataFrame
######################
def write_df_to_json_file(df, outfile):
    try:
        df.to_json(outfile, orient='records', lines=True, default_handler=str)
    except:
        log.error("Error processing dataframe=" + str(df) + " to filename=" + outfile)
        raise


######################
# write_df_to_json_file
# Write a pandas dataframe to a file.
# Input: dataframe and filename to write to.
# Output: Nothing
######################
def write_str_to_json_file(data, outfile):
    try:
        json.dump(data)
    except:
        log.error("Error processing dataframe=" + str(df) + " to filename=" + outfile)
        raise


######################
# read_json_to_df
# Write a pandas dataframe to a file.
# Input: dataframe and filename to write to.
# Output: Nothing
######################
def read_json_to_df(infile):
    sys.setdefaultencoding("ISO-8859-1")
    df = pd.DataFrame.empty
    try:
        pd.concat([pd.Series(json.loads(line)) for line in open(infile, encoding="utf8")], axis=1)
        df = df.transpose()
    except IOError as err:
        log.error("Error processing file=" + str(df) + " to filename=" + infile, err)
        raise
    return df



######################
# read_json_to_dict
# Read a JSON file to a dictionary.
# Input: Filename to read
# Output: dictionary
# Throws an exception if there is an error.
######################
def read_json_to_dict(filename):
    try:
        with open(filename) as f:
            return json.load(f)
    except:
        log.error("Error processing filename=" + filename)
        raise


######################
# read_json_to_df
# Read a JSON file to a pandas Dataframe.
# Input: Filename to read
# Output: Pandas Dataframe
######################
def read_json_to_df(filename):
    df = pd.DataFrame()
    try:
        df = pd.DataFrame()
        with open(filename) as f:
            df = pd.DataFrame(json.loads(line) for line in f)
    except:
        log.error("Error processing filename=" + filename)
        raise

    log.info("Dataframe shape=" + str(df.shape))

    return df
    # This is too slow but handles errors in JSON...
    #
    # Needs investigation on how to do it faster.
    # with open(extracted_from_urldb_filename) as f:
    #    counter = 0
    #    for line in f:
    #        try:
    #            counter = counter + 1
    #            if (counter % 1000 == 0):
    #                log.info("Read in counter=" + str(counter) + " lines.")
    #            data = json.loads(line)
    #        except ValueError as e:
    #            log.error('line=" + counter + " Cound not parse records for line=' + line)
    #            continue
    #            # Why [] - is this causing our issue with indexing
    #        newDF = pd.DataFrame.from_dict([data])
    #        df = df.append(newDF)
    # Reindex
    # Use this if we restructure the dataframe, or the indexes get off.
    # df = df.reset_index(drop=True)


######################
# time_fn
# Time how long a function takes
# Input: function to time, arguments to function, keyword arguments.
# Output: Time it took for function to run.
######################
def time_fn(fn, *args, **kwargs):
    start = time.time()
    results = fn(*args, **kwargs)
    end = time.time()
    fn_name = fn.__module__ + "." + fn.__name__
    print (fn_name + ": " + str(end - start) + "s")
    return results


######################
# get_logger
# Return the global logger.  Each program that needs a logger should call
# this method to get the common logger.
# Input: Nothing
# Output: Global logger
######################
def get_logger():
    global log
    return log


# Start logger
log = initialize_logging()
