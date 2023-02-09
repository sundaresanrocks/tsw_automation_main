__author__ = 'manoj'

import json
import logging
import base64
import urllib.request
import urllib.error
import urllib.parse
import requests

from ca.ca_config import CANON_HOST

CANON_URL_PREFIX = 'http://' + CANON_HOST + ':8080/canon/b64ue/'


class CanonicalizerError(Exception):
    """
    This exception is thrown for canonicalization errors.
    """


def get_canon_url(url):
    """
    Canonicalizes the given URL via json queries
    :param url: url
    :return: Canonicalized URL
    """
    url_encoded_bytes = bytes(urllib.parse.quote(url.encode('utf-8')), encoding='utf-8')
    b64_ue_url_bytes = base64.urlsafe_b64encode(url_encoded_bytes)
    b64_ue_url = CANON_URL_PREFIX + b64_ue_url_bytes.decode()

    http_reponse = requests.get(b64_ue_url).content

    value = json.loads(http_reponse.decode())

    if value['status'] != 'success':
        logging.error('Unable to canonicalize URL: %s' % url)
        # following line breaks the code for the urls which cannnot be canonicalised like SEARCHENGINES.GURU
        # raise CanonicalizerError(value['data'])
        return False
    return value['data']


# http://qadash.wsrlab:8080/canon/b64ue/

# Testing time [avimehenwal]
if __name__=='__main__':
    # import timeit
    import time
    start_time = time.time()
    with open('/home/toolguy/avi_test/tsa-new/ca/urls_50.txt') as urls:
        for url in urls:
            print(get_canon_url(url))
    # print(timeit.timeit("get_canon_url()", setup="from __main__ import get_canon_url"))
    print("TIME TAKEN --- %s seconds ---" %(time.time()-start_time))

# RESULTS:
# 42 secs for 50 urls ~ 1 sec per url