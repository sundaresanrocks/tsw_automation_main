__author__ = 'spriha'

import argparse
from path import Path
from scripts.others.soak import process_profiler
from scripts.others.soak import sfimport_soak
from libx.process import ShellExecutor
from dbtools.agents import Agents
from lib.db.mssql import TsMsSqlWrap

def run_performance(outputfilename):
     process_profiler.run_process_profile('wrua' , outputfilename, 0)

def check_wrua_queue():
    d2_obj = TsMsSqlWrap('D2')
    sql = "select cl_hash from d2.dbo.wrqueue (nolock) where agent_name = 'WRUA'"
    data = d2_obj.get_select_data(sql)
    count = len(data)
    return count

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('input_file', help='Enter the filename with urls to sfimport', type=str)
    arg_parser.add_argument('outputfilename', help='Enter the filename to record the performance', type=str)
    arg_parser.add_argument('queuesize', help= 'Enter the queue size the performance should be recorded for', type=int)
    args = arg_parser.parse_args()
    input_file = Path(args.input_file)
    outputfilename = Path(args.outputfilename)
    queuesize = args.queuesize
    current_queue = check_wrua_queue()
    print(current_queue)
    if (current_queue > queuesize) :
        print('We already have a larger queue available for WRUA')
    else :
        newqueue = queuesize - current_queue
        print(newqueue)
        sfimport_soak.run_soak_sfimport( 0 , input_file , newqueue)
        tman_obj = Agents("TMAN")
        tman_obj.run_agent(agent_args="-d -D ",output_file='tman_out.txt')
    try:
        ShellExecutor.run_daemon_standalone('/usr2/smartfilter/dbtools/wrua -D -o outfile.txt')
        run_performance(outputfilename)
    except KeyboardInterrupt:
        print('Detected keyboard interrupt. Exiting.')
        exit(0)
