"""
===============================
Wait for MWGDCC UI automation
===============================

Script that waits for the completion of MWGDCC UI automation.

The script exits after the maximum runtime. Checks are made periodically.

"""

WAIT_MAX_DURATION = 60 * 60 * 8         # 8 hours
CHECK_INTERVAL = 60                     # checks every minute

import sys
import subprocess
import pprint

exec_cmd = 'ps -ef | grep -v grep | grep "MWGDCC UI nightly tests"'
logging.info("Executing command : %s"%(exec_cmd))
spobj = subprocess.Popen(exec_cmd, 
                         stdout=subprocess.PIPE, 
                         stdin=subprocess.PIPE, 
                         stderr=subprocess.PIPE, 
                         shell=True)
stdout, stderr = spobj.communicate()

if log_path:
    ShellExecutor._put_stdoe_log_file(log_path, stdout, stderr)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:  python wait_for_mwgdcc_ui.py "MWGDCC UI nightly tests"')
        sys.exit(-1)

