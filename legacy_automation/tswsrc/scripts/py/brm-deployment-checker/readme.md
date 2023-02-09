Readme
======

Requirements
------------

#. Python 3.4
#. paramiko
#. argparse


Install python 3.4
==================
PY3_INS_DIR=$(echo ~/py34/)
PY3_BIN=$PY3_INS_DIR/bin/python3.4

mkdir -p /tmp/setup-py34
cd /tmp/setup-py34

wget --no-check-certificate https://www.python.org/ftp/python/3.4.0/Python-3.4.0.tgz
tar xzf Python-3.4.0.tgz

cd Python-3.4.0
./configure --prefix=$PY3_INS_DIR
make && make altinstall

~/py34/bin/pip


~/py34/bin/pip3.4 install paramiko
~/py34/bin/pip3.4 install argparse


Run script
==========
~/py34/bin/python3.4 rpm-check-util.py -k tsa_root_private -r 9283 qa-rpms.properties

Note: SVN revision can be obtained via jenkins
-k can point to automation keys or hudsen/jenkins private key that is used for deployments
