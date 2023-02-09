Python Environment
==================

Setup Python 3.4
----------------

::

    PY3_INS_DIR='/home/toolguy/py34/'
    PY3_BIN=$PY3_INS_DIR/bin/python3.4

    sudo yum groupinstall -y development
    sudo yum install -y zlib-dev openssl-devel sqlite-devel bzip2-devel

- Download python

::

    cd ~
    mkdir setup
    cd setup
    wget https://www.python.org/ftp/python/3.4.0/Python-3.4.0.tgz
    tar xzf Python-3.4.0.tgz

- install Python

::

    cd Python-3.4.0
    ./configure --prefix=$PY3_INS_DIR
    make && make altinstall


Python 3.4 package requirements
*******************************
::

    path.py

    PyMySQL
    pymongo
    pymssql

    paramiko
    raven
    selenium

    requests
    beautifulsoup4
    lxml
    simplejson

    sphinx
    pep8
    openpyxl
    XlsxWriter


