"""
Batch multiprocess
==================
Batch process a large file in mutually independent chunks and join the results

"""
from os import cpu_count

__author__ = 'manoj'

from contextlib import suppress
import logging
import os


MINIMUM_ENTRIES = 16
NO_OF_CORES = cpu_count()


class BatchProcess():

    def __init__(self):
        self.mapped_input_files = []

    # def mapper(self):
    #     raise NotImplementedError('Must be overridden')
    #
    # def worker(self):
    #     raise NotImplementedError('Must be overridden')
    #
    # def reducer(self):
    #     raise NotImplementedError('Must be overridden')


class SimpleFileBatchProcess(BatchProcess):

    def mapper(self, input_file, no_of_cores=NO_OF_CORES, minimum_entries=MINIMUM_ENTRIES):
        lines = open(input_file).readlines()
        if not minimum_entries > 0:
            raise ValueError('minimum_entries must be greater than 0. Found: %s' % minimum_entries)
        if len(lines) < minimum_entries * no_of_cores:
            no_of_cores = len(lines) // minimum_entries
            logging.debug('New number of cores = %s ' % no_of_cores)
        if not no_of_cores > 0:
            no_of_cores = 1
        if len(lines) < no_of_cores:
            raise ValueError('Number of lines in the input_file is less than no_of_cores')
        logging.debug('No of cores: %s' % no_of_cores)

        self.mapped_input_files = []
        #create input_files
        lines_per_file = len(lines) // no_of_cores
        for item in range(no_of_cores):
            file_name = input_file+'-%s' % item
            self.mapped_input_files.append(file_name)
            with open(file_name, 'w', newline='\n') as fpw:
                if item == lines_per_file:
                    fpw.writelines(lines[item*lines_per_file:])
                else:
                    fpw.writelines(lines[item * lines_per_file: (item+1)*lines_per_file])
        logging.debug('Input files: %s' % self.mapped_input_files)

    def reducer(self, worker_callback, output_file, temp_file_suffix='.tmp', include_header=True):

        self.run(worker_callback, temp_file_suffix)

        lines = []
        for file_name in self.mapped_input_files:
            with open(file_name + temp_file_suffix) as fpr:
                if include_header:
                    lines.extend(fpr.readlines())
                    include_header = False
                else:
                    lines.extend(fpr.readlines()[1:])
            with suppress(Exception):
                #### remove split input file
                os.unlink(file_name)
                #### remove temp output file
                os.unlink(file_name + temp_file_suffix)
        logging.debug('Output file: %s' % output_file)
        with open(output_file, 'w', newline='\n') as fpw:
            fpw.write(''.join(lines))
            # fpw.writelines(lines)

    def run(self, worker_callback, temp_file_suffix):
        processes = []
        for input_file_name in self.mapped_input_files:
            processes.append(worker_callback(input_file_name, input_file_name + temp_file_suffix))

        logging.debug('All processes started')
        for _process in processes:
            _process.wait()
        logging.debug('All processes ended')
