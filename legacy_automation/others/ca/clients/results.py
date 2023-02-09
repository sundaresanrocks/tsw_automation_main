__author__ = 'manoj'

import os
import logging
import pprint
import datetime

from celery import Celery, task
from ca.ca_config import RABBITMQ_BROKER, RABBITMQ_BACKEND, RESULTS_QUEUE, RESULTS_TASK
from ca.processors.mongoresults import CompetitorMongoDoc
from ca.processors.canonicalizer import get_canon_url


module_name = os.path.basename(__file__).partition('.')[0]
app = Celery(RESULTS_TASK, backend=RABBITMQ_BACKEND, broker=RABBITMQ_BROKER, queue=RESULTS_QUEUE)


def update_url(result):
    canon_url = get_canon_url(result['url'])
    competitor = result['competitor']

    def update_if_not_exists(sub_doc, key, value):
        if key not in sub_doc:
            sub_doc[key] = value

    #### create/update overall document details
    doc = CompetitorMongoDoc.get_url_by_id(canon_url['sha256'])
    if not doc:
        doc = CompetitorMongoDoc()
        doc['_id'] = canon_url['sha256']
    update_if_not_exists(doc, 'url', result['url'])
    update_if_not_exists(doc, 'first_seen', datetime.datetime.utcnow())
    update_if_not_exists(doc, 'cl_hash', canon_url['cl-hash'])

    doc['last_seen'] = datetime.datetime.utcnow()

    #### update competitor details
    update_if_not_exists(doc, competitor, {})
    update_if_not_exists(doc[competitor], 'first_seen', datetime.datetime.utcnow())
    doc[competitor]['last_seen'] = datetime.datetime.utcnow()
    doc[competitor]['result'] = result['data']

    #### save the document!
    doc.save()


def internal_mongo_results(results):
    """
    Updates results in the mongo database
    :return:
    """
    logging.info(pprint.pformat(results))
    for result in results:
        try:
            if not 'url' in result:
                logging.error('key "url" not found for result: %s' % pprint.pformat(result))
                continue
            if not 'data' in result:
                logging.error('key "data" not found for result: %s' % pprint.pformat(result))
                continue
            if not 'competitor' in result:
                logging.error('key "competitor" not found for result: %s' % pprint.pformat(result))
                continue
            update_url(result)
        except Exception as err:
            msg = 'Unable to store results for URL: %s \n' % result['url']
            logging.error(msg + err.args[0])
            continue
    logging.info('Processed %s URLs. Exiting..' % len(results))


@task.task(name=RESULTS_TASK, ignore_result=True)
def mongo_results_task(results):
    """
    Updates results in the mongo database
    :return:
    """
    return internal_mongo_results(results)
