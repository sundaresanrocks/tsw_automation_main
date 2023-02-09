"""
==============================
Runtime configuration settings
==============================

from runtime import runtime

"""

import os
import sys
import six
import platform
import logging
import getpass

from configparser import ConfigParser
from path import Path
import importlib

# Load constants
from conf.files import LOG, SH, BIN, PROP, LIST


__internal_runtime_env_var = '__LOAD_RUNTIME_BOOL'


def reset_runtime():
    """enables runtime to reload itself with new values on next import/reload"""
    os.environ[__internal_runtime_env_var] = 'False'
    importlib.reload(sys.modules[__name__])


def __log_config():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch_format = logging.Formatter('[%(levelname)s] [%(asctime)s] {%(filename)s:%(lineno)d} - %(message)s',
                                  '%y-%m-%d %H:%M:%S')
    ch.setFormatter(ch_format)
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(ch)


# execute config code based on internal variable
if (os.environ.get(__internal_runtime_env_var, 'False')).lower().strip() != 'true':
    os.environ[__internal_runtime_env_var] = 'False'

    # [avimehenwal] enabled logging
    __log_config()

    # check user level before execution
    if platform.system() == 'Linux' and getpass.getuser() == 'root':
        raise RuntimeError('root should not run this script!')

    # load environment variables
    WORKSPACE = os.environ['WORKSPACE']
    if not Path(WORKSPACE).isdir():
        raise EnvironmentError('$WORKSPACE Path not found: %s' % WORKSPACE)

    src_path = Path.joinpath(WORKSPACE, 'tswsrc')
    data_path = Path.joinpath(WORKSPACE, 'res')
    exec_path = Path.joinpath(WORKSPACE, 'exec')

    build_id = os.environ.get('BUILD_NUMBER', '0')
    exec_path.joinpath(build_id).makedirs_p()

    # ensure src_dir and data_dir are present
    if not src_path.isdir():
        raise NotADirectoryError('%s' % src_path)
    if not data_path.isdir():
        raise NotADirectoryError('%s' % data_path)

    # create exec_dir if not found
    exec_path.makedirs_p()
    if not exec_path.isdir():
        raise NotADirectoryError('%s' % exec_path)

    pytest_path = src_path.joinpath('pytest.ini')
    if not pytest_path.isfile():
        raise FileNotFoundError('pytest.ini at %s' % pytest_path)

    # load csv file
    tsw_config = os.environ['TSW_CONFIG']
    _ini_parser = ConfigParser()
    _ini_parser.read(pytest_path)

    # ensure that the required ini section exists
    if tsw_config not in _ini_parser.sections():
        raise LookupError('SectionNotFound: %s in file: %s' % (tsw_config, pytest_path))
    _ini_section = _ini_parser[tsw_config]

    # define ssh keys
    __ssh_connections = {}
    __ssh_keys = {
        'root': {'private': data_path.joinpath('keys/tsa_root_private'),
                 'public': data_path.joinpath('keys/tsa_root.pub')},
        'toolguy': {'private': data_path.joinpath('keys/tsa_toolguy_private'),
                    'public': data_path.joinpath('keys/tsa_toolguy.pub')},
        'sfcontrol': {'private': data_path.joinpath('keys/tsa_sfcontrol_private'),
                      'public': data_path.joinpath('keys/tsa_sfcontrol.pub')},
        'jenkins': {'private': data_path.joinpath('keys/tsa_jenkins_private'),
                    'public': data_path.joinpath('keys/tsa_jenkins.pub')},
        }

    # assert that all keys files exist in data path
    for __user in __ssh_keys:
        for key_type in __ssh_keys[__user]:
            if not __ssh_keys[__user][key_type].isfile():
                raise FileNotFoundError(__ssh_keys[__user][key_type])

    # reset env vars
    from conf.env import ENV
    env = ENV.env
    # env vars from parent environment
    _preload_env_vars = ['CLASSPATH_PREFIX', 'JAVA_OPTS']
    env.update({k: os.environ.get(k) for k in _preload_env_vars if k in os.environ})


def get_ssh(host, user):
    """Returns ssh connection for host with a pre-authorized private key defined in runtime variable __ssh_keys
    :return SSHConnection object
    """
    from libx.ssh import SSHTS
    if user not in __ssh_connections:
        __ssh_connections[user] = {}

    if host not in __ssh_connections[user]:
        __ssh_connections[user][host] = SSHTS(host, username=user, private_key=__ssh_keys[user]['private'])
    return __ssh_connections[user][host]


# Then copy paste nightly things here :) voila ! todo:

class DB:
    # name    = HOST['mssqldb']
    U2_name = _ini_section['mssqldb_u2'] + '_U2'
    D2_name = _ini_section['mssqldb_d2'] + '_D2'
    R2_name = _ini_section['mssqldb_r2'] + '_R2'

    U2_host = _ini_section['mssqldb_u2'] + '.corp.avertlabs.internal'
    D2_host = _ini_section['mssqldb_d2'] + '.corp.avertlabs.internal'
    R2_host = _ini_section['mssqldb_r2'] + '.corp.avertlabs.internal'

    U2_user = R2_user = D2_user = 'sa'
    U2_pass = R2_pass = D2_pass = '1qazse4'

    F2_name = _ini_section['mysqldb'] + '.corp.avertlabs.internal'
    F2_host = _ini_section['mysqldb'] + '.corp.avertlabs.internal'
    F2_user = 'sfcontrol'
    F2_pass = '7890uiojkm'

    T_name = 'telemetry'
    T_host = _ini_section['telemetrydb'] + '.corp.avertlabs.internal'
    T_user = 'sfcontrol'
    T_pass = '0ystrdm3'
    T_telemetry_tables = 'active_tables'

    vm_name = 'name of vm :('
    vm_snap = 'name of snap shot :('

class Mongo:
	user = ''
	passwd = ''
	host = _ini_section['mongodb'] + '.corp.avertlabs.internal'
	dbname = 'MWG_DC_COS_dev'
	port = 27018 #port = 27017

	top_sites_db = 'auto_nightly_db'
	top_sites_collection = 'top_site'

	auto_rating_db = 'auto_nightly_db'
	auto_rating_collection = 'scorers'

	mwgdcc_db = 'auto_nightly_db'
	mwgdcc_rules_package_collection = 'scorers'

	domip_db = 'threat'
	domip_collection = 'domainz'

	class THF:
		user = 'sfcontrol'
		passwd = '0ystrdm3'
		host = _ini_section['domipdb'] + '.corp.avertlabs.internal'
		dbname = 'threat'
		port = 27018#port = 4000
		

	class DOMIP:
		user = ''
		passwd = ''
		host = _ini_section['domipdb'] + '.corp.avertlabs.internal'
		dbname = 'threat'
		port = 27018#port = 27017
		table = 'domainz'

	class URLDB:
		user = ''
		passwd = ''
		host = _ini_section['urldb'] + '.corp.avertlabs.internal'
		dbname = 'auto_urldb'
		#port = 27017
		port = 27018

	class TopSites:
		#user = 'sfcontrol'
		#passwd = '0ystrdm3'
		host = _ini_section['topsitesdb'] + '.corp.avertlabs.internal'
		dbname = 'topsites'
		#port = 4000
		port = 27018
		collection = 'top_site'


class AppServer:
    host = _ini_section['appserver']
    fqdn = host + '.corp.avertlabs.internal'
    host_with_port = fqdn + ':8080'
    url = r'http://' + host + ':8080'


class BuildSys:
    system = _ini_section['buildbox']
    user = 'sfcontrol'
    passwd = 'xdr5tgb'
    su = 'root'
    su_passwd = 'xdr5tgb'
    BP_dir = '/usr2/smartfilter/build/publication_history'
    build_dir = '/usr2/smartfilter/build'

user_agent = '3'
cat_server_host = _ini_section['catserver']
cat_server_port = r'4006'
cat_server_leagacy_port = r'4005'
guvnor_server_host = r'http://' + _ini_section['guvnor'] + '.corp.avertlabs.internal:8080'
guvnor_server_url = guvnor_server_host + '/drools-guvnor-5.1.0/org.drools.guvnor.Guvnor/Guvnor.html'
drool_server_url = guvnor_server_host + 'drools-guvnor-5.1.0/org.drools.guvnor.Guvnor/package/tsw.harvester.%s/LATEST'

# MWG items disabled!
# class Vcenter:
#     vcenter_host = 'vcenter.corp.avertlabs.internal'
#     vcenter_user = 'tsweb'
#     vcenter_passwd = '1234qweasz'

# class MWGDCCEnvVars:
#     dumps = data_path + '/mwgdcc/dumps'
#     resources = data_path + '/mwgdcc/imp/resources'
#     rtc = '/opt/sftools/conf/rtc'
#     ensx_terms = rtc + '/' + 'English/sx.txt'
#
# class MWGDCCUI:
#     classpath = src_path + '/tsa/mwgdcc/ui/target/uitests-1.0-jar-with-dependencies.jar'
#     ui_properties = src_path + '/tsw/conf/mwgdccui.properties'



# update required environment variables

env["SFDBSERVERU2"] = DB.U2_name
env["SFDBSERVERR2"] = DB.R2_name
env["SFDBSERVERD2"] = DB.D2_name
env["SFDBSERVERF2"] = DB.F2_name

env["SFDBMDBSERVER"] = Mongo.host
env["SFDBMDBPORT"] = '27018'
env["CATSERVER_TIMEOUT"] = '2'
env["CATSERVER_HOST"] = cat_server_host
env["CATSERVER_PORT"] = cat_server_leagacy_port
env['DATAHOST'] = '192.168.24.167'
env['DATAPORT'] = '9999'
env['R_HOME'] = '/usr/lib64/R'
env['LIBRARY_PATH'] = '/usr/lib64/R/lib'
