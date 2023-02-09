Quick start
===========

Setup Python 3.4
****************

#. Copy from x86 or x64 bit version of python tar.gz and extract it.

**Note: The packaged version is not available currently. See how to setup python in detail

.. highlight:: bash

::

    cd ~
    rm -f py.tar.gz
    rm -f tswenv.tar.gz
    wget http://172.22.81.112/tsa/py34.tar.gz
    wget http://172.22.81.112/tsa/tswenv.tar.gz
    tar xzf py34.tar.gz
    tar xzf tswenv.tar.gz

    source tswenv/bin/activate


Add to nightly automation
*************************

*Add your run details to shell script*
``tsw/bin/remote_full_test.sh`` is called remotely to execute the tests. Add new run details if necessary.

.. highlight:: bash

::

    cd /home/toolguy/dev/src
    vi tsw/bin/remote_full_test.sh

    svn ci

*Add suites to jenkins initialization file* at remote machine ``root@172.22.81.112``

.. highlight:: bash

::

    vi /opt/lampp/htdocs/tsa/jenkins/nightly.txt

Contents of ``nightly.txt``

::

    harvesters=harvesters/tc/saas.SaaS, harvesters/tc/apwg.APWG,
    legacy=tsw/tc/canon.IP, tsw/tc/canon.URL,

Start tests from jenkins
************************
#. Go to jenkins location at http://tsbuild02.wsrlab:8080/job/QANightlyTest/
#. Click on Build
#. Select the list of tests that you want to execute by using ``Ctrl+Click`` in the list boxes
#. Click on Build again to start the tests

Monitor the tests
*****************
#. Go to jenkins location at http://tsbuild02.wsrlab:8080/job/QANightlyTest/
#. Hover the mouse over the currently running build id.
#. Click ``Console`` in the popup that appears



Machines
========

Testlink Automation user: tswauto Pass: tsw
-------------------------------------------
URL: http://tsqatestlink.wsrlab/
Shell credentials – bitnami/1qazse4
Hostname : tsqatestlink.wsrlab
IP: 172.22.81.20
Admin credentials: <DO NOT USE UNLESS REQUIRED> user/1qazse4
Testlink DB config files : /opt/bitnami/apps/testlink/htdocs/config_db.inc.php

