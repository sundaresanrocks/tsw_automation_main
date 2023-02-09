"""
=============================
Start/Stop remote service
=============================

Executable script to stop/start remote service.

Usage:
    python rservice.py host service start|stop

    ex: python rservice.py puppet start

"""

import os
import sys
# import getpass
from libx.ssh import SSHX

KEY_PATH = os.environ['WORKSPACE'] + '/res/keys/'

if __name__ == '__main__':

    usage = '''Usage:
    Start/Stop puppet service
    -------------------------
    python service.py puppet start
    python service.py puppet stop
'''
    print(sys.argv)
    if (len(sys.argv) != 3) or (sys.argv[2].strip() not in ['start', 'stop']):
        print(usage)
        sys.exit(-1)
    
    action = sys.argv[2].strip()
    s = SSHX('localhost', 'root', KEY_PATH + 'tsa_root_private')
    if action == 'stop':
        sys.exit(s.service_stop('puppet'))
    elif action == 'start':
        sys.exit(s.service_start('puppet'))
    else:
        raise ValueError('Unknown action, %s' % sys.argv[2])
