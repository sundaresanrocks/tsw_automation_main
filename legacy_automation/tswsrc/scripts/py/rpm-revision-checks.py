"""
Simple script to check if all remote hosts have same revision number.

"""

__author__ = 'manoj'

import os
import logging
logging.getLogger().setLevel(logging.INFO)


if __name__ == '__main__':
    import runtime
    from conf.env.nightly import get_env_properties

    HOST = get_env_properties()
    LOCALHOST_CORE_REV = runtime.get_ssh(HOST['localhost'] + '.wsrlab', 'root')._get_rpm_list('wsr-core')[0].rpartition('-')[2]

    errors = []

    def check_revision_via_ssh(host_key, rpm_prefix):
        try:
            rev = runtime.get_ssh(HOST[host_key] + '.wsrlab', 'root')._get_rpm_list(rpm_prefix)[0].rpartition('-')[2]
            if rev != LOCALHOST_CORE_REV:
                msg = 'Wrong revision in ' + HOST[host_key] + ' Expected:%s Found:%s' % (
                    LOCALHOST_CORE_REV, rev) + ' for package prefix: %s' % rpm_prefix
                errors.append(msg)
                logging.error(msg)
            else:
                logging.info('Revision matches for host: %s for package:%s' % (HOST[host_key], rpm_prefix))
        except:
            msg = 'Unable to get revision details for package:%s on host: %s' % (rpm_prefix, HOST[host_key])
            errors.append(msg)
            logging.error(msg)

    check_revision_via_ssh('localhost', 'wsr-canonicalizer')
    check_revision_via_ssh('catserver', 'wsr-core')
    check_revision_via_ssh('catserver', 'wsr-canonicalizer')
    check_revision_via_ssh('appserver', 'wsr-core')
    check_revision_via_ssh('appserver', 'wsr-j2ee-app')
    check_revision_via_ssh('appserver', 'wsr-canonicalizer')
    check_revision_via_ssh('buildbox', 'wsr-core')
    check_revision_via_ssh('buildbox', 'wsr-canonicalizer')

    if errors:
        logging.error('\n\nTotal Errors: %s\n\n' % len(errors))
        os._exit(1)
    else:
        logging.info('SUCCESS: No errors found!')