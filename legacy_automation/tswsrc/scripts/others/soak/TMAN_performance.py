__author__ = 'spriha'

import argparse
from path import Path
from scripts.others.soak import process_profiler
from scripts.others.soak import sfimport_soak
from libx.process import ShellExecutor


def run_performance(outputfilename):
     process_profiler.run_process_profile('tman' , outputfilename, 0)


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('input_file', help='Enter the filename with urls to sfimport', type=str)
    arg_parser.add_argument('outputfilename', help='Enter the filename to record the performance', type=str)
    arg_parser.add_argument('queuesize', help= 'Enter the queue size the performance should be recorded for', type=int)
    args = arg_parser.parse_args()
    input_file = Path(args.input_file)
    outputfilename = Path(args.outputfilename)
    queuesize = args.queuesize
    sfimport_soak.run_soak_sfimport( 0 , input_file , queuesize)
    try:
        ShellExecutor.run_daemon_standalone('/usr2/smartfilter/dbtools/tman -d -D -o outfile.txt')
        run_performance(outputfilename)
    except KeyboardInterrupt:
        print('Detected keyboard interrupt. Exiting.')
        exit(0)
