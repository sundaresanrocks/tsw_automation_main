__author__ = 'abhijeet'


import time
import argparse
from path import Path
import psutil
from datetime import datetime


def get_process_stats(process_name):
    try:
        for proc in psutil.process_iter():
            if process_name in proc.name() and not 'process_profiler' in proc.name():
                cmdline = ' '.join(str(x) for x in proc.cmdline())
                capture_time = datetime.utcfromtimestamp(time.time())
                result = (capture_time, cmdline, proc.cpu_percent(), proc.memory_percent(), proc.memory_info().rss,
                          proc.memory_info().vms)
                return result
    except psutil.NoSuchProcess:
        pass
    return None


def run_process_profile(process_name, out_file, sleep_time=1):
    out = open(out_file, 'w')
    out.write('Time, Command Line, CPU percent, Memory percent, RSS, VMS\n')
    out.flush()
    try:
        while True:
            res = get_process_stats(process_name)
            if res is not None:
                print('Found usage statistics:%s' % str(res))
                out.write('%s\n' % ', '.join(str(x) for x in res))
                out.flush()
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        print('Detected keyboard interrupt. Exiting.')
        out.close()
        exit(0)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('process_name', help='Name of the process to profile', type=str)
    arg_parser.add_argument('out_file', help='path to output file', type=str)
    arg_parser.add_argument('sleeptime', help='Number of seconds to sleep between each process check cycle', type=int)
    args = arg_parser.parse_args()
    sleeptime = args.sleeptime
    out_file = Path(args.out_file)
    if out_file.exists():
        print('File name %s already exists' % out_file)
        exit(1)
    if not out_file.parent.exists():
        out_file.parent.makedirs()
    run_process_profile(args.process_name, out_file, sleeptime)
