"""
=====================
ssh2
=====================

Friendly Python SSH2 interface
"""

import os
import re
import tempfile
import paramiko
import logging
import path


class SSHConnection(object):
    """Connects and logs into the specified hostname.
    Arguments that are not given are guessed from the environment."""

    def __init__(self,
                 host,
                 username=None,
                 private_key=None,
                 password=None,
                 port=22):
        self.host = host
        self.username = username
        log_msg = 'SSHConnection: host: %s ' % host \
                  + 'username: %s ' % username \
                  + 'private_key: %s ' % private_key \
                  + 'password: %s ' % password \
                  + 'port: %s' % str(port)
        logging.debug('HOST :- %s' % self.host + log_msg)
        self._sftp_live = False
        self._sftp = None
        if not username:
            raise TypeError("You have not specified a username")

        # Log to a temporary file.
        templog = tempfile.mkstemp('.txt', 'ssh-')[1]
        paramiko.util.log_to_file(templog)

        # Begin the SSH transport.
        self._transport = paramiko.Transport((host, port))
        self._transport_live = True
        # Authenticate the transport.
        if password:
            # Using Password.
            self._transport.connect(username=username, password=password)
        else:
            # Use Private Key.
            if not private_key:
                raise TypeError("You have not specified a password or key.")
                # # Try to use default key.
                # if os.path.exists(os.path.expanduser('~/.ssh/id_rsa')):
                # private_key = '~/.ssh/id_rsa'
                # elif os.path.exists(os.path.expanduser('~/.ssh/id_dsa')):
                #    private_key = '~/.ssh/id_dsa'
                #else:
                #    raise TypeError, "You have not given a password or key."
            private_key_file = os.path.expanduser(private_key)
            if not os.path.isfile(private_key_file):
                raise KeyError('SSH Key not found! %s' % private_key_file)
            rsa_key = paramiko.RSAKey.from_private_key_file(private_key_file)
            self._transport.connect(username=username, pkey=rsa_key)

    def _sftp_connect(self):
        """Establish the SFTP connection."""
        if not self._sftp_live:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
            self._sftp_live = True

    def get(self, remotepath, localpath=None):
        """Copies a file between the remote host and the local host."""
        if not localpath:
            localpath = os.path.split(remotepath)[1]
        self._sftp_connect()
        logging.info('HOST %s:- ' % self.host + 'GET: remote: %s, to local: %s', remotepath, localpath)
        self._sftp.get(remotepath, localpath)

    def put(self, localpath, remotepath=None):
        """Copies a file between the local host and the remote host."""
        # check if local file exists
        if not os.path.isfile(localpath):
            raise EnvironmentError('File not found: %s' % localpath)
        # calculate remotepath if it is None
        if not remotepath:
            remotepath = os.path.split(localpath)[1]
        # put the file
        self._sftp_connect()
        logging.info('HOST %s:- ' % self.host + 'PUT: local: %s to remote: %s', localpath, remotepath)
        self._sftp.put(localpath, remotepath)

        # calculate md5 checksums
        md5local = path.Path(localpath).read_hexhash("md5")
        md5remote = self.md5sum(remotepath)
        logging.debug('md5 checksum: local: %s \t remote: %s' % (md5local, md5remote))
        if md5local != md5remote:
            raise ValueError('md5 checksum mismatch! new md5: %s' % md5remote)

    def md5sum(self, remotepath=None):
        """Returns md5sum for remote file"""
        # calculate md5 checksums
        stdoe = self.execute('md5sum %s' % remotepath)
        if len(stdoe[1]) != 0:
            if 'No such file or directory' in stdoe[1]:
                raise FileNotFoundError(remotepath)
            else:
                _msg = 'Unable to md5sum on host. %s' % '\n'.join(stdoe)
                logging.warning(_msg)
                raise EnvironmentError(_msg)
        md5 = stdoe[0].split(' ')[0]
        logging.debug('md5 checksum: %s \tremote file: %s' % (md5, remotepath))
        return stdoe[0].split(' ')[0]

    def execute(self, command, *, ssh_env_str=None):
        """Execute the given commands on a remote machine."""
        channel = self._transport.open_session()
        self._transport.set_keepalive(30)
        if ssh_env_str:
            command = '%(ssh_env_str)s SHELL=/bin/bash; %(ssh_cmd)s ' % {'ssh_env_str': ssh_env_str,
                                                                         'ssh_cmd': command}
        logging.info('HOST %s:- ' % self.host + 'EXEC: %s', command)
        channel.exec_command('source .bash_profile;' + command)
        sout = channel.makefile('rb', -1).readlines()
        # output = [x.strip() for x in output]
        # output = [x.strip() for x in output]
        serr = channel.makefile_stderr('rb', -1).readlines()
        # todo: write the files to current directory, just like ShellExecutor
        stdout_str = b''.join(sout).decode('UTF-8')
        stderr_str = b''.join(serr).decode('UTF-8')
        logging.debug('HOST %s:- ' % self.host + 'Stdout: %s\nStderr: %s', stdout_str, stderr_str)
        return stdout_str, stderr_str

    def close(self):
        """Closes the connection and cleans up."""
        # Close SFTP Connection.
        if self._sftp_live:
            self._sftp.close()
            self._sftp_live = False
            # Close the SSH Transport.
        if self._transport_live:
            self._transport.close()
            self._transport_live = False

    def __del__(self):
        """Attempt to clean up if not explicitly closed."""
        try:
            if hasattr(self, 'close'):
                self.close()
        except:
            pass


class SSHX(SSHConnection):
    """Extension of SSHConnection"""

    def exec_open_channel(self, command, *, ssh_env_str=None):
        """Execute a process and don't close the channel"""
        if ssh_env_str:
            command = '%(ssh_env_str)s SHELL=/bin/bash; %(ssh_cmd)s ' % {'ssh_env_str': ssh_env_str,
                                                                         'ssh_cmd': command}
        channel = self._transport.open_session()
        logging.info('HOST %s:- ' % self.host + 'OPEN CHANNEL: EXEC: %s', command)
        channel.exec_command('source .bash_profile;' + command)
        return channel

    def exec_recv_exit_code(self, command, *, ssh_env_str=None):
        """Execute and return the stats code"""
        if ssh_env_str:
            command = '%(ssh_env_str)s SHELL=/bin/bash; %(ssh_cmd)s ' % {'ssh_env_str': ssh_env_str,
                                                                         'ssh_cmd': command}
        channel = self._transport.open_session()
        logging.info('HOST %s:- ' % self.host + '%s', command)
        channel.exec_command('source .bash_profile;' + command)
        exit_code = channel.recv_exit_status()
        logging.debug('HOST %s:- ' % self.host + 'EXIT CODE: %s for %s', exit_code, command)
        return exit_code

    def service_stop(self, service_name):
        """Stop a unix service"""
        xcode = self.exec_recv_exit_code('/etc/init.d/%s stop' % service_name)
        if xcode == 0:
            logging.info('HOST %s:- ' % self.host + 'SERVICE: %s is stopped', service_name)
            return xcode
        else:
            raise EnvironmentError('SERVICE: %s stop failed', service_name)

    def service_is_running(self, service_name):
        """True if given service is running"""
        xcode = self.exec_recv_exit_code('/etc/init.d/%s status' % service_name)
        if xcode == 0:
            logging.info('HOST %s:- ' % self.host + 'SERVICE: %s is running', service_name)
            return True
        elif xcode == 3:
            logging.info('HOST %s:- ' % self.host + 'SERVICE: %s is stopped', service_name)
            return False
        else:
            raise EnvironmentError('Service: %s - unknown state' % service_name)

    def service_start(self, service_name):
        """Start a given service"""
        xcode = self.exec_recv_exit_code('/etc/init.d/%s start' % service_name)
        if xcode == 1:
            logging.warning('HOST %s:- ' % self.host + 'SERVICE %s: is already running.', service_name)
            raise EnvironmentError('SERVICE %s: is already running.')
        elif xcode == 0:
            logging.info('HOST %s:- ' % self.host + 'SERVICE: %s is running', service_name)
            return xcode
        else:
            raise EnvironmentError('SERVICE: %s start failed', service_name)

    def service_restart(self, service_name):
        """Restart a given service"""
        self.service_stop(service_name)
        return self.service_start(service_name)

    def yum_update(self):
        """Yum updates the red hat system as root"""
        if self.username != 'root':
            raise EnvironmentError('yum update can be called only as root!')
        stdoe = self.execute('yum -y update')
        if not (('Complete!' in stdoe[0]) or ('No Packages marked for Update' in stdoe[0])):
            if stdoe[1] != '':
                raise EnvironmentError('Errors while executing yum update')
        logging.info('HOST %s:- ' % self.host + 'yum update COMPLETE')

    def sed_file(self, find_term, replace_term, file_name, delimiter='/'):
        """execute sed on a remote host"""
        _cmd = "sed -i 's%s%s%s%s%sg' %s" % (delimiter, find_term,
                                             delimiter, replace_term,
                                             delimiter, file_name)
        self.execute(_cmd)

    def get_svn_version(self, svn_path):
        """returns svn information for a given directory"""
        # input validation
        if not isinstance(svn_path, str):
            raise TypeError('svn_path must be string')
            # execute ssh command and process stdoe
        stdoe = self.execute('svn info %s ' % svn_path)
        if len(stdoe[1]) > 0:
            if 'is not a working copy' in stdoe[1]:
                raise ValueError('%s is not svn working copy' % svn_path)
            else:
                raise IOError('Unable to get svn info. unknown error')
        rev = re.compile(r'Revision: ([0-9]+)').findall(stdoe[0])
        if len(rev) != 1:
            raise KeyError('Unable to find revision information')
        return rev

    def get_grep_file(self, remote_src_file, args,
                      local_path='./tsa_get_grep.tmp',
                      rem_tmp_file='/tmp/tsa_get_grep.tmp'):
        """grep the remote file with given args and copy the file back"""
        _cmd = 'grep %(args)s %(remote_src_file)s > %(rem_tmp_file)s' % {'args': args,
                                                                         'remote_src_file': remote_src_file,
                                                                         'rem_tmp_file': rem_tmp_file}
        self.execute(_cmd)
        self.get(remote_src_file, local_path)

    def _get_rpm_list(self, grep_pat=""):
        """Gets list of installed rpm packages"""
        rpms = []
        stdoe = self.execute('rpm -qa | grep "%s"' % grep_pat)
        pkgs = stdoe[0].splitlines()
        for pkg in pkgs:
            if str(pkg).strip() != '':
                rpms.append(str(pkg).strip())
        return rpms

    def _file_exists(self, file_name):
        """Checks if file exists using ls command"""
        stdout, stderr = self.execute('ls ' + file_name)
        if len(stderr) == 0:
            return True
        return False

    def dir_list(self, dir_name):
        """Returns a list of directories"""
        stdout, stderr = self.execute('ls -1 %s' % dir_name)
        if len(stderr) == 0:
            return stdout.splitlines()
        return []


class SSHTS(SSHX):
    """Extension of SSHConnection"""

    def _check_connectivity(self, dbname):
        """returns True if connection is successful"""
        _cmd = "echo 'quit' | isql " + dbname + " sa 1qazse4"
        stdoe = self.execute(_cmd)
        if 'Connected' in ''.join(stdoe):
            logging.info('HOST %s:- ' % self.host + "Connection successful: %s", dbname)
            return True
        logging.warning('HOST %s:- ' % self.host + "Unable to connect to: %s", dbname)
        return False

    def _setup_db_connectivity(self, dbname):
        """setup db connectivity for given database name
        raises Exception
        """
        ini_file = '/etc/odbc.ini'
        conf_file = '/etc/freetds/freetds.conf'
        (server, dbshort) = dbname.split('_')
        server += '.wsrlab'

        stdoe_ini = self.execute("grep " + dbname + " " + ini_file)
        stdoe_conf = self.execute("grep " + server + " " + conf_file)

        if dbname not in stdoe_ini[0]:
            _cmd = "echo -e '\n###Added by qa automation###\n" \
                   + "[" + dbname + "]\n" \
                   + "Driver          = TDS\n" \
                   + "Description     = Smart Filter database\n" \
                   + "Trace           = No\n" \
                   + "Servername      = " + server + "\n" \
                   + "Database        = " + dbshort + "\n" \
                   + "UID             = sfcontrol\n" \
                   + "Protocol        = 9.0\n' >> " + ini_file
            logging.info('HOST %s:- ' % self.host + "Updating odbc.ini: " + _cmd)
            stdout, stderr = self.execute(_cmd)
            if (stdout is '') & (stderr is ''):
                logging.info('HOST %s:- ' % self.host + "odbc.ini updated successfully")
            else:
                logging.error('HOST %s:- ' % self.host + "ERROR: stderr: " + stderr)
                raise EnvironmentError('Unable to update %s' % dbname)

        if server not in stdoe_conf[0]:
            _cmd = "echo -e '\n###Added by qa automation###\n" \
                   + "[" + server + "] " \
                   + "\n        host = " + server \
                   + "\n        port = 1433" \
                   + "\n        tds version = 9.0\n' >> " + conf_file
            logging.info('HOST %s:- ' % self.host + "Updating freetds.conf: %s", _cmd)
            stdout, stderr = self.execute(_cmd)
            if (stdout is '') & (stderr is ''):
                logging.info('HOST %s:- ' % self.host + "freetds.conf updated successfully")
            else:
                logging.error('HOST %s:- ' % self.host + "ERROR: stderr: " + stderr)
                raise EnvironmentError('Unable to update %s' % dbname)

    def ts_odbc_setup(self, u2_name, d2_name, r2_name):
        """Sets odbc, freetds files for DB connectivity"""
        if self.username != 'root':
            raise EnvironmentError("must be run as root")

        db_names = (u2_name, d2_name, r2_name)
        failed = []
        for db_name in db_names:
            if not self._check_connectivity(db_name):
                self._setup_db_connectivity(db_name)
                if not self._check_connectivity(db_name):
                    failed.append(db_name)
        if len(failed) == 0:
            return True

    def ts_check_odbc_setup(self, u2_name, d2_name, r2_name):
        """Checks odbc, freetds files for DB connectivity"""
        db_names = (u2_name, d2_name, r2_name)
        failed = []
        for db_name in db_names:
            if not self._check_connectivity(db_name):
                failed.append(db_name)
        if len(failed) != 0:
            raise EnvironmentError('Unable to connect to - %s' % ', '.join(failed))
        return True

    def ts_sfimport(self, url_file,
                    agent=81,
                    queue='General',
                    harvester='Customer Logs',
                    language='English',
                    remote_temp_file='/tmp/tsa-ar-sfimport.txt'):
        """sfimport on a remote system, return stdout/err stream"""
        if self.username == 'root':
            raise EnvironmentError("sfimport can't be run as root")
        import runtime

        _cmd = [str(runtime.ENV.get_env_for_ssh_cmd()).strip()[:-1],
                '/usr2/smartfilter/import/sfimport -a %s' % agent
                + ' -q %s' % queue
                + ' -H "%s"' % harvester
                + ' -f u -D -A -c un '
                + ' -L %s' % language
                + ' -l %s' % remote_temp_file]

        self.execute('rm -f %s' % remote_temp_file)
        self.put(url_file, remote_temp_file)
        stdoe = self.execute(';'.join(_cmd))
        return stdoe

    def get_installed_wsr_rpm_packages(self, regex_pat='[a-zA-Z]+[0-9]*-[0-9]'):
        """
        Gets list of installed wsr packages
        #hack: change regex if needed
        """
        wsr_ver_list = {}
        pkgs = self._get_rpm_list('wsr-')

        pat = re.compile(regex_pat)
        for pkg in pkgs:
            ser = pat.search(pkg)
            if ser:
                wsr_ver_list[pkg[:ser.end() - 2]] = pkg[ser.end() - 1:]
            else:
                raise KeyError('New package: %s. Please modify regex' % pkg)
        return wsr_ver_list


if __name__ == '__main__':
    raise Exception('You ran this script!. Import this :D')