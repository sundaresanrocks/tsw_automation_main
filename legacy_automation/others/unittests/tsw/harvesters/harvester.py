from tsw.lib.harvester.rules import HarvesterAPWG

__author__ = 'manoj'

import unittest
import os

import tsw.lib.servers
from tsw.lib.harvester.harvester import Harvester


class TestHarvester(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()


def main():
    """ Unit tests"""
    #####  unit tests  ######
    apwg_con = HarvesterAPWG()
    har = Harvester(apwg_con)
    tmpfile = har.create_temp_file('man')
    os.unlink(tmpfile)
    ### place_souce_file ####
    har.put_file_in_working([])
    har.put_file_in_working('dummy.txt')
    har.put_file_in_working(['dummy.txt'])

    try:
        har.put_file_in_working(None)
    except TypeError:
        pass
    try:
        har.put_file_in_working('nonexist.txt')
    except FileNotFoundError:
        pass

    print(('app server:', tsw.lib.servers.is_app_server_up()))
    print(('guv server', tsw.lib.servers.is_guvnor_server_up()))

    print(('reset processed files', har.reset_processed_files()))
    print(('clean working directory', har.clean_working_dir()))
    print(('is property exists', har.check_properties_file()))

    print(('check open session', har.check_open_session()))
    print(('remove open session', har.remove_open_session()))
    print(('check open session', har.check_open_session()))
    print(('create open session', har.create_open_session()))
    print(('check open session', har.check_open_session()))

    har.put_file_in_working('dummy.txt')
    #print 'check harvester resutl', har.check_harvester_result()
    #hobj = har.process_log()
    #if len(hobj) >=1:
    #    print "Log INFO : Actions Taken : %s " %(hobj[-1].action_taken)
    #    print "Log INFO : rules_matched : %s " %(hobj[-1].rules_matched)
    #print len(hobj)
    #pass
