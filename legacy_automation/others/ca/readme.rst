Configuration details
=====================
    
Note:
*****
Ports used:

	#. Celery flower: 8088
	#. Canonicalizer: 8080
	#. RabbitMQ: 8010

RabbitMQ credentials:
*********************
    #. Virtual host: myvhost
    #. User name: myuser
    #. Password: mypassword


Celery Workers
==============
Start workers - more info at ``http://celery.readthedocs.org/en/latest/userguide/workers.html``

#. Start Avira

::

    set PYTHONPATH=c:\src;c:\src\ca\clients;
    c:
    cd src\ca\clients
    celery -A avira worker --queue avira --loglevel=info --concurrency=1 

#. Start results processor

::

    set PYTHONPATH=c:\src;c:\src\ca\clients;
    c:
    cd src\ca\clients
    celery -A results worker --queue results --loglevel=info --concurrency=1 

#. Start sdkclient_task from linux machine(172.19.216.202 aka false positive machine)

::

    # Note: /home/toolguy/sdclient must be present!
    cd ~/ca-test
    export PYTHONPATH=$PWD/ca/clients:$PWD
    #### PYTHONPATH=/home/toolguy/ca-test/ca/clients:/home/toolguy/ca-test
    cd ca/clients
    celery -A sdkclient_task worker --queue sdkclient --loglevel=info --concurrency=1

Steps to setup a box for competitor analysis
============================================

#. Install python 3.4 32 bit on the machine at location c:\py34
#. Set proper python paths - c:\py34; c:\py34\scripts; and others as required.

pip install the following modules:
    selenium
    celery
    pillow
    requests
    pywin32 32bit version on windows

    
Setup rabbitmq(server, already setup!)
======================================
1. Install rabbitmq
::
    wget -O /etc/yum.repos.d/epel-erlang.repo http://repos.fedorapeople.org/repos/peter/erlang/epel-erlang.repo
    wget http://pkgs.repoforge.org/wxGTK/wxGTK-2.8.10-1.el5.rf.x86_64.rpm
    yum localinstall wxGTK-2.8.10-1.el5.rf.x86_64.rpm --nogpgcheck
    yum install erlang

    wget http://www.rabbitmq.com/releases/rabbitmq-server/v3.3.4/rabbitmq-server-3.3.4-1.noarch.rpm
    yum localinstall --nogpgcheck rabbitmq-server-3.3.4-1.noarch.rpm

    cat >>/etc/rabbitmq/rabbitmq.config <<EOL
%% -*- mode: erlang -*-
%% ----------------------------------------------------------------------------
%% RabbitMQ Sample Configuration File.
%%
%% See http://www.rabbitmq.com/configure.html for details.
%% ----------------------------------------------------------------------------
[
 {rabbit,
  [%%
    {tcp_listeners, [{"0.0.0.0", 8010}]}
   %% {tag_queries, []}
  ]}
].
    
EOL
    chkconfig rabbitmq-server on
    /etc/init.d/rabbitmq-server start

2. Configure users

::

    sudo rabbitmqctl add_user myuser mypassword
    sudo rabbitmqctl add_vhost myvhost
    sudo rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"

    rabbitmqctl list_users
    rabbitmqctl status

2. Create python virtual environment for django

::

    ~/py34/bin/pyvenv-3.4 ~/djenv
    source ~/djenv/bin/activate

3. Install celery, celery flower

::
    pip install celery
    pip install celery flower

4. Start celery flower

::

    /root/djenv/bin/celery flower -address=0.0.0.0 --broker="amqp://myuser:mypassword@qadash.wsrlab:8010/myvhost" -port=8088 --broker_api="http://myuser:mypassword@qadash.wsrlab:15672/api"

