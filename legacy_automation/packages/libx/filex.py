"""
============================================
filex - File Management Library
============================================
"""
import re
import os
import shutil
import logging
import time
import datetime
import uuid
import hashlib
from path import Path

#snippet from Harvester
def put_files_in_target(source_file, _target_dir, source_base='./', create_target_path=False):
    """Places source_file Files in the target directory
    :source_file: the given files will be put in target directory
    :type: string or list of strings
    Raises:
        EnvironmentError when unable to copy file
    """
    if create_target_path:
        Path(_target_dir).mkdir_p()
    if not (os.path.isdir(_target_dir)):
        raise NotADirectoryError('Target directory %s doesnt exist' % _target_dir)
    _source_list = []
    if type(source_file) == type('string'):
        _source_list.append(source_file)
    elif type(source_file) == type([]):
        _source_list = source_file
    else:
        raise TypeError('source_file should be list/string')

    for item in _source_list:
        if type(item) != type('str'):
            raise TypeError('source_file should be string/list of ' + 'strings. Found %s of type %s' % (item,
                                                                                                        type(item)))
        _file_abs = source_base + item
        if not os.path.isfile(_file_abs):
            raise EnvironmentError(
                'Source Data File %s does not exist!' % _file_abs)

        shutil.copy(_file_abs, _target_dir)
        logging.info("%s placed in target dirctory" % _file_abs)
    return True


def clean_any_dir_recursive(_dir):
    """Deletes the dir using rmtree, creates a new dir with same name. '/'
    is not allowed."""

    if _dir.strip() == '/':
        raise IOError('target directory cant be root!')
    Path(_dir).rmtree_p()
    os.makedirs(_dir)
    logging.info('Clean any dir recursive: %s - ok' % _dir)


def clean_files_in_dir(_dir):
    """Deletes all files in a given folder. '/' is not allowed."""
    if _dir.strip() == '/':
        raise IOError('target directory cant be root!')
    if not os.path.isdir(_dir):
        logging.info('%s doesnt exist/not directory. Trying to create' % _dir)
        os.makedirs(_dir)

    file_list = os.listdir(_dir)
    for fileName in file_list:
        item = os.path.join(_dir, fileName)
        if os.path.isfile(item):
            os.remove(item)
    logging.info("Clean files in dir: %s - ok" % _dir)
    return True


def _get_files_in_dir(_dir):
    """Returns the list of files in a directory, not recursive"""
    if not os.path.isdir(_dir):
        logging.info('%s is not a direcotry.')
        raise EnvironmentError('%s is not a direcotry.')
    source_file_list = []
    dir_file_list = os.listdir(_dir)
    for fileName in dir_file_list:
        item = os.path.join(_dir, fileName)
        if os.path.isfile(item):
            source_file_list.append(item)
    return source_file_list


def get_files_in_dir(_dir, modified_since=None, wildcard='', recursive=False):
    """Returns the list of modified files in a directory after the timestamp
    :param _dir: A directory
    :param modified_since: instance of datenow class.
    :param wildcard: wild card string *basename*. Defaults to ''
    :rtype: list
    """
    ret_list = []
    for dir_path, dir_names, file_names in os.walk(_dir):
        if (not recursive) and (dir_path != _dir):
            continue
        for filename in file_names:
            if wildcard in filename:
                abs_filename = os.path.join(dir_path, filename)
                if modified_since:
                    _t_stamp = datetime.datetime.fromtimestamp(
                        os.path.getmtime(abs_filename))
                    #                    logging.warning(_t_stamp)
                    #                    logging.warning(modified_since)
                    if _t_stamp > modified_since:
                        ret_list.append(abs_filename)
                else:
                    ret_list.append(abs_filename)
    return ret_list


def get_file_timestamp(long=False):
    """ returns file timestamp"""
    time_now = datetime.datetime.now()
    dt = datetime.datetime
    if int:
        return str(str(dt.now()).replace(':', '-')).replace(' ', '_')
    return str(time_now.year) + str(time_now.month) + str(time_now.day) \
           + time.strftime("%I", time.localtime()) + str(time_now.minute) \
           + str(time_now.second)


_slugify_strip_re = re.compile(r'[^\w\.\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


def slugify(value):
    """
    Normalizes string, removes non-alpha characters,
    and converts spaces to hyphens.
    
    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata

    if not isinstance(value, str):
        value = str(value)
    value = str(unicodedata.normalize('NFKD', value).encode('ascii', 'ignore'))
    value = str(_slugify_strip_re.sub('', value).strip())[1:]
    return _slugify_hyphenate_re.sub('-', value)


def open_unique_file(base_dir, prefix=''):
    while True:
        fn = os.path.join(base_dir, str(prefix) + str(uuid.uuid4()))
        try:
            fdw = os.open(fn, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        except OSError:
            # file already exists, try again
            continue
        break
    logging.debug('Unique File: %s created' % fn)
    return os.fdopen(fdw, 'w')


def md5_file(file, block_size=10 * 2 ** 20):
    if os.path.exists(file):
        handle = open(file, 'rb')
        md5 = hashlib.md5()
        while True:
            block_data = handle.read(block_size)
            if not block_data:
                break
            md5.update(block_data)
        return md5.hexdigest()
    else:
        return False


def main():
    import path
    path.Path('/as').mkdir_p()
    path.Path('/as').mkdir_p()
    fderr = open_unique_file('.', 'stderr.')

    print((slugify('a.s-_dAAAfaf:sdf/.<>}{')))
    print(('short timestamp:', get_file_timestamp()))
    print(('long timestamp:', get_file_timestamp(True)))
    print((get_files_in_dir('/tmp')))
    print((get_files_in_dir('/tmp', recursive=True)))
    print((get_files_in_dir('/tmp', wildcard='temp')))
    print((get_files_in_dir('/tmp', wildcard='text')))
    print((get_files_in_dir('/tmp', wildcard='tmp')))
    print((get_files_in_dir('/tmp', modified_since=datetime.datetime(2013, 4, 1), wildcard='')))


if __name__ == '__main__':
    main()

