import sys
import getpass
import logging
import runtime
import runtime
from libx.ssh import SSHConnection


KeyAuth = runtime.KeyAuth
RETRY_COUNT = 2


def copy_key(host, username, public_key_file=None, password=None):
    """copy key for user to the host"""
    if not public_key_file:
        if username not in KeyAuth.users:
            raise ValueError('User not supported: %s' % username)

    print(('processing host:', host))
    # private_key_file = KeyAuth.users[username]['private']
    public_key_file = KeyAuth.users[username]['public']
    try:
        ssh = runtime.get_ssh(host, username)
    except Exception:
        logging.warning('Unable to connect via private key. Trying with password...')
        ssh = None
    else:
        ssh.close()
        logging.info('Key is already present in host.')
        return True

    for count in range(RETRY_COUNT):
        if not password:
            password = getpass.getpass('Enter password:')

        try:
            ssh = SSHConnection(host, username=username, password=password)
            break
        except:
            logging.warning('Unable to Connect..')
            if count > RETRY_COUNT:
                logging.error('setup Failed for host: %s', host)
            raise
    logging.info('Connection established with %s', 
                 str(ssh.execute('hostname')[0]).strip())

    print('Copying file.. ')
    ssh.execute('mkdir -p ~/.ssh/')
    ssh.put(public_key_file, '/tmp/tsa_public_key_copy')
    print('Appending keys.. ')
    ssh.execute('cat /tmp/tsa_public_key_copy >> ~/.ssh/authorized_keys')
    print('Setting file permission to 600.. ')
    ssh.execute('chmod 0600 ~/.ssh/authorized_keys')
    print('Cleaning temp files.. ')
    ssh.execute('rm /tmp/tsa_public_key_copy')
    print('Done.')

    try:
        ssh = runtime.get_ssh(host, username)
    except Exception:
        ssh = None
        logging.error('Unable to connect via private key.')
        logging.error('Public key authentication setup: FAILED for host: %s', host)
    else:
        ssh.close()
        logging.info('Public key authentication setup: SUCCESS for host: %s', host)
        return True


if __name__ == '__main__':
    # List of hosts(one user)
    # List of users(one host)
    # Public key file
    # Default password option

    if len(sys.argv) != 3:
        print('Usage:  python copy_ssh_key.py hostname username ')
        sys.exit(-1)
    if sys.argv[2] not in KeyAuth.users:
        print(('User ', sys.argv[2], ' is not supported'))
        sys.exit(-1)
    
    copy_key(sys.argv[1], sys.argv[2])
