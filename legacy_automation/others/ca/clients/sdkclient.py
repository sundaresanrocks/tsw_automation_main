"""
sudo sysctl -w net.ipv4.ip_local_port_range="1024 64000"

edit or append to /etc/sysctl.conf file:
# increase system IP port limits
net.ipv4.ip_local_port_range = 1024 65535
"""

import multiprocessing
import subprocess
import logging
import os
import re
import time
import pprint

# import multiprocessing
# from multiprocessing.queues import Queue
# from multiprocessing.process import current_process
from multiprocessing.context import Process
# from multiprocessing.synchronize import Lock
from queue import Queue
from threading import Thread
import processors.canonicalizer as canon
import pdb

logging.basicConfig(format='[%(levelname)s] [%(asctime)s] {%(filename)s:%(lineno)d} - %(message)s',
                    datefmt='%y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)


# making unique call for canonicaliser [avimehenwal]
def canonicalize_url_data(url):
    import processors.canonicalizer as canon
    if canon.get_canon_url(url) is False:
        msg = url + '\t cannnot be canonicalised by canonicalizer !!! Skipped'
        print(msg)
        with open('canon_error.log', 'a+') as fpw:
            print(fpw)
            print(fpw.write(str(msg+"\n")))
        return False
    else:
        return canon.get_canon_url(url)


def get_sdk_client_url_data(url, client_path, canon_bool=True):
    """
    Runs sdk client, parses the output data and returns result as a dict.
    :param url: url to be queries
    :return: Lookup information about URL
    """
    exec_cmd = '%s -u %s tunnel.web.trustedsource.org' % (client_path, url)
    if not os.path.isfile(client_path):
        raise FileNotFoundError(client_path)

    spobj = subprocess.Popen(exec_cmd,
                             stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)

    stdout, stderr = [data.decode("UTF-8") for data in spobj.communicate()]

    stdoe = stdout + stderr

    if 'Usage: ./sdkclient' in stdoe or 'Failed to look up host' in stdoe or 'TS_RateUrl failed' in stdoe \
            or stdoe.lower().startswith('fail'):
        logging.error(url + ": %s" % stdoe)
        return None

    if 'rep:' not in stdoe:
        logging.error(url + ": %s" % stdoe)
        return None

    #todo: use the regex (.*):\s(.*) to form the dict

    def remexp(regex, search_string):
        re_result = re.findall(regex, search_string)
        if re_result and len(re_result) == 1:
            return re_result[0]
        return None

    geo = lambda x: x if len(x.strip()) else ''
    try:
        rep_dict = {'rep': int(remexp('rep:\s(-*\d+)', stdoe)),
                    'cats': remexp('\ncats:\s(.*)\n', stdoe),
                    'attr_flags': re.findall('\nattr_flags:\s(\d+)\n', stdoe)[0],
                    'ms': True if re.findall('mcafee secure:\s(yes)', stdoe) else False,
                    'geo': geo(re.findall('\ngeo:(.*)\n', stdoe)[0])
                    }
    except Exception as err:
        # logging.warning('except' + "%s" % traceback.format_exc())
        rep_dict = None

    if canon_bool:
        canon = canonicalize_url_data(url)
        # print(canon)
        rep_dict['canon'] = canon

    return rep_dict


class SDKClientURLLooker:

    def __init__(self, **kwargs):
        self.queue_sentinel = 'STOP'
        self.work_queue = Queue()
        self.result_queue = Queue()
        self.worker_count = kwargs['threads']
        self.client_path = kwargs['config']['bin']

    def worker(self, work_queue):
        for url_line in iter(work_queue.get, self.queue_sentinel):
            # print(url_line)
            result = None
            for i in range(3):
                result = get_sdk_client_url_data(url_line, self.client_path)
                if result:
                    break
                time.sleep(1)
            self.result_queue.put([url_line, result])

    def process_urls(self, rank_url):
        process_list = []
        worker_count = min(self.worker_count, len(rank_url))
        for url in rank_url:
            self.work_queue.put(url[1])
        for work in range(worker_count):
            process = Thread(target=self.worker, args=(self.work_queue,))
            process.start()
            process_list.append(process)
            self.work_queue.put(self.queue_sentinel)
        for process in process_list:
            process.join()
        self.result_queue.put(self.queue_sentinel)
        res = {}
        for url, value in iter(self.result_queue.get, self.queue_sentinel):
            if value is not None:
                for item in rank_url:
                    if item[1] == url:
                        alexa_rank = item[0]
                value['alexa_rank'] = alexa_rank
                print(url, value)
                res[url] = value
        # res = {url: value for url, value in iter(self.result_queue.get, self.queue_sentinel)}
        # pdb.set_trace()
        return res

if __name__ == '__main__':

    xx = SDKClientURLLooker(config={'bin': 'k:\\gti\\fp\\sdkclient.bat'})
    res = xx.process_urls(['google.com', 'amazon.com', 'yahoo.com', 'twitter.com'])
    with open('op.txt', 'w') as fpw:
        fpw.write(pprint.pformat(res))




    # print(get_sdk_client_url_data('google.com', './sdkclient'))