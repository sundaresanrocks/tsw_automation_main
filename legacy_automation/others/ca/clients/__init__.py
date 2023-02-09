__author__ = 'manoj'
import os
from .sdkclient import SDKClientURLLooker


class CompetitorNotFound(Exception):
    """
    This exception is thrown when a competitor was not found
    """


SUPPORTED_CLIENTS = {'sdkclient': {'class': SDKClientURLLooker,
                                   'bin': os.environ.get('SDK_CLIENT', '/home/toolguy/sdkclient'),
                                   'server': 'tunnel.web.trustedsource.org'}}

