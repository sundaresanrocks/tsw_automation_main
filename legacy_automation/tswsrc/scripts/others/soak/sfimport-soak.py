__author__ = 'abhijeet'

import argparse
from path import Path
from lib.sfimport import sfimport
from urllib.parse import urlparse
from datetime import datetime
from lib.db.mssql import TsMsSqlWrap
import random
import time
import os

def get_new_in_file(url_file):
    soak_file_path = Path('sfimport-soak-files')
    if not soak_file_path.exists():
        soak_file_path.makedirs()
    in_file_path = soak_file_path.joinpath('sfimport-in%s'%datetime.now().strftime('%Y%m%dT%H%M%S'))
    with open(in_file_path, 'w') as in_file:
        with open(url_file.abspath(), 'r') as url_sample:
            for ustring in url_sample:
                if ustring.startswith('*://'):
                    ustring = ustring.replace('*', 'http', 1)
                parsed_ustring = urlparse(ustring)
                if not parsed_ustring.scheme:
                    continue #invalid url; skip from writing to file
                nustring = parsed_ustring.geturl().replace('.', '%s.'%datetime.now().strftime('%Y%m%dT%H%M%S'), 1)
                in_file.write(urlparse(nustring).geturl())
    return in_file_path


def get_random_category(categories_list):
    return random.choice(categories_list)


def get_all_categories():
    u2_obj = TsMsSqlWrap('U2')
    sql = 'select cat_short from cat_definition with (nolock)'
    sql_res = u2_obj.get_select_data(sql)
    categories_list = list()
    for record in sql_res:
        categories_list.append(record['cat_short'])
    return categories_list


def run_soak_sfimport(sleeptime, url_file):
    sfimport_obj = sfimport()
    categories_list = get_all_categories()
    try:
        while True:
            in_file = get_new_in_file(url_file)
            category = get_random_category(categories_list)
            try:
                sfimport_obj.append_category(in_file, category)
            except AttributeError:
                pass #ignore sfimport errors
            time.sleep(sleeptime)
    except KeyboardInterrupt:
        print('Detected keyboard interrupt. Exiting.')
        exit(0)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('sleeptime', help='Number of seconds to sleep between each sfimport cycle', type=int)
    arg_parser.add_argument('url_file', help='Path to url file with sample urls', type=str)
    args = arg_parser.parse_args()
    sleeptime = args.sleeptime
    url_file = Path(args.url_file)
    if not url_file.exists():
        print('url file path does not exist')
    elif not url_file.isfile():
        print('url file path provided does not point to a file')
    else:
        run_soak_sfimport(sleeptime, url_file)
