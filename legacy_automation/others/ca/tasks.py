__author__ = 'M'

from celery import Celery, task

#capx = Celery('tasks', broker='amqp://qadash.wsrlab//')
cel = Celery('ca_tasks', backend='amqp', broker='amqp://myuser:mypassword@qadash.wsrlab:8010/myvhost')
task


@cel.task()
def add(x, y):
    return x+y


@cel.task()
def norton(url):
    return 'result from norton for url' % url


@cel.task()
def avira(urls):

    return 'result from avira for url' % urls

