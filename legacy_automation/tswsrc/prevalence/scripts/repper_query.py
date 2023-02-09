
import subprocess
from multiprocessing.queues import Queue
from multiprocessing.synchronize import Lock
from os import cpu_count
from multiprocessing.context import Process

WORKER_COUNT = cpu_count() * 4
#WORKER_COUNT = 2
ALEXA_FILE = '/tmp/top-1m.csv'
#ALEXA_FILE = '/tmp/alx'
QUEUE_SENTINEL = 'STOP'

SDKCLI_CMD = '/home/toolguy/gticloud/sdkclient -A test/TrustedSource_CA.crt -C test/TrustedSourceServer.crt -K test/TrustedSourceServer.key localhost -p 7443 -U -u %s'

def query_gticc(url):
    """Runs a process via subprocess.popen and waits till it terminates.
    """
    spobj = subprocess.Popen(SDKCLI_CMD % url, 
                             stdout=subprocess.PIPE, 
                                stdin=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                shell=True)
    stdout, stderr = spobj.communicate()
    return stdout, stderr

def worker(work_queue):
    try:
        for url in iter(work_queue.get, QUEUE_SENTINEL):
            #print url
            query_gticc(url)
    except Exception:
        pass
    return True


def main():
    work_queue = Queue()
    processes = []

    for url_line in open(ALEXA_FILE).readlines():
        rank, _, url = url_line.strip().rpartition(',')
        work_queue.put(url)

    for wrk in range(WORKER_COUNT):
        prcs = Process(target=worker, args=(work_queue,))
        prcs.start()
        processes.append(prcs)
        work_queue.put(QUEUE_SENTINEL)

    for prcs in processes:
        prcs.join()


if __name__ == '__main__':
    main()