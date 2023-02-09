"""
Data driven tests
*****************
"""
import collections

__author__ = 'manoj'


import os
import csv
import json
import logging
import datetime
from functools import wraps
#todo: check if a test already exists. if so, raise "duplicate test error" and abort!
#todo: remove reference to config
#todo: filter the tests
_TEST_GEN_DATA = '%__zzz_tsa_test_gen_list'
_TEST_GEN_FILE = '%__zzz_tsa_test_gen_file'
_TEST_DATA_FILE = '%__zzz_tsa_test_data_file'
_TEST_DATA = '%__zzz_tsa_test_data'
_TESTLINKID = '%__zzz_tsa_testlink_id'
_SUPPORTED_FILE_EXT = ['json', 'txt', 'csv']

def testlinkid(*arg):
    """Test link id of given test case"""
    def wrapper(original_func):
        id = getattr(original_func, _TESTLINKID, '')
        setattr(original_func, _TESTLINKID, id)
        return original_func
    return wrapper

def testdata_file(*args):
    """Test case decorator. Test data for test function"""
    def wrapper(original_func):
        dataattr = getattr(original_func, _TEST_DATA_FILE, [])
        dataattr.extend(args)
        setattr(original_func, _TEST_DATA_FILE, dataattr)
        return original_func
    return wrapper

def testdata(*args):
    """ """
    def wrapper(original_func):
        dataattr = getattr(original_func, _TEST_DATA, [])
        dataattr.extend(args)
        setattr(original_func, _TEST_DATA, dataattr)
        return original_func
    return wrapper

def testgen_data(*args):
    """Test case decorator. Test data for test function"""
    def wrapper(original_func):
        dataattr = getattr(original_func, _TEST_GEN_DATA, [])
        dataattr.extend(args)
        setattr(original_func, _TEST_GEN_DATA, dataattr)
        return original_func
    return wrapper

def testgen_file(*files):
    """Test case decorator for test data in a file based on file extension.
    .json and .txt files are currently supported.

    File/list of files is the input.

    json files can contain:
        1. list - item values are used in naming tests
        2. dict - keys are used in naming tests

    Txt file contains:
        Lines of text data, new test for each line

    csv file contains:
        Lines of comma separated values, new test for each line
    """
    def wrapper(original_func):
        fileattr = getattr(original_func, _TEST_GEN_FILE, [])
        fileattr.extend(files)
        setattr(original_func, _TEST_GEN_FILE, fileattr)
        return original_func
    return wrapper


def tsadriver(cls):
    """Class decorator, decorate a unittest.TestCase class.

    The names of the test methods follow the pattern ``test_func_name
    + "_" + str(data)``. If ``data.__name__`` exists, it is used
    instead for the test method name.

    For each method decorated with ``@file_data('test_data.json')``, the
    decorator will try to load the test_data.json file located relative
    to the python file containing the method that is decorated. It will,
    for each ``test_name`` key create as many methods in the list of values
    from the ``data`` key.

    The names of these test methods follow the pattern of
    ``test_name`` + str(data)``
    """

    def __feed_data(original_func, *args, **kwargs):
        """feed the test data item to the test."""
        @wraps(original_func)
        def wrapper(self):
            logging.debug('Test data wrapper: \n  args: %s \n  kwargs: %s' % (str(args).encode('UTF-8'),
                                                                             str(kwargs).encode('UTF-8')))
            return original_func(self, *args, **kwargs)
        return wrapper

    def __raise_errpr(original_func, *args, **kwargs):
        """test will raise error."""
        @wraps(original_func)
        def wrapper(self):
            raise IOError('File not found')
        return wrapper

    def load_file(name, func, file_attr, testgen):
        """Json data file handler"""

        def _raise_ve(*args):
            raise ValueError("%s does not exist" % file_attr)

        def _raise_ext(*args):
            raise IOError("Unknown extention: %s" % file_attr)

        def _raise_fnf(*args):
            raise IOError("File not found: %s" % file_attr)

        def _add_test():
            _test_name = "{0}_{1}".format(name, suffix)
            if (hasattr(cls, _test_name)):
                _test_name += str(datetime.datetime.now())
            setattr(cls, _test_name, __feed_data(func, value))

        #find extension
        if file_attr.find('.') == -1:
            setattr(cls, name, __feed_data(_raise_ext, None))
            return

        #check extension type
        file_ext = file_attr.split('.')[-1]
        if file_ext not in _SUPPORTED_FILE_EXT:
            setattr(cls, name, __feed_data(_raise_ext, None))
            return

        if os.path.exists(file_attr):
            logging.info('Data file found: %s' % file_attr)
        else:
            logging.error('Data file not found: %s' % file_attr)
            if testgen:
                test_name = "{0}_{1}".format(name, "error")
                setattr(cls, test_name, __feed_data(_raise_fnf, None))
            else:
                setattr(cls, name, __feed_data(_raise_fnf, None))
            return

        #handle file types
        if file_ext == 'json':
            data = json.loads(open(file_attr, encoding='utf-8').read())
            if testgen:             #generate tests
                for elem in data:
                    if isinstance(data, dict):
                        key, value = elem, data[elem]
                        suffix = key
                    elif isinstance(data, list):
                        suffix = value = elem
                    _add_test()
            else:                   #pass data
                setattr(cls, name, __feed_data(func, data))
        elif file_ext == 'txt':
            data = open(file_attr, encoding='utf-8').read().splitlines()
            if testgen:             #generate tests
                for elem in data:
                    suffix = value = elem.strip()
                    _add_test()
            else:                   #pass data
                setattr(cls, name, __feed_data(func, data))
        elif file_ext == 'csv':
            data = list(csv.reader(open(file_attr, encoding='utf-8')))
            if testgen:             #generate tests
                for elem in data:
                    if len(elem) > 0 and str(elem[1]).strip().startswith('#'):
                        continue    #skip if first element starts with #
                    suffix = value = elem
                    _add_test()
            else:                   #pass data
                setattr(cls, name, __feed_data(func, data))
        else:
            raise Exception('Unknown file extension')

    for name, func in list(cls.__dict__.items()):
        _del_attr_flag = False
        if hasattr(func, _TEST_DATA):
            for v in getattr(func, _TEST_DATA):
                setattr(cls, name, __feed_data(func, v))
                #break       #limits to first value

        if hasattr(func, _TEST_DATA_FILE):
            _bool_break = False
            if len(getattr(func, _TEST_DATA_FILE)) == 1:
                _bool_break = True
            for file_attr in getattr(func, _TEST_DATA_FILE):
                if _bool_break:          #limits to first value
                    load_file(name, func, file_attr, False)
                    break
                else:                   #creates a test for each file
                    _del_attr_flag = True
                    test_name = "{0}_{1}".format(name, file_attr)
                    load_file(test_name, func, file_attr, False)

        if hasattr(func, _TEST_GEN_DATA):
            for v in getattr(func, _TEST_GEN_DATA):
                if not(type(v) in (type(()), type([])), type({})):
                    v = [v]
                for vi in v:
                    test_name = getattr(vi, "__name__", "{0}_{1}".format(name, vi))
                    if type(v) in (type({}), type(collections.OrderedDict())):
                        setattr(cls, test_name, __feed_data(func, v[vi]))
                    else:
                        setattr(cls, test_name, __feed_data(func, vi))
            _del_attr_flag = True

        if hasattr(func, _TEST_GEN_FILE):
            for file_attr in getattr(func, _TEST_GEN_FILE):
                load_file(name, func, file_attr, True)
            _del_attr_flag = True

        #delete actual test for generator tests
        if _del_attr_flag:
            delattr(cls, name)

    return cls

