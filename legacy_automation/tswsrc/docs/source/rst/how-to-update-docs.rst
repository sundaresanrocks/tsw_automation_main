How to update docs
==================

Steps
-----

#. Set virtual environment to python 3.4
#. Set all required environment vars for automation
#. Run docs-update.py - creates rst in ``sources/generated`` as part of auto docs
::

    cd docs/
    python docs-update.py

#. Make documentation - builds html documentation
::

    make html

#. Zip the build\html folder
::

    cd docs/build
    rm html.tar.gz
    tar zcf html.tar.tz html

#. Upload it to ``172.22.81.112`` machine
::

    scp html.tar.gz root@172.22.81.112:/opt/lampp/htdocs/docs

#. Extract the html.tar.gz
#. Clear browser cache and verify if the updated docs are available

