import subprocess

__author__ = 'manoj'

import os
import re
import pprint
import logging
from path import Path

REPO = Path('/opt/sftools/java/lib/')
VER = '1.3.63'

import runtime


DIR_SRC = Path.joinpath(runtime.WORKSPACE, 'others')#runtime.WORKSPACE.joinpath('/others')
if not DIR_SRC.isdir():
    raise NotADirectoryError('DIR_SRC variable not found!')

DIR_RES = runtime.data_path
if not DIR_RES.isdir():
    raise NotADirectoryError('DIR_RES variable not found!')

JAVA_TSW = DIR_SRC.joinpath('java_tsw')
SRC_MAIN_JAVA = JAVA_TSW.joinpath('src/main/java/')

# todo: get version from properties file!

CLASS_PATH_LIST = ['.',
                   DIR_RES.joinpath('jars/json-simple-1.1.1.jar'),
                   '%(repo)scommons-io-2.0.1.jar',
                   '%(repo)scommons-codec-1.5.jar',
                   '%(repo)scommon-%(ver)s.jar',
                   '%(repo)sharvesters-%(ver)s.jar',
                   '%(repo)scanonicalizer-java-%(ver)s.jar',
                   '%(repo)scsclient-java-%(ver)s.jar',
                   '%(repo)scsclient-wrapper-%(ver)s.jar',
                   '%(repo)sjackson-core-asl-1.9.2.jar',
                   '%(repo)sjackson-mapper-asl-1.9.2.jar',
                   '%(repo)sjackson-xc-1.9.9-redhat-2.jar',
                   SRC_MAIN_JAVA,
                   JAVA_TSW + '/target/classes']
CLASS_PATH = ':'.join(CLASS_PATH_LIST) % {'repo': REPO, 'ver': VER}
logging.warning(CLASS_PATH)
JAVA_COMPILE_TEMPLATE = '/usr/bin/javac -cp %s' % CLASS_PATH + ' '
JAVA_LD_PATH = '/opt/sftools/lib/'
JAVA_TEMPLATE = '/usr/bin/java -cp %s' % CLASS_PATH + '  -Djava.library.path=%s ' % JAVA_LD_PATH
ERROR_COMPILE_PATTERN = '(\d)+\serrors?'


def shell_runner(exec_cmd):
        logging.info("Executing command : %s" % (exec_cmd))
        sp_obj = subprocess.Popen(exec_cmd,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  shell=True)
        stdout, stderr = sp_obj.communicate()
        str_out = stdout.decode("UTF-8")
        str_err = stderr.decode("UTF-8")
        return str_out, str_err


def compile_java_file(file_name):
    if not isinstance(file_name, str):
        raise TypeError('file_name must be str. found: %s' % type(file_name))

    if file_name.rpartition('.')[2] != 'java':
        raise ValueError('file_name must end with .java')

    if not os.path.isdir(SRC_MAIN_JAVA):
        raise NotADirectoryError(SRC_MAIN_JAVA)

    pwd = os.getcwd()
    os.chdir(SRC_MAIN_JAVA)
    stdo, stde = shell_runner(JAVA_COMPILE_TEMPLATE + file_name)
    errs = re.findall(ERROR_COMPILE_PATTERN, stdo + stde)
    os.chdir(pwd)
    if errs:
        logging.error((stdo + stde))
        raise EnvironmentError('CompilationError:' + '\n'.join(errs))
    logging.info('Compilation Success: %s' % file_name)
    return True


if __name__ == '__main__':
    compile_java_file('GenericSourceAdapterDriver.java')
    compile_java_file('CanonFile.java')
    compile_java_file('ContentParserDriver.java')
    compile_java_file('ContentProviderDriver.java')
    compile_java_file('MainServer.java')
    compile_java_file('ContentExtractorDriver.java')