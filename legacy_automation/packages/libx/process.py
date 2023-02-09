"""
============================================
Process/Shell Execution Library
============================================
Wrapper for shell execution and subprocess.

"""
import logging
# from libx.filex import open_unique_file

import subprocess
# import time
import sys
import re
import io
import pprint
import os
import uuid


class Process:
    """
    Wrapper for python subprocess to simplify calling.
        :param exec_str: the execution string that will be executed
        :param stdpipes: False - output will not be piped.
                         Can be used when dealing with internal objects
                         Will not override the run_xxpiped_xxxxx commands
        :param flags: Subprocess flags if any
    """

    def __init__(self, exec_str, stdpipes=False, flags=None):
        self.stdpipes = False
        self.flags = None
        self.retcode = None
        self.process = None
        self._executed = None
        self.exec_str = exec_str
        if type(True) == type(stdpipes):
            self.stdpipes = stdpipes
        self.set_flags(flags)

    def run_piped_wait(self):
        """
        Returns a process object that has piped stderr and stdout
        Blocked function call
        Waits till the process completes execution or crashes
        """
        if self._executed:
            raise Exception('Can be executed only once')
        self.process = self.__get_live_process(True)

        _out, _err = self.process.communicate()

        self.process.stdout = io.StringIO(_out.decode('UTF-8'))
        self.process.stderr = io.StringIO(_err.decode('UTF-8'))

        return self.process

    def run_unpiped_wait(self):
        """
        Returns a process object that has unpiped stderr and stdout
        Unblocked function call
        Waits till the process completes execution or crashes
        """
        if self._executed:
            raise Exception('Can be executed only once')
        process = self.__get_live_process(False)
        process.wait()
        return process

    def run_piped_daemon(self):
        """
        Execute a process and returns subprocess.Popen object.
        May cause buffer overflow in pipes!
        The returned object can be interacted for more control.
        Warning!!!!Use with caution!!!!
        """
        if self._executed:
            raise Exception('Can be executed only once')
        self.process = self.__get_live_process(True)
        return self.process

    def run_unpiped_daemon(self):
        """
        Execute a process and returns subprocess.Popen object.
        The process is run as daemon.
        The returned object can be interacted for more control.
        """
        if self._executed:
            raise Exception('Can be executed only once')
        self.process = self.__get_live_process(False)
        return self.process

    def get_returncode(self):
        """Get exit code of the completed process"""
        if self._executed:
            return self.retcode
        else:
            return None

    def set_flags(self, flags):
        """
            Sets the subprocess flags 
        """
        if None == flags:
            if sys.platform.startswith("win"):
                import ctypes

                # From MSDN
                SEM_NOGPFAULTERRORBOX = 0x0002
                ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)
                # win32con.CREATE_NO_WINDOW?
                flags = 0x8000000
            else:
                flags = 0
            self.flags = flags
        return

    def __get_live_process(self, stdpipes=False):
        """ Dont call from outside. Only internal calls"""
        import runtime

        if self._executed:
            raise Exception('Can be executed only once')
        flags = self.flags
        new_env = runtime.env
        if not stdpipes:
            _process = subprocess.Popen(self.exec_str,
                                        shell=True,
                                        creationflags=flags,
                                        env=new_env)
        else:
            _process = subprocess.Popen(self.exec_str,
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        creationflags=flags,
                                        env=new_env)
        self._executed = True
        self.process = _process
        return _process


class ShellExecutor:
    """Generic class to execute shell command. Retains the process object.
        Can be used to validate stdout and stderr streams

        Implements:
            must implement cmd_builder() method in subclass

        Raises:
            ChildProcessError() -
    """

    def __init__(self):
        self.cmd = []
        self._executed = False
        self.stderr = None
        self.stdout = None
        self.process = None
        self.process_obj = None

    def get_exec_str(self):
        return ' '.join(self.cmd)

    def cmd_builder(self):
        raise Exception("cmd_builder must be implemented in subclass")

    def run_and_validate(self, rgx_stderr, exp_stderr, rgx_stdout, exp_stdout):
        import runtime
        if self._executed:
            raise Exception('Can be executed only once')
        self._executed = True
        logging.debug('Patterns for stderr: %s' % rgx_stderr)
        logging.debug('Patterns for stdout: %s' % rgx_stdout)

        # check if exp_stderr is a list or not
        if list != type(exp_stderr):
            logging.critical('exp_stderr should be a list or tuple')
            raise TypeError

        #check if exp_stdout is a list or not
        if list != type(exp_stdout):
            logging.critical('exp_stdout should be a list or tuple')
            raise TypeError

        #check if rgx_stderr is a list or not
        if list != type(rgx_stderr):
            logging.critical('rgx_stderr should be a list or tuple')
            raise TypeError

        #check if rgx_stdout is a list or not
        if list != type(rgx_stdout):
            logging.critical('rgx_stdout should be a list or tuple')
            raise TypeError

        logging.info("Execution string: %s" % self.get_exec_str())
        self.process_obj = Process(self.get_exec_str())
        self.process_obj.run_piped_wait()
        self.process = self.process_obj.process

        self.stderr = str(self.process.stderr.read().encode('utf-8'))
        self.stdout = str(self.process.stdout.read().encode('utf-8'))
        logging.debug("stderr: %s" % self.stderr)
        logging.debug("stdout: %s" % self.stdout)

        ShellExecutor._put_stdoe_log_file('.', self.stdout, self.stderr, env=runtime.env)

        #process stderr stream
        _act_err = self.__re_pattern_matcher(self.stderr, rgx_stderr)
        #process stdout stream
        _act_out = self.__re_pattern_matcher(self.stdout, rgx_stdout)

        logging.info('Expected Result Tuple for stderr: %s' % exp_stderr)
        logging.info('Actual Result Tuple from  stderr: %s' % _act_err)
        logging.info('Expected Result Tuple for stdout: %s' % exp_stdout)
        logging.info('Actual Result Tuple from  stdout: %s' % _act_out)

        if exp_stderr == _act_err and exp_stdout == _act_out:
            _res = True
        else:
            _res = False
        # r_val = self.pass_fail(_res)
        r_stat = 'Success.'
        if not _res:
            r_stat = 'Mismatch.'
        logging.info("Subprocess execution result validation: %s " % r_stat)
        if not _res:
            raise ChildProcessError('Execution stdout/stderr check failed.')
        return _res

    def __re_pattern_matcher(self, search_string, patterns):
        _results = []
        for _pattern in patterns:
            _rm = re.search(_pattern, search_string, re.IGNORECASE)
            logging.debug('Regex Match:- Pattern: %s \nTarget: %s' % (_pattern, search_string))
            if _rm:
                logging.info('Match Found: %s' % _pattern)
                _results.append(True)
            else:
                # logging.debug('Regex Match Failed: %s' % _pattern)
                _results.append(False)
        return _results

    def pass_fail(self, boolean):
        if boolean:
            return 'PASS'
        else:
            return 'FAIL'

    def get_return_code(self):
        return self.process

    @staticmethod
    def run_wait_standalone(exec_cmd, log_path='.', create_log_file=True, log_prefix_str='', env=True, timeout=600):
        """Runs a process via subprocess.popen and waits till it terminates.
        This is used to run given command in shell. It is standalone. It can
        be used without instantiating the class.

        Returns:
            <stdout>, <stderr> as string

        Usage:
            from tsa.process import ShellExecutor
            exec_str = 'ps -e'
            sout, serr = ShellExecutor.run_wait_standalone(exec_str)
        """
        # todo: replace below with ones from config
        if isinstance(env, bool):
            if env:
                import runtime
                env = runtime.env
            else:
                env = None

        logging.info("Executing command : %s" % (exec_cmd))
        spobj = subprocess.Popen(exec_cmd, stdout=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=True,
                                 env=env)
        try:
            spobj.wait(timeout=timeout)
            stdout, stderr = ['' if val is None else str(val.decode("UTF-8", errors='ignore'))
                              for val in spobj.communicate(timeout=timeout)]
        except subprocess.TimeoutExpired:
            spobj.kill()
            stdout, stderr = ['' if val is None else str(val.decode("UTF-8", errors='ignore'))
                              for val in spobj.communicate()]
            logging.info('Process was killed via TimeoutExpired exception')

        if log_path:
            ShellExecutor._put_stdoe_log_file(log_path, stdout, stderr, prefix_str=log_prefix_str, env=env,
                                              cmd=exec_cmd)

        return stdout, stderr

    @staticmethod
    def _put_stdoe_log_file(base_dir, stdo, stde, env=None, prefix_str='', cmd=None):
        """
        Write stdout and stderr to files
        """
        if not isinstance(prefix_str, str):
            raise TypeError('prefix_str must be str. found: %s' % type(prefix_str))
        count = 0
        while True:
            if count > 4:
                raise EnvironmentError('Unable to create temporary file. Retried %s times' % count)
            count += 1
            uu = str(uuid.uuid4())

            def new_temp_file(file_part):
                if prefix_str:
                    suffix = '-' + prefix_str + '-' + uu + '.log'
                else:
                    suffix = prefix_str + '-' + uu + '.log'
                return os.path.join(base_dir, file_part + suffix)

            fne = new_temp_file('stderr')
            fno = new_temp_file('stdout')
            fn_env = new_temp_file('env')
            fn_cmd = new_temp_file('cmd')

            try:
                fde = os.open(fne, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
                fdo = os.open(fno, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
                fd_env = os.open(fn_env, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
                fd_cmd = os.open(fn_cmd, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
            except OSError:
                if os.path.isfile(fne):
                    os.unlink(fne)
                if os.path.isfile(fno):
                    os.unlink(fno)
                if os.path.isfile(fn_env):
                    os.unlink(fn_env)
                if os.path.isfile(fn_cmd):
                    os.unlink(fn_cmd)
                # file already exists, try again
                continue
            break
        # todo: change below to debug level

        logging.debug('stdout/err log files: %s %s created' % (os.path.abspath(fno), os.path.abspath(fne)))
        with os.fdopen(fdo, 'w') as fp_stdo, \
                os.fdopen(fde, 'w') as fp_stde, \
                os.fdopen(fd_env, 'w') as fp_env, \
                os.fdopen(fd_cmd, 'w') as fp_cmd:
            fp_stdo.write(str(stdo))
            fp_stde.write(str(stde))
            if env:
                import runtime
                env = runtime.env
                fp_env.write(str(pprint.pformat(env)))
            if cmd:
                fp_cmd.write(str(pprint.pformat(cmd)))
        return

    @staticmethod
    def run_daemon_standalone(exec_cmd, env=None):
        """Runs a process via subprocess.popen and returns immediately.
        This is used to run given command parallely in shell. It is standalone. 
        It can be used without any Instantiating the class.

        Returns: <subprocess object>

        Usage:
        >>>
            from tsa.process import ShellExecutor
            exec_str = 'ps -e'
            subprocess_obj = ShellExecutor.run_daemon_standalone(exec_str)
        """
        # todo: replace below with ones from config
        if not env:
            import runtime

            env = runtime.env
        logging.info("Executing command : %s" % exec_cmd)
        return subprocess.Popen(exec_cmd, shell=True, env=env)


class OSProcessHandler:
    """Helps to get pid, kill process in os"""

    def __init__(self, process_name, full_format=False, ssh_con=None, exclude_grep=False):
        """Init with a process name"""
        if not ssh_con:
            if os.name == 'nt':
                raise OSError('windows not supported!')
        self.process_name = process_name
        self.full_format = full_format
        self.ssh_con = ssh_con
        self.exclude_grep = exclude_grep

    def get_pid_list(self):
        """
        Returns:
            a list of pids for the process.
            [] if no process is running with given name
        """
        return OSProcessHandler.__get_pid_list(self.process_name,
                                               self.ssh_con,
                                               self.full_format,
                                               self.exclude_grep)

    def is_running(self):
        """Check if process is running

        Returns:
            True if running, False if not
        """
        if self.get_pid_list():
            return True
        return False

    def kill_processes(self):
        """Kills all processes with process name"""
        OSProcessHandler.kill_process_by_pid(self.get_pid_list(), self.ssh_con)

    @staticmethod
    def __get_pid_list(grep_string, ssh_con, full_format=False, exclude_grep=False):
        """Internal function"""
        pid_list = []
        cmd = "ps --no-headers -e"
        if exclude_grep:
            exclude_grep = ' | grep -v grep'
        else:
            exclude_grep = ''

        if full_format:
            cmd += "f"
            tgs = " | grep -i '%s'" % grep_string
        else:
            tgs = " | grep -i ' %s$'" % grep_string
        tgs += ' %s ' % exclude_grep
        if full_format:
            cmd += tgs + '''|awk '{s="";for(i=8;i<=NF;i++) s=s $i " ";print $2,s}' '''
        else:
            cmd += tgs + "| awk '{print $1,$4}'"
        if not ssh_con:
            sout, serr = ShellExecutor.run_wait_standalone(cmd)
        else:
            sout, serr = ssh_con.execute(cmd)
        for line in sout.split('\n'):
            if grep_string:
                if full_format:
                    if not grep_string in line:
                        continue
                else:
                    if not (line.rpartition(' ')[2] == grep_string):
                        continue
            pid = line.partition(' ')[0]
            if str(pid).strip() != '':
                pid_list.append(pid)
        logging.debug('%s PID list: %s' % (grep_string, ' '.join(pid_list)))
        return pid_list

    @staticmethod
    def is_pid_running(pid, ssh_con=None, exclude_grep=False):
        """Check if process is running

        :param pid: string

        Returns:
            True if running, False if not
        """
        if pid in OSProcessHandler.get_all_pids(ssh_con, exclude_grep):
            return True
        return False

    @staticmethod
    def get_all_pids(ssh_con=None, exclude_grep=False):
        """Returns pids of all running processes
        """
        return OSProcessHandler.__get_pid_list('', ssh_con, exclude_grep)

    @staticmethod
    def kill_process_by_pid(pids, ssh_con=None):  # todo: modify for ssh!
        """Kills a process based on the given pid
        Raises:
            OSError if unable to kill a pid
        """
        if type(pids) == str or type(pids) == str:
            pids = [pids]
        elif not isinstance(pids, list):
            raise TypeError('input must be a pid(string) or list of pids')
        for pid in pids:
            cmd = 'kill -9 %s' % str(pid)
            if not ssh_con:
                sout, serr = ShellExecutor.run_wait_standalone(cmd)
            else:
                sout, serr = ssh_con.execute(cmd)
            if serr:
                if ('No such process' in serr) or (not sout):
                    logging.debug('Already Killed: %s' % pid)
                    continue
                else:
                    raise OSError('Unable to kill pid: %s' % pid)
                    #todo: #check: logic here

        for pid in pids:
            if OSProcessHandler.is_pid_running(pid, ssh_con):
                raise OSError('Kill failed. pid: %s' % pid)
            else:
                logging.debug('Killed: %s' % pid)


if __name__ == '__main__':
    # x = ShellExecutor.run_wait_standalone('dir')
    #    for i in x:
    #        print i
    #    x = ShellExecutor.run_daemon_standalone('dir')
    #print x
    #print x.returncode

    #    zzz = OSProcessHandler('ChainedScorer', full_format = True)
    #    print zzz.get_pid_list()
    import runtime

    ssh = runtime.get_ssh('tsqa32scorer.wsrlab', 'root')
    zzz = OSProcessHandler('java', ssh_con=ssh)
    print('Before killing', zzz.get_pid_list())
    zzz.kill_processes()
    print('After killing', zzz.get_pid_list())

    #test
    #    z = OSProcessHandler('tail')
    ##    print 'process list:', z.get_pid_list()
    #    #test
    #    print 'kill process', z.kill_processes()
    #    #test
    ##    print 'all pids:', OSProcessHandler.get_all_pids()
    #    #test
    ##    print 'is running(1):', OSProcessHandler.is_pid_running('1')
    ##    print 'is running(999999):', OSProcessHandler.is_pid_running('999999')
    #    #test
    ##    print OSProcessHandler.kill_process_by_pid('999999')
    #    pid = '28291'
    #    print 'before kill:', z.is_pid_running(pid)
    ##    print 'kill:', OSProcessHandler.kill_process_by_pid(pid)
    ##    print 'after kill:', z.is_pid_running(pid)


    #    print 'kill:', OSProcessHandler.kill_process_by_pid(['28291', '28292', '28293'])

    # #    print 'after kill:', z.is_pid_running(pid)
    # pass
    #
