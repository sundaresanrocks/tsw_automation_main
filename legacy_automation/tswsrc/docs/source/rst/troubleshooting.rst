Troubleshooting
===============

This page is for known troubleshooting fixes for various issues in Web Systems.

How to access mongo database on tsqathfmongodb01.wsrlab
-------------------------------------------------------
Contributor - Sundar
********************
**Note** : Port 4000 is blocked from some places  … so we won’t be able to connect to tsqathfmongodb01 via port using Mongo VUE

.. highlight:: bash

::

    ssh root@ tsqathfmongodb01.wsrlab
    [root@tsqathfmongodb01 ~]# mongo -u sfcontrol -p 0ystrdm3 tsqathfmongodb01:4000/thfDB
    Few Useful Search via Mongo DB shell: Here tieroneurl is collection name
    db.tieroneurl.find({ "normalizedUrl" : "https://162.243.254.193/4.exe" }).limit(50);
    db.tieroneurl.find({ 'canonicalizedDomain' : '162.243.254.193' })
    db.tieroneurl.find({ "originalUrls" : [  " https://sundar1.com:443/21.exe " ] })



OSError: CompilationError:4 File "java_tsw/py/compile.py", line 78, in compile_java_file
----------------------------------------------------------------------------------------------
Contributor - avimehenwal
********************
When compile.py raises an exception like

.. highlight:: bash

::
    Traceback (most recent call last):
      File "java_tsw/py/compile.py", line 84, in <module>
        compile_java_file('GenericSourceAdapterDriver.java')
      File "java_tsw/py/compile.py", line 78, in compile_java_file
        raise EnvironmentError('CompilationError:' + '\n'.join(errs))
    OSError: CompilationError:4
    +++++ trap_handler_err 30 1
    +++++ echo 'FAILED: line 30, EXIT CODE; 1'
    FAILED: line 30, EXIT CODE; 1


update the value of ``VER`` variable in complie.py file with the latest version from new build


Finding the latest version of java files from the new build
--------------------------------------------------------------
Contributor - avimehenwal
********************
Find the value for ``VER`` variable in compile.py is easy
Run the following command in shell after ``yum update`` ing you test machine

.. highlight:: bash

::
    cd /opt/sftools/java/lib
    ls | grep harvester

This will generate an output like the following where the number appended the package is the current version no

.. highlight:: bash

::
    (tswenv) [toolguy@tsqa64codecoverage lib]$ ls | grep harvester
    daves%20wps%20malware%20harvester-import.jar
    harvesters-1.3.52-drools-helper.jar
    harvesters-1.3.52-for-hadoop.jar
    harvesters-1.3.52.jar
    harvesters-1.3.52-model.jar
    harvesters.jar

Or use this linux command

``ls /opt/sftools/java/lib/ | grep '^harvesters-[0-9].[0-9].[0-9][0-9].jar$' | cut -c12-17``

Catserver build issues
----------------------
Contributor - Abhijeet
**********************
Following are known troubleshooting fixes for some issues faced while making catserver builds:

1. Stuck at "Requesting lock of build table at: Wed Jul 16 11:30:57 2014"

     Sol:
      a. Goto the database configured
      b. Run Query on D2 to reset all locks "update active_agents set is_running = 0, shutdown_now = 0 "

2. I/O error received from sfcheckurl!

     Sol: Caused when there is no change between the current and previous state of the build table when the build was last created.
       a. Put some URLS into the DB with tsw/mindb.py.
       b. Run tman once.
       c. Create build now.


