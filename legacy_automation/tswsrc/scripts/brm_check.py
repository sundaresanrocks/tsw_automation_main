"""
=======================
BRM Check Utility
=======================

Usage:
tpy brm_check.py <jenkins host> <release_branch> <build number> 
<host list.txt> [--install]

"""
__author__ = 'manoj'

import os
import sys


if __name__ == '__main__':
    if len(sys.argv) <= 4:
        print('Usage:  tpy brm_check.py <jenkins_host> <release_branch> <build_number> <host_list.txt> [--install]')
        sys.exit(-1)

    jenkins_host = sys.argv[1]
    release_branch = sys.argv[2]
    build_number = sys.argv[3]
    file_name = sys.argv[4]

    if not os.path.isfile(file_name):
        print(('File:', file_name, ' not found'))
        sys.exit(-1)

    #generate host list
    hosts = []
    [hosts.append(str(line).strip()) for line in open(file_name).readlines() 
     if not str(line).strip().startswith('#')]

    print(('Hosts: ', ','.join(hosts)))
    #Run the utility
    from lib.utils.brm import BRMUtils

    brm_obj = BRMUtils(jenkins_host, release_branch, build_number)
    if '--install' in sys.argv:
        brm_obj.check_and_update_hosts(hosts)
    else:
        #check only!
        brm_obj.check_installed_version(hosts)
