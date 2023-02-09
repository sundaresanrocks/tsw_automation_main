Deploy
======

This is where you describe how the project is deployed in production.

#. Create an user with username as ``user``
#. Give sudo privileges to ``user`` by adding the following line in ``/etc/sudoers``

    ::

        user    ALL=(ALL) NOPASSWD: ALL
#. Open incoming connections in port 80, and 22. Run file ``install_firewall_http_ssh_only.sh``
#. Install nginx ``install_nginx.sh``
#. Install supervisord (python 2.x) ``install_supervisord.sh``
#. Install python 3.4 ``install_py34.sh``
#. Checkout source code to
#. Setup Virtual environment



Generate docs
-------------

#. Run ``make docs`` on the deplyment machine
#. Docs will be present in `_build/pp/docs/`
#. They can accessed via http://csppdash.local/pp/docs
