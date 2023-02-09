.. TS Websystems Automation documentation master file
    @author mk

Welcome to TS Websystems Automation Framework's documentation!
==============================================================

Links:
------

+--------------------+-------------------------------------------+--------------------------------------------+
|Location            |URL                                        |Local Path on system                        |
+====================+===========================================+============================================+
|QA Dashboard        |http://qadash.wsrlab/                      |/usr/share/nginx/html                       |
+--------------------+-------------------------------------------+--------------------------------------------+
|This documentation  |http://qadash.wsrlab/docs/                 |/usr/share/nginx/html/docs                  |
+--------------------+-------------------------------------------+--------------------------------------------+
|Reports UI *new*    |http://qadash.wsrlab/tsw-reports/          |/opt/lampp/htdocs/tsw-reports               |
+--------------------+-------------------------------------------+--------------------------------------------+
|Code coverage       |http://qadash.wsrlab/tsw-cc/               |/usr/share/nginx/html/tsw-cc                |
+--------------------+-------------------------------------------+--------------------------------------------+
|Jenkins Server      |http://tsbuild64.wsrlab:8080/              |                                            |
+--------------------+-------------------------------------------+--------------------------------------------+
|Sentry Server       |http://qasentry.wsrlab/                    |                                            |
+--------------------+-------------------------------------------+--------------------------------------------+
|Testlink            |http://tsqatestlinkserver.wsrlab/testlink  |/opt/lampp/htdocs/testlink                  |
+--------------------+-------------------------------------------+--------------------------------------------+
|old reports(<Aug 7) |http://qaautoui.wsrlab/tsa/reports/        |                                            |
+--------------------+-------------------------------------------+--------------------------------------------+

.. init marker for auto update

.. toctree::
    :maxdepth: 1
    :hidden:


    rst/quickstart

    rst/misc

    rst/demo-commands

    rst/setup



    generated/ar

    generated/build

    generated/concat

    generated/conf

    generated/dbtools

    generated/domip

    generated/end2end

    generated/harvesters

    generated/legacy

    generated/lib

    generated/prevalence

    generated/urldb

    generated/scripts



    rst/code-tips

    rst/code-standards

    rst/code-coverage

    rst/write-unit-tests

    rst/rst/how-to-update-docs

    code-tips

    rst/troubleshooting


.. exit marker for auto update


.. todo

How to checkout code?
*********************

.. highlight:: bash

::

    mkdir -p /home/toolguy/workspace/dev
    cd /home/toolguy/workspace/dev

    svn co svn+ssh://svn.research.sys/svn/ts_automation/branches/tsw-ci/tswsrc tswsrc
    svn co svn+ssh://svn.research.sys/svn/ts_automation/branches/tsw-ci/others others
    svn co svn+ssh://svn.research.sys/svn/ts_automation/branches/tsw-ci/packages packages
    svn co svn+ssh://svn.research.sys/svn/ts_automation/branches/tsw-ci/res res

How to configure test environment?
**********************************

.. highlight:: bash

::

    source ~/tswenv/bin/activate;                  # switch to python 3.4+ virtual environment
    export WORKSPACE=~/workspace/dev/;             # root folder for automation
    export TSW_CONFIG=dev;                         # ci or nightly or full section from pytest.ini
    export RELEASE_BRANCH=WEB_R013;                # release branch under test
    export PYTHONPATH=$WORKSPACE/tswsrc:$WORKSPACE/packages:$WORKSPACE/mfsrc:$WORKSPACE/others:.;
    export CLASSPATH_PREFIX=$WORKSPACE/tswsrc/java_tsw/src/main/java; #todo: remove this!
    cd $WORKSPACE/tswsrc/;

How to execute tests?
*********************

.. highlight:: bash

::

    py.test --collect-only;            # collects tests - helps to identify import errors, if any
    py.test;                           # execute all tests with in current directory
    py.test test_sample.py             # execute all tests with in the module
    py.test test_sample.py::TestClassSample             # execute tests in a class
    py.test test_sample.py::test_pass                   # execute one function test
    py.test test_sample.py::TestClassSample::test_err   # execute one unit test
    py.test test_sample.py::test_eval[a];               # execute one generated test

Docstring reference
*******************

Quickstart guide: http://docutils.sourceforge.net/docs/user/rst/quickref.html

Refernce for writing docstrings: http://172.22.81.112/tsa/python%20docstring%20reference.pdf

Directory Structure
-------------------
Top Level - Automation Workspace
********************************
Check out the svn code into this folder

==============================      =========================================
./<<<automation workspace>>>/       Remarks
==============================      =========================================
mfsrc                               mongo framework root
tswsrc                              source code from trunk/src
res                                 test data from trunk/res
others                              java code, comp. analysis, mwgdcc., etc
packages                            libx, json_tools, framework, etc., **must be in python path**
exec                                temporary execution data, logs, reports, etc.,
==============================      =========================================

First Level - tswsrc
********************
All the source code is inside this folder

==========================  =========================================
File/Folder                 Remarks
==========================  =========================================
tswsrc/runci.sh             Run automation in continuous integration mode
tswsrc/pytest.ini           **py.test configuration file**
tswsrc/runtime.py           **Runtime configurations for automation**
tswsrc/filter.ini           Test filter file for plugin pytest-filter
tswsrc/testlink.ini         Test mapping for plugin pytest-testlink
tswsrc/conftest.py          Local test plugins for py.test
tswsrc/conf                 TSW related configurations
tswsrc/lib                  TSW related libraries
tswsrc/scripts              Misc scripts and shell code with permission 0755
tswsrc/docs                 Documentation
==========================  =========================================


Jenkins Jobs
************

+------------------+-------------+-------------------------------------------------------------------------------------+
|Job Name          | Schedule    | Purpose                                                                             |
+==================+=============+=====================================================================================+
|qa-nightly        | Daily       || All executed nightly tests must pass - expected failures = zero                    |
|                  |             || ``qadash:/usr/share/nginx/html/tsw-jenkins/qa-nightly.properties``                 |
|                  |             || email: ``DL MFE Labs Engineering - Web QA Nightly``                                |
+------------------+-------------+-------------------------------------------------------------------------------------+
|qa-full           | Daily       || Daily status of all available tests(including fail/errors)                         |
|                  |             || Periodic code coverage runs, based on day of the week                              |
|                  |             || url: http://qadash.wsrlab/tsw-jenkins/qa-full.properties                           |
|                  |             || ``qadash:/usr/share/nginx/html/tsw-jenkins/qa-full.properties``                    |
|                  |             || email: ``DL MFE Labs Engineering - Web QA``                                        |
+------------------+-------------+-------------------------------------------------------------------------------------+
|qa-ci             | RTQA Build  || At time of RTQA Build                                                              |
|                  |             || email: ``DL MFE Labs Engineering - Web DevQA``                                     |
+------------------+-------------+-------------------------------------------------------------------------------------+

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
