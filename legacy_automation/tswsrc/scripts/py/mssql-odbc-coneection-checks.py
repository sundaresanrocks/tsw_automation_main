"""
Simple script to check if databases can be connected via odbc/freetds driver
"""

import sys
import os
import logging
import runtime
logging.getLogger().setLevel(logging.INFO)

__author__ = 'manoj'

if __name__ == '__main__':

    HOST = runtime._ini_section
    errors = []

    logging.info('Checking connectivity to databases via odbc/freetds driver')
    ssh_obj = runtime.get_ssh(HOST['localhost'], 'root')
    ssh_obj.ts_odbc_setup(HOST['mssqldb_u2'] + '_U2', HOST['mssqldb_d2'] + '_D2', HOST['mssqldb_r2'] + '_R2')
    ssh_obj.ts_check_odbc_setup(HOST['mssqldb_u2'] + '_U2', HOST['mssqldb_d2'] + '_D2', HOST['mssqldb_r2'] + '_R2')

