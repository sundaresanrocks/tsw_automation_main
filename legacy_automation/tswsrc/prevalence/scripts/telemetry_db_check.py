import os
import datetime
import logging
import pymssql
import subprocess
import socket 
import sys
#t#from Queue import Queue
#t#from threading import Lock, Thread #$mt
from multiprocessing import Queue, Lock, Process, current_process   #$mp
import path
#### DEV SYSTEM IDENTIFIER ####
_SYS_PROD = True if socket.gethostname() == 'WIN-24HCTIDIPVS' else False
print(('Configuration: %s' 'WIN-24HCTIDIPVS' if _SYS_PROD else 'MKD'))

#### DB CONFIG ####
DB_USER = 'sa'
DB_PASS = '4eszaq1'
DB_NAME = 'telemetry'
DB_HOST = 'tsqatelemetrydb01.wsrlab'

#### PATH CONFIG ####
DIR_DRIVE = 'c:' if _SYS_PROD else 'm:'
DIR_BASE = DIR_DRIVE + '/' + 'qa'
DIR_WORK = DIR_BASE + '/' + 'working'
DIR_SOURCE_PATH = 'z:/repper_telemetry' if _SYS_PROD else 'm:/qa/tele_src' 
DIR_SOURCE_PATH = 'c:/qa' if _SYS_PROD else 'm:/qa/tele_src' 
#DIR_SOURCE_PATH = 'z:/repper_telemetry'

#### EXTERNAL BINARIES ####
BIN_7ZIP = 'C:/Program Files (x86)/7-Zip/7z.exe' if _SYS_PROD else \
                'C:/Program Files/7-Zip/7z.exe'

#### CONCURRENCY CONFIG/SHARED VARS ####
WORKER_POOL_SIZE  = 48 if _SYS_PROD else 2
QUE_SENTINEL_TEXT = 'END_OF_QUEUE'
QUE_WORK          = Queue()
QUE_ERROR         = Queue()
LST_HASH_MISS     = []
LST_VAL_MISMATCH  = []
LCK_ERROR         = Lock()
LCK_HASH_MISS     = Lock()
LCK_VAL_MISMATCH  = Lock()

#MAX_URL_COUNT = 2 #1000 * 1000



def get_files_in_dir(_dir, modified_since=None, wildcard='', recursive=False):
    """Returns the list of modified files in a directory after the timestamp
    :param _dir: A directory
    :param timestamp: instance of datenow class.
    :param basename: wild card string *basename*. Defaults to ''
    :rtype: list
    """
    rlist = []
    for dirpath, dirnames, filenames in os.walk(_dir):
        if (not recursive) and (dirpath != _dir):
               continue
        for filename in filenames:
            if wildcard in filename:
                abs_filename = os.path.join(dirpath, filename)
                if modified_since:
                    _tstamp = datetime.datetime.fromtimestamp(
                                            os.path.getmtime(abs_filename))
#                    logging.warning(_tstamp)
#                    logging.warning(modified_since)
                    if (_tstamp > modified_since):
                        rlist.append(abs_filename)
                else:
                    rlist.append(abs_filename)
    return rlist


class TelemetryDBChecks:
    """

    """
    def __init__(self):
        """Init connection with mssql db"""
        logging.debug("Connecting to mssql db: %s"%DB_HOST)
        self.con = pymssql.connect(host=DB_HOST, 
                                   user=DB_USER, 
                                   password=DB_PASS, 
                                   database=DB_NAME
                                  )
        logging.debug("Successfully Connected to the %s Database" % DB_HOST)

    def verify_hash_in_table(self, txt_file_name, table_suffix=None, 
                             table_prefix='telemetry_'):
        """
        Verify seen_count value for cl_hash in the telemetry database
        :param txt_file_name: name of file with cl_hash and seen_count
        :param table_suffix: suffix of the table, usually date.
        when table_suffix is None, text_file_name is used as suffix
        :param table_prefix: prefix for the table name including '_' if any

        File format:
            0X########################\t###\r

        Sample:
            0X000001A8493539E0C0612527	2
            0X000001D936C8A48834BB2811	1
        """
        if not table_suffix:
            table_suffix = os.path.basename(txt_file_name).rsplit('.')[0]
        table_name = str(table_prefix).strip() + str(table_suffix).strip()
        qry_tmpl = 'select seen_count from %s where ' % table_name \
                        + " cl_hash=CONVERT(binary(12), '%s', 1)"
        mismatch = 0
        not_found = 0

        fpr = open(txt_file_name)
        for line in fpr:
            cl_hash, delimiter, seen_count = line.strip().partition('\t')
#            logging.warning(type(cl_hash))
            qry = qry_tmpl % cl_hash
#            logging.warning(qry)
            self.cur = self.con.cursor()
            self.cur.execute(qry)
            for row in self.cur:
                if row[0] != int(seen_count):
                    logging.error('MISMATCH: %s\tdb=%s\tfile=%s' % (cl_hash,
                                                        row[0], seen_count))
            if self.cur.rowcount == 0:
                logging.error('NOT FOUND: %s', cl_hash)
        fpr.close()

def worker(work_queue, qry_tmpl, lck_error=Lock(), 
           lck_hash_miss=Lock(), lck_val_miss=Lock()):
    """Worker :("""
        #### Connect to db from each worker
    op_file = 'results.log'
    lst_hash_miss = []
    lst_error = []
    lst_val_miss = []
    db_con = pymssql.connect(host=DB_HOST, 
                                   user=DB_USER, 
                                   password=DB_PASS, 
                                   database=DB_NAME
                                  )

        ### Load hahes from queue
    #for line in work_queue.get():
    for line in iter(work_queue.get, QUE_SENTINEL_TEXT):
#        logging.warning(line)
        try:
            cl_hash, seen_count = str(line).strip().split('\t')
            qry = qry_tmpl % cl_hash
#            print qry

            cursor = db_con.cursor()
            cursor.execute(qry)
            for row in cursor:
                if row[0] != int(seen_count):
                    lst_val_miss.append((cl_hash, row[0], seen_count,))
            if cursor.rowcount == 0:
                lst_hash_miss.append((cl_hash, seen_count))
        except Exception as err:
            lst_error.append(err.args[0])
            raise
    db_con.close()

    lck_error.acquire()
    with open(op_file, 'a') as fpa:
        for item in lst_error:
            msg = 'ERROR: %s' % item
            fpa.write(msg + '\n')
            logging.error(msg)
    lck_error.release()

    lck_val_miss.acquire()
    with open(op_file, 'a') as fpa:
        for item in lst_val_miss:
            msg = 'VALUE MISMATCH: %s\tdb=%s\tfile=%s' % (item[0], item[1], 
                                                   item[2])
            fpa.write(msg + '\n')
            logging.error(msg)
    lck_val_miss.release()

    lck_hash_miss.acquire()
    with open(op_file, 'a') as fpa:
        for item in lst_hash_miss:
            msg = 'HASH MISS: %s\t%s' % (item[0], item[1])
            fpa.write(msg + '\n')
            logging.error(msg)
    lck_hash_miss.release()
    return True

def process_file_concurrently(text_file_name, table_suffix=None, 
                             table_prefix='telemetry_'):     
    """Returns a list of tuple(cl_hash, seen_count) from text file"""
        #### Construct the table_name
    if not table_suffix:
        table_suffix = os.path.basename(text_file_name).rsplit('.')[0]
    if not table_prefix:
        raise ValueError('Invalid table_prefix value!')
    table_name = str(table_prefix).strip() + str(table_suffix).strip()
    qry_tmpl = 'select seen_count from %s where ' % table_name \
                    + " cl_hash=CONVERT(binary(12), '%s', 1)"

        #### Load all Hashes in the queue
    with open(text_file_name) as fpr:
        for line in fpr:
            QUE_WORK.put(line)

        #### Start the process pool
    processes = []
#    worker(QUE_WORK, qry_tmpl, LCK_ERROR, LCK_HASH_MISS, LCK_VAL_MISMATCH)
    logging.info('Forking processes...')
    for work in range(WORKER_POOL_SIZE):
        process = Process(target=worker, args=(QUE_WORK, qry_tmpl,
        #t#process = Thread(target=worker, args=(QUE_WORK, qry_tmpl,#$mp
                                               LCK_ERROR, LCK_HASH_MISS, 
                                               LCK_VAL_MISMATCH))
        process.start()#$mp
        processes.append(process)
        QUE_WORK.put(QUE_SENTINEL_TEXT)

        #### Wait for termination of all chile proceses
    for process in processes:#$mp
        process.join()#$mp
    #t#QUE_WORK.join()#$mt
    print('All done')

def process_telemetry_logs_for_date(dates):
    """Process all the telemetry data for the given date/dates"""
    if (type(dates) == type('')) or type(dates) == type(''):
        dates = [dates]
    if not os.path.isdir(DIR_WORK):
        try:
            os.makedirs(DIR_WORK)
        except:
            logging.error('Unable to working create dir: %s' % DIR_WORK)
            raise
    if not os.path.isfile(BIN_7ZIP):
        raise EnvironmentError('7z.exe not found in %s' % BIN_7ZIP)
    files_dict = {}
    err_list = []
    dir_src_tmpl = DIR_SOURCE_PATH + '/%s_output'
    dir_tar_tmpl = DIR_WORK + '/%s/' 
    file_tar_tmpl = DIR_WORK + '/%s/%s'

    for date in dates:
        path.Path(dir_tar_tmpl % date).mkdir_p()
        _dir = dir_src_tmpl % date
        if not os.path.isdir(_dir):
            err_list.append('%s: is not a directory!' % _dir)
            continue
        files = [ _file for _file in get_files_in_dir(_dir, wildcard='part-') if not _file.endswith('.gz')]
        if not files:
            err_list.append('No files for date: %s in dir: %s' % (date, _dir))
        files_dict[date] = files
    if err_list:
        raise EnvironmentError('\n'.join(err_list))
    for date_l in files_dict:
        for _file in files_dict[date_l]:
            logging.warning('Processing file: %s' % _file)

            target = dir_tar_tmpl % date
            #extract
            cmd = '"%s" -y e %s -o%s' % (BIN_7ZIP, _file, target)
#            subprocess.call(cmd.replace('/', '\\'))

            txt_file =target + os.path.basename(_file)[:-3]
            print(('Checking %s' % txt_file))
#            process_file_concurrently(txt_file, table_suffix = '20140106')

#            break       #terminate after one file
        break       #terminate after one date

    #for date in dates:
    date = dates[0]





def main():
    file_name = 'c:/qa/part-r-00000' if _SYS_PROD else 'm:/qa/working/20.txt'
    file_name = 'c:/qa/100k.txt' if _SYS_PROD else 'm:/qa/working/20.txt'
#    tobj = TelemetryDBChecks()
#    tobj.verify_hash_in_table(file_name)
    start_time = datetime.datetime.now()
    #process_file_concurrently(file_name, table_suffix = '20140106')
    process_telemetry_logs_for_date(['20140106'])
    end_time = datetime.datetime.now()
    msg = '\nStart:%s\nEnd:%s\nDuration:%s\n\n' %(start_time, end_time, 
                                                  (end_time - start_time))
    with open('time.log', 'a+') as fpw:
        fpw.write(msg)
    logging.warning(msg)



if __name__ == '__main__':
    main()