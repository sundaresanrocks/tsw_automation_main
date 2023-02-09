__author__ = 'manoj'

CANON_HOST = 'qadash.wsrlab'

RABBITMQ_BROKER = 'amqp://myuser:mypassword@qadash.wsrlab:8010/myvhost'
RABBITMQ_BACKEND = 'amqp'
RESULTS_QUEUE = 'results'
RESULTS_TASK = 'results_task'

SUPPORTED_TASKS = {'avira': 'avira_task',
                   'norton': 'norton_task',
                   'sdkclient': 'sdkclient_task',
                   'results': 'results_task',
                   'bitdefender': 'bitdefender_task',
                   'wot': 'wot_task'}

TEXT_GREEN = 'GREEN'
TEXT_YELLOW = 'YELLOW'
TEXT_GRAY = 'GRAY'
TEXT_RED = 'RED'


class MongoDBSettings:
    user = ''
    passwd = ''
    host = '172.19.216.125'
    dbname = 'competitor'
    port = 27017

    collection_name = 'urlstore'