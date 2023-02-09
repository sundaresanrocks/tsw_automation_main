"""
============================
Snapshot Helper Module
============================

Must call python 2.7 library functions and relay the messages in JSON format

"""

import logging
import runtime
from libx.process import ShellExecutor
import subprocess

PY27_BIN = '/home/toolguy/py27/bin/python2.7 '
VM27_PY = ' bin/py27/vm27.py '


class SnapShotHelper:
    """
    Helps to manage VM snapshots - does not allow more than one snapshots 
    to have same name

    @vm_name: Name of the existing Virtual Machine
    @esx_host: IP/Hostname of ESX Server/VISphere Server
    @esx_user: User name for ESX Server/VISphere Server
    @esx_pass: Password for ESX Server/VISphere Server
    """
    def __init__(self, vm_name, esx_host, esx_user, esx_pass):
        """        """
        if not isinstance(vm_name, str):
            raise TypeError('vm_name must be string, found:%s' % type(vm_name))
        self.sp_obj = None
        # self.vm_name = vm_name
        # self.esx_host = esx_host
        # self.esx_user = esx_user
        # self.esx_pass = esx_pass
        self.cmd = PY27_BIN + VM27_PY + vm_name + ' %(action)s %(snap_name)s'
        self.exec = ShellExecutor()

    def runner(self, exec_cmd, log_path='.'):
        """Runs python 2.7 script and parse values from command line"""
        logging.info("Executing command : %s" % (exec_cmd))
        env = runtime.env
        self.sp_obj = subprocess.Popen(exec_cmd,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       shell=True,
                                       env=env)
        stdout, stderr = self.sp_obj.communicate()
        str_out = str(stdout.decode("UTF-8"))
        str_err = str(stderr.decode("UTF-8"))
        if log_path:
            ShellExecutor._put_stdoe_log_file(log_path, str_out, str_err, prefix_str='vm27', env=env)
        if 'STATUS CODE: SUCCESS' not in str_err:
            err_msg = 'vm: py27 execution failure. cmd: %s' % exec_cmd
            raise EnvironmentError(err_msg)
        return True

    def exists(self, snap_name):
        """Function to check if snapshot exists or not
        Returns True if given snapshot exists. False otherwise
        """
        self.runner(self.cmd % {'snap_name': snap_name,
                                'action': 'exists'})
        logging.info('VM operation - exists: SUCCESS')

    def revert(self, snap_name):
        """Reverts the VM to the given snapshot"""
        self.runner(self.cmd % {'snap_name': snap_name,
                                'action': 'revert'})
        logging.info('VM operation - revert: SUCCESS')

    def create(self, snap_name, desc):
        """Creates a new snap shot with the given name"""
        self.runner(self.cmd % {'snap_name': snap_name,
                                'action': 'create'})
        logging.info('VM operation - create: SUCCESS')
        # raise NotImplementedError("Not yet available for 3.4")

    def delete(self, snap_name):
        """delete the given snap shot name"""
        self.runner(self.cmd % {'snap_name': snap_name,
                                'action': 'delete'})
        logging.info('VM operation - delete: SUCCESS')
        # raise NotImplementedError("Not yet available for 3.4")


def get_snapshot_wrapper(vm_name):
    """
    Wrapper to mange snapshots for VMWare vSphere server
    :param vm_name: Name of the VM
    returns: SnapShotHelper with active connection
    """
    import runtime
    return SnapShotHelper(vm_name,
                          esx_host=runtime.Vcenter.vcenter_host,
                          esx_user=runtime.Vcenter.vcenter_user,
                          esx_pass=runtime.Vcenter.vcenter_passwd)


def unit_tests():
    """Unit tests for calling py27 wrapper functions"""
    vm_obj = get_snapshot_wrapper('vm-manoj')
    vm_obj.delete('snap_not')
    vm_obj.exists('snap_new')

    try:
        vm_obj.exists('snap_not')
    except EnvironmentError:
        logging.info('Environment Error')
    vm_obj.revert('snap_new')
    try:
        vm_obj.revert('snap_not')
    except EnvironmentError:
        logging.info('Environment Error')

if __name__ == '__main__':
    unit_tests()
