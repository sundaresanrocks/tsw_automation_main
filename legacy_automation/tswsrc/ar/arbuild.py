import os
import time


from framework.test import SandboxedTest
import logging

from lib.exceptions import TestFailure
from lib.build import Build
import runtime
from lib.sfv4 import SFV4CheckURL


        

class ARBUILD:
    """
    Autorating BUild Execution
    """
    def build_process(self):
        """ This is test 1"""
        
        
        
def _build_unit_test():
    obj = ARBUILD()
    obj.build_process()
    sfv4_obj = SFV4CheckURL()
    return_val = sfv4_obj.check_urls(obj.urls)
    print(return_val)

if __name__ == '__main__':
    _build_unit_test()