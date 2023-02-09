#!/bin/sh


#source ~/tswenv/bin/activate; python /home/toolguy/workspace/qa-ci/tswsrc/scripts/servers/ftp_service.py user:pass:/home/toolguy/workspace/qa-ci/res/harvesters/driver/content_providers/server_root/ &
#source ~/tswenv/bin/activate; python /home/toolguy/workspace/qa-ci/tswsrc/scripts/servers/http_service.py 8001 user:pass /home/toolguy/workspace/qa-ci/res/harvesters/driver/content_providers/server_root/ &

# Set traps for error - ensures that all calls return with 0 exit code
set -o errtrace
trap_handler_err() {
    echo "FAILED: line $1, EXIT CODE; $2"
    exit 1
}
trap 'trap_handler_err $LINENO $?' ERR


# Check if $WORKSPACE directory is set. If not, exit immediately.
if [[ ${WORKSPACE} && ${WORKSPACE-x} ]]
then
    echo "INFO: Using env var: \$WORKSPACE=$WORKSPACE";
else
    echo "ERROR: \$WORKSAPCE is not set. It is base folder inside which src, res, packages, and others are checked out";
    exit 1;
fi


#Activate python environment, export envrieonment variables, switch directory
echo "INFO: Activating python virtual environment at /home/toolguy/tswenv/bin/activate"
source /home/toolguy/tswenv/bin/activate

echo "INFO: Switching to $WORKSPACE/tswsrc"
cd ${WORKSPACE}/tswsrc

#export environment variables
echo "INFO: Setting environment variables from \$WORKSPACE/tswsrc/scripts/export-environment-vars.sh"
source ${WORKSPACE}/tswsrc/scripts/export-environment-vars.sh

# Create a temp file with list of environments
env > /tmp/env_$BUILD_NUMBER

#stop puppet if it is running
if  [[ `pgrep puppetd || echo "stopped"` != 'stopped' ]]
then
    echo "INFO: Stopping puppet"
    python ${WORKSPACE}/tswsrc/scripts/py/remote-service-via-ssh.py puppet stop
    if  [[ `pgrep puppetd || echo "stopped"` != 'stopped' ]]
    then
        echo "FAILED: Puppet is still running. Unable to stop puppet."
        exit 2;
    fi
fi
echo "INFO: Puppet is not running. Environment is ready for automation execution"


#rpm revision checks
#python ${WORKSPACE}/tswsrc/scripts/rpm-revision-checks.py


#mssql database checks
#python ${WORKSPACE}/tswsrc/scripts/mssql-odbc-coneection-checks.py


#start http server
#todo: ensure there are no previous processes that use port 2121 using
FTP_STATUS=`netstat -tunlp | grep ':2121' && echo "RUNNING" || echo "NOT RUNNING"`
FTP_CMD="nohup python $WORKSPACE/tswsrc/scripts/servers/ftp_service.py user:pass:$WORKSPACE/res/tsw/harvesters/driver/content_providers/server_root/ &"

if [[ $FTP_STATUS = "NOT RUNNING" ]]
then
    echo "FTP SERVER not running"
    echo "Tip: Start it by command $FTP_CMD "
    exit 1
fi

#todo: ensure there are no previous processes that use port 8001 using
HTTP_STATUS=`netstat -tunlp | grep ':8001' && echo "RUNNING" || echo "NOT RUNNING"`
HTTP_CMD="nohup python $WORKSPACE/tswsrc/scripts/servers/http_service.py 8001 user:pass $WORKSPACE/res/tsw/harvesters/driver/content_providers/server_root/ &"
if [[ $HTTP_STATUS = "NOT RUNNING" ]]
then
    echo "HTTP SERVER not running"
    echo "Tip: Start it by command $HTTP_CMD"
    exit 1
fi

#copy versioned log4j to conf
cp $WORKSPACE/res/conf/log4j.xml /opt/sftools/conf/
