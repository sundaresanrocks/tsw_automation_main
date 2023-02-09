"""
===========================================
Web Systems Build Deployment Check Utility.
===========================================

Uasge:
~/py34/bin/python3.4 rpm-check-util.py -k tsa_root_private -r 9283 qa-rpms.properties

Note: SVN revision can be obtained via jenkins

"""

__author__ = 'manoj'


import logging
import os
import argparse
try:
    from brm_required_modules import Properties, SSHConnection
except:
    from .brm_required_modules import Properties, SSHConnection
logging.getLogger().setLevel(logging.INFO)

#globals
ssh_connections = {}
errors = []


def main(svn_revision, private_key, prop_file, user_name):
    """

    :param svn_revision: revision number used for rpm checks
    :param private_key: path to private key file
    :param prop_file: path to properties file
    :param user_name: user name for remote ssh connections
    :return: Exit code - 0 = success, 1 = fail
    """

    empty_rpm_hosts = []
    error_hosts = []
    arg_errors = []
    match_count = 0

    #check for input errors
    if not os.path.isfile(private_key):
        msg = "Private key file: %s was NOT FOUND" % private_key
        arg_errors.append(msg)

    if not os.path.isfile(prop_file):
        msg = "Properties file: %s was NOT FOUND" % prop_file
        arg_errors.append(msg)

    if len(user_name) < 1:
        msg = "Not a valid user name. Must be at least of length 1"
        arg_errors.append(msg)

    if int(svn_revision) < 9000:
        msg = "Invalid revision number: %s. Must be greater than 9000" % svn_revision
        arg_errors.append(msg)

    if arg_errors:
        for msg in arg_errors:
            logging.error(msg)
        os._exit(1)

    prop = Properties()
    prop.load(open(prop_file))

    #Convert comma separated values into a list of strings
    host_d = {key: prop[key].strip().split(',') if prop[key].strip() != '' else [] for key in prop.getPropertyDict()}

    #find keys with empty values and add it to a new list - empty_rpm_hosts
    for host in host_d:
        if not host_d[host]:
            empty_rpm_hosts.append(host)
    #find keys with empty values from host_d
    for host in empty_rpm_hosts:
        del host_d[host]
        logging.warning('Empty rpm package details for host: %s' % host)

    #make ssh connections
    for host in host_d:
        try:
            ssh_connections[host] = SSHConnection(host, username=user_name, private_key=private_key)
            logging.info('Connected to host: %s via ssh' % host)
        except:
            logging.error('Unable to connect to host: %s' % host)
            error_hosts.append(host)
    #remove error hosts from host_d
    for host in error_hosts:
        del host_d[host]

    #check for rpm version
    for host, rpm_list in host_d.items():
        try:
            for rpm_name in rpm_list:
                ssh_obj = ssh_connections[host]
                remote_rpms = ssh_obj.get_rpm_list(rpm_name)
                if len(remote_rpms) != 1:
                    #todo: separate below into 2 use cases - 0=no rpm installed >2 make suffix to be unique
                    # handle error case by skipping rpm
                    logging.error('0 or 2+ RPMs were returned for pattern:%s' % rpm_name + ' on host: %s' % host)
                    if host not in error_hosts:
                        error_hosts.append(host)
                    continue
                remote_rpm_revision = remote_rpms[0].rpartition('-')[2].strip()
                if int(remote_rpm_revision) == int(svn_revision):
                    # success!
                    match_count += 1
                    logging.info('Revision check - ok for rpm: %s on host: %s' % (rpm_name, host))
                else:
                    # handle error case
                    if host not in error_hosts:
                        error_hosts.append(host)
                    logging.error('Revision mismatch for rpm: %s on host: %s' % (rpm_name, host))
        except:
            # handle error case
            logging.error('Unknown error while processing on host: %s' % host)
            if host not in error_hosts:
                error_hosts.append(host)

    #diplay summary information
    summary = 'Summary\nHosts with errors: %s' % len(error_hosts) + \
              '\nNumber of successful RPM version matches: %s' % match_count
    if error_hosts:
        logging.error('error hosts - %s' % ', '.join(error_hosts))
        logging.error(summary)
        os._exit(1)
    else:
        # exit with return code 0 - success
        logging.info(summary)
        os._exit(0)

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Web Systems Build Deployment Check Utility.')
    parser.add_argument('-k', '--private-key',
                        help='Private key for remote hosts',
                        action='store',
                        required=True)
    parser.add_argument('-r', '--revision',
                        help='SVN revision number',
                        action='store',
                        required=True)
    parser.add_argument('-u', '--user',
                        help='User name',
                        action='store',
                        required=False,
                        default='root')
    parser.add_argument('properties_file',
                        help='Properties file with host name as key and '
                             'comma separated list of rpm package names as value')

    opts = parser.parse_args()

    main(opts.revision.strip(),
         opts.private_key.strip(),
         opts.properties_file.strip(),
         opts.user.strip())


