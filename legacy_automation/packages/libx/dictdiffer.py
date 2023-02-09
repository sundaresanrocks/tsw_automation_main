"""
========================================================================
*Customized Dictionary comparison Utility that uses a map for validation
*@author : Anurag Vemuri
***
Please subclass this class and override _comparator()
incase the comparison criteria needs to be changed .
***
=========================================================================
"""

import time
import logging
import datetime


class DictDiffer():
    """ """

    def __init__(self, time_delta=3600):
        self.match_dict = {}
        self.time_delta = time_delta
        self.mismatch_list = []

    def __date_comparison(self, key, dict1, dict2, time_delta):
        """Please provide time delta in seconds"""
        date_compare_flag = True
        seconds_diff = 0
        logging.info('Comparing dates %s %s' % (dict1[key], dict2[key]))
        if dict1 > dict2:
            seconds_diff = (dict1[key] - dict2[key]).seconds
        else:
            seconds_diff = (dict2[key] - dict1[key]).seconds
        logging.info('Difference of %s seconds' % seconds_diff)
        if seconds_diff > time_delta:
            date_compare_flag = False
        return date_compare_flag

    def _comparator(self, key, dict1, dict2):
        """Override this to change comparison criteria"""
        compare_flag = True
        logging.debug('Comparing %s %s' % (dict1[key], dict2[key]))
        compare_flag = self.__validate(key, dict1, dict2)
        if type(dict1[key]) == type(datetime.datetime.now()):
            compare_flag = self.__date_comparison(key, dict1, dict2, self.time_delta)
        elif dict1[key] != dict2[key]:
            compare_flag = False
            self.mismatch_list.append('Mismatch at key "%s" -> (%s , %s)' % (key, dict1[key], dict2[key]))
        self.match_dict[key] = compare_flag

    def __validate(self, key, dict1, dict2):
        """Validates if key is present in both the dicts"""
        validate_flag = True
        message = None
        logging.debug('Validating %s' % key)
        if not dict1.has_key(key):
            message = 'Dict 1 does not have key %s' % key
            raise Exception(message)
            # self.match_dict[key] = message
            # validate_flag = False
        if not dict2.has_key(key):
            message = 'Dict 1 does not have key %s' % key
            raise Exception(message)
            # self.match_dict[key] = message
            # validate_flag = False
        return validate_flag

    def __result(self):
        """Parses result list and generates mismatch messages"""
        return self.mismatch_list

    def __dict_differ(self, dict1, dict2, full, map_obj):
        """Recursively parses individual elements of nested lists/dicts"""
        if map_obj is not None:
            dict_map = map_obj
        else:
            dict_map = dict1
        index = 0
        for key in dict_map.keys():
            self.__validate(key, dict1, dict2)
            if type(dict_map[key]) == type([]):
                while index < len(dict_map[key]):
                    try:
                        self.__dict_differ((dict1[key])[index], (dict2[key])[index], full, (dict_map[key])[index])
                        index += 1
                    except Exception:
                        raise Exception('Unequal number of entries in\nDict1: %s\nDict2: %s' % (dict1[key], dict2[key]))
            elif type(dict_map[key]) == type({}):
                self.__dict_differ(dict1[key], dict2[key], full, dict_map[key])
            else:
                if full is False:
                    if dict_map[key] is True:
                        self._comparator(key, dict1, dict2)
                else:
                    self._comparator(key, dict1, dict2)

    def compare_dicts(self, dict1, dict2, full, dict_map=None):
        """
        Wrapper that is open to external calls .
        returns: mismatches as list
        """
        result = None
        if type(dict1) != type({}) \
                or type(dict2) != type({}) \
                or type(full) != type(True) \
                or (type(dict_map) != type({}) and type(dict_map) != type(None)):
            raise Exception("Please provide arguments in following order:\nDict,Dict,bool,Dict."
                            "Do not provide a MAP(4th argument), if full=True")
        if full is True:
            if dict_map is not None:
                raise Exception('Please remove dict_map(4th argument) or set full=False(3rd argument)')
        elif full is False:
            if dict_map is None:
                raise Exception('Please provide a MAP for comparison')
        self.__dict_differ(dict1, dict2, full, dict_map)
        result = self.__result()
        return result


if __name__ == '__main__':
    test_dict1 = eval(open('one.txt').read())
    time.sleep(3)
    test_dict2 = eval(open('two.txt',).read())
    obj = DictDiffer(2)
    test_dict_map = eval(open('map.txt',).read())
    print(obj.compare_dicts(test_dict1, test_dict2, False, dict_map=test_dict_map))
    obj1 = DictDiffer(20)
    test_dict_map = eval(open('map.txt',).read())
    print(obj1.compare_dicts(test_dict1, test_dict2, False, dict_map=test_dict_map))
