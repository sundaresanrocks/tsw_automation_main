#!/usr/bin/env python
"""
---------------------------------------------------------
rest_reference_client.py

Copyright (C) 2017 McAfee, Inc. All rights reserved.

Code to send a request to a REST PSF server.
---------------------------------------------------------
"""

# System imports
from collections import namedtuple
import argparse
import base64
import ConfigParser
import hashlib
import hmac
import httplib
import os
import sys
import time
import logging
import pprint
from uuid import getnode
from random import randint
import json


DESCRIPTION = """
This script is used to send queries to the REST PSF Server.
The script is configured using values from the configuration.py script.
The Authorization header contains the HMAC code generated based on the request
body and is calculated based on the headers and query provided.

The query to be sent to the server is passed to this script on the command
line using the -q flag python rest_reference_client.py -q <query file>
"""

# The HTTP method used to send POST requests
POST_METHOD = "POST"

# Maximum size of request in bytes
MAX_REQ_SIZE = 16 * 1024

# Maximum number of queries per request
MAX_QUERY_COUNT = 5

# Headers is a tuple which contains the headers needed to send a request to the
# PSF server
# Refer to the Swagger documentation for how to set the values of these headers
Headers = namedtuple('Headers', ["Affid", "Authorization", "Cid", "Cliid",
                                 "Date", "Prn", "Pv", "Rid", "Ro"])

# These tuples are used to hold the configuration data parsed from the
# configuration.py file
Client = namedtuple('Client', ['client_id', 'password'])
Server = namedtuple('Server', ['address', 'path', 'use_https'])
AUTH_HEADER_DATA_FIELDS = ["affid", "cid", "prn", "pv"]
AuthorizationHeaderData = namedtuple('AuthorizationHeaderData',
                                     AUTH_HEADER_DATA_FIELDS)
# Tuple to define the response returned by the server. The values of these
# fields are defined in the Swagger documentation.
Response = namedtuple('Response', ["data", "headers", "reason", "status"])

# These constants are used in the config file to define the sections
CLIENT_SECTION = "client"
SERVER_SECTION = "server"
HEADER_SECTION = "header"


def calculate_authorization_header(authorization_header_data, date, cliid,
                                   rid, query_body, client):
    """ Calculate the required authorization header to send to the server from
        the input data. Requests without the correct authorization header will
        be rejected by the server.
        The result is the HMAC signature of the body and the following headers
        (prn, pv, rid, cliid, affid, cid, date)
    """
    canonical_str = \
        "affid: " + authorization_header_data.affid + "\n" + \
        "cid: " + authorization_header_data.cid + "\n" + \
        "cliid: " + cliid + "\n" + \
        "date: " + date + "\n" + \
        "prn: " + authorization_header_data.prn + "\n" + \
        "pv: " + authorization_header_data.pv + "\n" + \
        "rid: " + str(rid) + "\n" + \
        query_body

    hmac_code = base64.b64encode(hmac.new(client.password, canonical_str,
                                          digestmod=hashlib.sha1).digest())
    return 'CCS {0}:{1}'.format(client.client_id, hmac_code)


def build_headers(query_body, client, authorization_header_data):
    """ Create a Headers object with the values set for the headers
        required to send a REST request to a PSF server.
    """

    # Calculate Cliid
    mac = getnode()
    mac_str = ':'.join(("%012x" % mac)[i:i+2] for i in range(0, 12, 2))
    cliid = hashlib.md5(mac_str).hexdigest()

    # Calculate random request ID
    rid = randint(0, 9223372036854775807)

    # Get date in expected format
    os.environ['TZ'] = 'GMT'
    time.tzset()
    date = time.strftime("%a %b %d %H:%M:%S %Y")

    auth = calculate_authorization_header(authorization_header_data, date,
                                          cliid, rid, query_body, client)

    headers = Headers(Affid=authorization_header_data.affid,
                      Authorization=auth,
                      Cid=authorization_header_data.cid,
                      Cliid=cliid,
                      Date=date,
                      Prn=authorization_header_data.prn,
                      Pv=authorization_header_data.pv,
                      Rid=str(rid),
                      Ro=1)
    return headers


def send_http_request(server, body, headers):
    """ Send the http request to the server
    """
    if server.use_https == "True" or server.use_https == "true":
        logging.info('Sending the query over HTTPS...')
        conn = httplib.HTTPSConnection(server.address)
    else:
        logging.info('Sending the query over HTTP...')
        # pylint: disable=locally-disabled, redefined-variable-type
        conn = httplib.HTTPConnection(server.address)

    logging.debug(headers)
    logging.debug(body)
    headers_dict = headers._asdict()  # pylint: disable=W0212
    headers_dict["Content-Type"] = "application/json; charset=utf-8"

    conn.request(POST_METHOD, server.path, body, headers_dict)
    resp = conn.getresponse()

    data = resp.read()
    resp_headers = resp.getheaders()
    conn.close()

    response = Response(data, resp_headers, resp.reason, resp.status)
    return response


def validate_and_extract(config_parser, section, option):
    """ Checks the configuration file for the presence of the specified key.
        If present, then return the value
        If absent or set to None then raise an error
    """
    if config_parser.has_option(section, option):
        value = config_parser.get(section, option)
        if value is not None:
            return value
    raise ValueError("Configuration file is missing the required parameter `"
                     + section + ", " + option + "`")


def log_named_tuple(tuple_to_print):
    """ Prints given tuple in a nice way
    """
    msg = pprint.pformat(tuple_to_print)
    logging.info(msg)


def parse_client_configuration(config_parser):
    """ Parse the client configuration from the configuration file
        If a required configuration item is missing then log an error and
        raise an exception.
    """
    client = Client(
        validate_and_extract(config_parser, CLIENT_SECTION, 'client_id'),
        validate_and_extract(config_parser, CLIENT_SECTION, 'client_password'))
    log_named_tuple(client)
    return client


def parse_server_configuration(config_parser):
    """ Parse the server configuration for query requests
        If a required configuration item is missing then log an error and
        an exception.
    """
    server = Server(
        validate_and_extract(config_parser, SERVER_SECTION, 'server_address'),
        validate_and_extract(config_parser, SERVER_SECTION, 'query_path'),
        validate_and_extract(config_parser, SERVER_SECTION, 'use_https'))
    log_named_tuple(server)
    return server


def parse_auth_configuration(config_parser):
    """ Parse the authorization configuration for query requests
        If a required configuration item is missing then log an error and
        raise an exception.
    """
    authorization_header_data = AuthorizationHeaderData(
        validate_and_extract(config_parser, HEADER_SECTION, 'affid'),
        validate_and_extract(config_parser, HEADER_SECTION, 'cid'),
        validate_and_extract(config_parser, HEADER_SECTION, 'prn'),
        validate_and_extract(config_parser, HEADER_SECTION, 'pv'))
    log_named_tuple(authorization_header_data)
    return authorization_header_data


def read_from_query_file(query_file):
    """ Read the contents of the specified file and return it as a string. """
    try:
        with open(query_file) as fin:
            queries_str = fin.read()

    except IOError:
        # Handle errors such as file not existing. Here we just reraise the
        # exception and let the overall script fail.
        raise

    # Check number of queries in the file
    queries = json.loads(queries_str)
    if len(queries["q"]) > MAX_QUERY_COUNT:
        raise ValueError("Too many query entries")

    # Recreate the original request without any pretty printing
    queries_str = json.dumps(queries)

    # Check size of request
    if sys.getsizeof(queries_str) > MAX_REQ_SIZE:
        raise ValueError("Request is too big")

    return queries_str


def parse_configuration(config_parser):
    """ Parse the configuration for query requests
        If a required configuration item is missing then log an error and
        raise an exception.
    """
    client = parse_client_configuration(config_parser)
    server = parse_server_configuration(config_parser)
    authorization_header_data = parse_auth_configuration(config_parser)
    return client, server, authorization_header_data


def send_request(config_parser, build_headers_fn, body=""):
    """ Send the specified body text to the server and log the
        various stages of the operation.
    """
    logging.info("Parsing configuration...")
    client, server, authorization_header_data = \
        parse_configuration(config_parser)
    logging.info("")

    headers = build_headers_fn(body, client, authorization_header_data)
    return send_http_request(server, body, headers)


def configure_logger():
    """ Basic configuration of logger module with setting
        proper logging level
    """
    logging.basicConfig(filename='reference_client.log', level=logging.DEBUG)


def main():
    """ Main function responsible for parsing args and then executing the query
    """

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("-q", "--query_file",
                        required=True,
                        help="Contains the query to send to the server")
    parser.add_argument("-c", "--config",
                        required=False,
                        default="configuration.cfg",
                        help="Configuration file")
    parser.add_argument("-s", "--server",
                        required=False,
                        default=None,
                        help="The address of the server e.g. 127.0.0.1 "
                             "or myserver.mcafee.com")
    parser.add_argument("-p", "--path",
                        required=False,
                        default=None,
                        help="The query path on the server to send the "
                             "request to")

    args = parser.parse_args()

    body = read_from_query_file(args.query_file)

    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read(args.config)

    # Override server set in config file with server set on command line
    if args.server:
        config_parser.set(SERVER_SECTION, 'server_address', args.server)

    # Override query path set in config file with that set on command line
    if args.path:
        config_parser.set(SERVER_SECTION, 'query_path', args.path)

    response = send_request(config_parser, build_headers, body)

    logging.info("Received response...")
    log_named_tuple(response)
    print response.data

    # Print a large/noticeable warning if server was operating in safe mode
    if dict(response.headers)['aflag'] == '1':
        print "WARNING: SERVER IS IN SAFE MODE - RESULTS MAY NOT BE VALID"


if __name__ == "__main__":
    configure_logger()
    sys.exit(main())
