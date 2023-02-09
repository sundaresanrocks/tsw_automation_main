import logging

__author__ = 'manoj'

import os
import time
from celery import Celery
from ca.clients.base import ChromeExtensionBase
from ca.clients.sdkclient import get_sdk_client_url_data
from ca.ca_config import RABBITMQ_BROKER, RABBITMQ_BACKEND, TEXT_GRAY, TEXT_GREEN, TEXT_RED, TEXT_YELLOW
from ca.ca_config import RESULTS_QUEUE, RESULTS_TASK, SUPPORTED_TASKS


module_name = os.path.basename(__file__).partition('.')[0]
task_name = SUPPORTED_TASKS['sdkclient']
app = Celery(task_name, backend=RABBITMQ_BACKEND, broker=RABBITMQ_BROKER, queue='sdkclient')


def lookup(url):
    #### importing here to avoid cyclic imports!
    from ca.clients import SUPPORTED_CLIENTS

    result = None
    for i in range(3):
        result = get_sdk_client_url_data(url, SUPPORTED_CLIENTS['sdkclient']['bin'])
        if result:
            break
        time.sleep(1)
    if not result:
        return ChromeExtensionBase.return_fail_data('Got None result from get_sdk_client_url_data() for url: %s' % url)
    elif 'rep' not in result:
        return ChromeExtensionBase.return_fail_data('Got error result from get_sdk_client_url_data() for url: %s' % url)
    elif result['rep'] <= 14:
        return ChromeExtensionBase.return_success_data(TEXT_GREEN)
    elif result['rep'] <= 29:
        return ChromeExtensionBase.return_success_data(TEXT_GRAY)
    elif result['rep'] <= 49:
        return ChromeExtensionBase.return_success_data(TEXT_YELLOW)
    elif result['rep'] > 49:
        return ChromeExtensionBase.return_success_data(TEXT_RED)
    else:
        return ChromeExtensionBase.return_fail_data('Unknown result from get_sdk_client_url_data() for url: %s' % url)


def internal_sdkclient_task(urls):
    results = []
    for url in urls:
        result = lookup(url)
        result["url"] = url
        result["competitor"] = module_name
        results.append(result)
    return results


@app.task(name=task_name, ignore_result=True)
def sdkclient_task(urls):
    """
    Does a GTI cloud lookup and returns the status for the given URLs
    :return:
    """
    results = []
    try:
        results = internal_sdkclient_task(urls)
    finally:
        app.send_task(RESULTS_TASK, [results], queue=RESULTS_QUEUE)
