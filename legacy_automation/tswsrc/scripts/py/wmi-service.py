import argparse
import datetime
import logging

__author__ = 'manoj'

from libx.csvwrap import load_and_parse_csv_as_dict
SUPPORTED_ACTIONS = ['start', 'stop', 'restart']


def manage_service(service_name, action):
    if not isinstance(service_name, str):
        raise TypeError('name must be type str. found: %s' % type(service_name))
    if not action.lower() in SUPPORTED_ACTIONS:
        raise ValueError('Action must be one of %s' % SUPPORTED_ACTIONS)



def main():
    parser = argparse.ArgumentParser(description='Remote service restart.')
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-csv',
                       help="""CSV File input""",
                       dest='csv_file_name',
                       action='store', )
    group.add_argument('-text',
                       help="""Text file input""",
                       dest='text_file_name',
                       action='store', )
    group.add_argument('-h',
                       help="""Comma separated list of hosts""",
                       dest='hosts_list',
                       action='store', )
    parser.add_argument('-s',
                       help="""Comma separated list of service names""",
                       dest='service_list',
                       action='store', )
    parser.add_argument('-action',
                       help="""Action - start or stop or restart""",
                       dest='service_action',
                       action='store', )
    # parser.add_argument('input_file',
    #                     help='Text input file with list of urls', )
    parser.add_argument('-e', '--email',
                        help="""Email recipient""",
                        dest='email',
                        action='store', )
    parser.add_argument('-t', '--threads',
                        help="""No of threads 0 < t < 512. Default 10""",
                        dest='threads',
                        action='store',
                        type=int)

    opts = parser.parse_args()
    errors_list = []
    print(opts)


    if opts.threads:
        threads = int(opts.threads)
    else:
        threads = 10
        logging.warning('Default of threads = %s' % threads)
    if threads < 1 or threads > 512:
        logging.error('Enter number of threads via -t ')
        exit(10)

    if opts.csv_file_name:
        if opts.service_list:
            errors_list.append('Service name must not be present for csv file format')
        if opts.service_action:
            errors_list.append('Service action must not be present for csv file format')

    if opts.txt_file_name:
        if not opts.service_list:
            errors_list.append('Service name is missing for txt file format(required option)')
        if not opts.service_action:
            errors_list.append('Service action is missing for txt file format(required option)')

    if opts.hosts_list:
        if not opts.service_list:
            errors_list.append('Service name is missing for host option')
        if not opts.service_action:
            errors_list.append('Service action is missing for host option')




manage_service(None, 'StarT')

if __name__ == '__main__':

    start_time = datetime.datetime.now()
    try:
        main()
    finally:
        logging.info('time taken: %s seconds' % (datetime.datetime.now() - start_time).seconds)
    exit(0)

