import logging
import os
import pprint
from java_tsw.py.compile import JAVA_TEMPLATE
from libx.process import ShellExecutor

__author__ = 'manoj'


def run_canon_file(input_file, output_file, rank_seed=1):
    if not os.path.isfile(input_file):
        raise FileNotFoundError(input_file)
    if os.path.isfile(output_file):
        logging.warning('File deleted: %s' % output_file)
        os.unlink(output_file)
    cmd = JAVA_TEMPLATE + ' CanonFile %s %s %s' % (input_file, output_file, rank_seed)
    stdo, stde = ShellExecutor.run_wait_standalone(cmd)
    #todo: do error checking

    if not os.path.isfile(output_file) or os.path.getsize(output_file) <= 0:
        if stdo:
            logging.error(pprint.pformat(stdo))
        if stde:
            logging.error(pprint.pformat(stde))
        raise FileNotFoundError('Output was file not created: %s' % output_file)


def get_canon_process(input_file, output_file, rank_seed=1):
    cmd = JAVA_TEMPLATE + ' CanonFile %s %s %s' % (input_file, output_file, rank_seed)
    logging.debug(cmd)
    return ShellExecutor.run_daemon_standalone(cmd)


if __name__ == '__main__':
    run_canon_file('luq1', 'o.txt')