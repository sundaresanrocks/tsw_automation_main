"""
==============================
Competitor Analysis Queue URLs
==============================

Command line tool to queue urls for competitor analysis
"""
import argparse
import datetime
import logging
import os
import importlib

__author__ = 'manoj'

from ca.clients import CompetitorNotFound
from ca.ca_config import SUPPORTED_TASKS
start_time = datetime.datetime.now()
from celery import Celery
from ca.ca_config import RABBITMQ_BROKER, RABBITMQ_BACKEND
cel_queue = Celery(backend=RABBITMQ_BACKEND, broker=RABBITMQ_BROKER)


def queue_urls(competitors, urls):
    """

    :param competitors:
    :param urls:
    :return:
    """
    if isinstance(urls, str):
        urls = [urls]
    error_competitor_names = [client for client in competitors if client not in SUPPORTED_TASKS]
    if error_competitor_names:
        logging.error('Competitor not supported: %s' % error_competitor_names)
        raise CompetitorNotFound(error_competitor_names)
    for competitor in competitors:
        cel_queue.send_task(SUPPORTED_TASKS[competitor], [urls], queue=competitor)


def main():

    urls = []
    parser = argparse.ArgumentParser(description='Competitor Analysis Queue URLs utility.')
    parser.add_argument('--url',
                        help="""Queue a single URL""",
                        dest='url')
    parser.add_argument('--txt',
                        help="""Queue list of URLs from text file""",
                        dest='file')
    parser.add_argument('-c', '--competitor-list',
                        help="""Comma separate list of Competitors. - %s""" % ','.join(SUPPORTED_TASKS),
                        dest='competitors',
                        action='store')
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

    if not opts.competitors:
        competitors = [client for client in SUPPORTED_TASKS]
    else:
        competitors = [client for client in opts.competitors.split(',') if client.strip()]

    if not urls:
        logging.error('Zero URLs to be queues!')
        os._exit(1)

    if not competitors:
        logging.error('Zero Competitors provided!')
        os._exit(1)

    try:
        queue_urls(competitors, urls)
    except CompetitorNotFound:
        os._exit(1)


if __name__ == '__main__':
    try:
        main()
    finally:
        logging.info('time taken: %s seconds' % (datetime.datetime.now() - start_time).seconds)
    exit(0)
