"""
============================================
Utilities Library
============================================
"""
import difflib
import pprint
import inspect
import pickle
import os

class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:

    1) items added
    2) items removed
    3) keys same in both but changed values\n
    4) keys same in both and unchanged values
    5) dicts match
    5) partial match
    """
    
    def __init__(self, current_dict, past_dict):
        if not isinstance(current_dict, dict):
            raise TypeError('current_dict must be a dict')
        if not isinstance(past_dict, dict):
            raise TypeError('past_dict must be a dict')
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
        self.union = self.set_current.union(self.set_past)

    def added(self):
        """returns items added in current dict"""
        return self.set_current - self.intersect 

    def removed(self):
        """returns items removed in current dict"""
        return self.set_past - self.intersect 

    def changed(self):
        """returns items changed in current dict"""
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        """returns items unchanged in current dict"""
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])

    def diff(self):
        """returns diff between current and past dict"""
        return self.union - self.intersect

    def ismatch(self):
        """returns true if diference is empty. else returns false"""
        try:
            if len(self.current_dict) != len(self.past_dict):
                raise Exception('length of dicts not equal')
            for key in self.current_dict.keys():
                if self.current_dict[key] != self.past_dict[key]:
                    raise Exception('values dont match')
        except Exception as err:
            return False
        return True

    def __str__(self):
        """ Returns list, keys added, removed and values changed"""
        msg = 'new dict: %s\nbase dict: %s' % (pprint.pformat(self.current_dict, width=4,indent=4),
                                               pprint.pformat(self.past_dict, width=4, indent=4))
        if self.ismatch():
            msg += '\nDict differ: new and base match!'
            return msg

        for item in self.added():
            msg += '\n\tDict differ: Added keys: {' + str(item) + ': ' \
                + str(self.current_dict[item]) + '}'
        for item in self.removed():
            msg += '\n\tDict differ: Missing keys: {' + str(item) + ': ' \
                + str(self.past_dict[item]) + '}'
        for item in self.changed():
            msg += '\nDict differ: key: ' + str(item) + \
                '\told: ' + str(self.past_dict[item]) + \
                '\tnew: ' + str(self.current_dict[item])
        return msg

    def partial_match(self):
        """Returns True if subset match exists!"""
        if (len(self.added()) == 0) and (len(self.changed()) == 0):
            return True
        return False


class ListDiffer(object):
    """
    Calculate the difference between two lists as:
    (1) items added
    (2) items removed
    (3) list match
    (4) isempty
    """
    def __init__(self, current_list, past_list):
        self.current_list, self.past_list = current_list, past_list
        self.set_current, self.set_past = set(current_list), set(past_list)
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        """returns items added in current list"""
        return list (self.set_current - self.intersect)

    def removed(self):
        """returns items removed in current dict"""
        return list(self.set_past - self.intersect)

    def diff(self):
        """returns diff between current and past list"""
        diff = []
        lstdiff = lambda l1,l2: [x for x in l1 if x not in l2]
        if len(lstdiff(self.current_list, self.past_list)) != 0:
            diff.append(lstdiff(self.current_list,self.past_list))
        if len(lstdiff(self.past_list, self.current_list)) != 0:
            diff.append(lstdiff(self.past_list, self.current_list))
        return diff

    def ismatch_unordered_set(self):
        """returns true if diference is empty. else returns false
        order is not considered"""
        if len(self.diff()) == 0:
            return True
        else:
            return False

    def ismatch(self):
        """returns true if list matches and order is same"""
        #copy list
        match = True
        if len(self.current_list) != len(self.past_list):
            return False
        if self.current_list == [] and self.past_list == []:
            return True
        if not self.ismatch_unordered_set():
            return False

        list = []
        for item in self.past_list:
            list.append(item)
        list.reverse()
        for item in self.current_list:
            x = list.pop()
            if item != x:
                match = False
        return match


def put_pickle(object, file_suffix=''):
    """Pickles the object"""
    z_frame = inspect.getframeinfo(inspect.currentframe())
    z_file = '%s.%s.%s' %(os.path.basename(z_frame.filename), 
                          str(z_frame.function), 
                          file_suffix)
    pickle.dump(object, open('/tmp/%s' % z_file, 'w+'))


def get_pickle(file_suffix=''):
    """Returns an object from pickle"""
    z_frame = inspect.getframeinfo(inspect.currentframe())
    z_file = '%s.%s.%s' % (os.path.basename(z_frame.filename), 
                           str(z_frame.function), 
                           file_suffix)
    return pickle.load(open('/tmp/%s' % z_file))


if __name__ == '__main__':
    '''unit tests for ListDiffer'''
    # x = ListDiffer([1,2] , [2,1])
    # print x.added()
    # print x.removed()
    # print x.diff()
    # print x.ismatch()
    # x = ListDiffer([1,2,1] , [1,1,2])
    # print x.ismatch()
    # print x.ismatch_unordered_set()
    #
    # '''unit tests for DictDiffer'''
    # y = DictDiffer({1:1,2:2,6:6} , {3:2,2:3,1:1})
    # print y.added()
    # print y.removed()
    # print y.changed()
    # print y.unchanged()
    # print y.diff()
    # print y.ismatch()
    # print str(y)
    # print DictDiffer({1:1},{1:1})
    # raw_input('press ENTER to continue...')