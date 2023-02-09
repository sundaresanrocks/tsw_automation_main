"""
==============================
Competitor Analysis Query URLs
==============================

Command line tool to query urls for competitor analysis
"""
import argparse
import datetime
import logging
import os
import pprint

__author__ = 'manoj'

start_time = datetime.datetime.now()
from ca.processors.canonicalizer import get_canon_url, CanonicalizerError
from ca.processors.mongoresults import CompetitorMongoDoc


def query_urls(urls):
    """

    :param urls:
    :return:
    """
    for url in urls:
        logging.info('Querying URL: %s' % url)
        try:
            url_sha_256 = get_canon_url(url)['sha256']
        except CanonicalizerError as err:
            logging.error('CanonicalizerError for URL: %s - %s' % (url, err.args[0]))
            continue
        doc = CompetitorMongoDoc().get_url_by_id(url_sha_256)
        print(pprint.pformat(doc))


def main():

    urls = []
    parser = argparse.ArgumentParser(description='Competitor Analysis Queue URLs utility.')
    parser.add_argument('--url',
                        help="""Query a single URL""",
                        dest='url')
    parser.add_argument('--txt',
                        help="""Query list of URLs from text file""",
                        dest='file')
    opts = parser.parse_args()

    if not opts.url or opts.file:
        parser.print_help()

    if opts.file:
        if not os.path.isfile(opts.file):
            logging.error('FileNotFoundError - %s' % opts.file)
            raise FileNotFoundError(opts.file)

        urls = [line.strip() for line in open(opts.file).readlines() if not line.strip().startswith('#')]

    if opts.url:
        urls.append(opts.url.strip())

    if not urls:
        logging.error('Zero URLs!')
        os._exit(1)

    query_urls(urls)


if __name__ == '__main__':
    try:
        main()
    finally:
        logging.info('time taken: %s seconds' % (datetime.datetime.now() - start_time).seconds)
    exit(0)
