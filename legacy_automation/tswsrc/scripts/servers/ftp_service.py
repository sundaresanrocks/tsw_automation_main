__author__ = 'manoj'
import sys
import logging

from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer  # <-
from pyftpdlib.authorizers import DummyAuthorizer
import subprocess
import ssl


def ftp_subprocess(cmd_args):
    import runtime
    cmd = 'python ' + runtime.src_path + '/bin/servers/ftp_service.py ' + cmd_args
    logging.info('Creating FTP server: %s' % cmd)
    return subprocess.Popen(cmd, shell=True)


def ftp_server(users):
    authorizer = DummyAuthorizer()
    for auth in users:
        authorizer.add_user(auth[0], auth[1], auth[2])
    handler = FTPHandler
    handler.authorizer = authorizer
    server = ThreadedFTPServer(('0.0.0.0', 2121), handler)
    server.serve_forever()


if __name__ == '__main__':
    auth_list = []
    print('Usage: python ftp_service.py user:pass:dir')
    for arg in sys.argv[1:]:

        auth_list.append(arg.split(':'))
    ftp_server(auth_list)
