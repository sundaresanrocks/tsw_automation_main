Demo Commands
=============

start ftp server
****************

.. highlight:

::

    python bin/servers/ftp_service.py user:pass:${DIR_RES}/harvesters/driver/content_providers/server_root/

start http server
*****************
::

    python bin/servers/http_service.py 18000 user:pass ${DIR_RES}/harvesters/driver/content_providers/server_root/

content provider tests
**********************
::

    python run.py -t "m test" harvesters/contentprovider/ftp.File harvesters/contentprovider/ftp.FTP harvesters/contentprovider/ftp.HTTP
    python run.py -t "m test" harvesters/contentprovider/ftp.FTP
    python run.py -t "m test" harvesters/contentprovider/ftp.HTTP

    python run.py -t "m test" harvesters/contentprovider/ftp.File harvesters/contentprovider/ftp.FTP harvesters/contentprovider/ftp.HTTP agents/jafw.Prev1.test agents/jafw.Prev2.test


    python run.py -t "prev client" agents/jafw.Prev1.test
    python run.py -t "prev client" agents/jafw.Prev2.test

