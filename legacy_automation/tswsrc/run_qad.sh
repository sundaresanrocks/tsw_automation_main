#!/bin/sh

if [[ !(${WORKSPACE} && ${WORKSPACE-x}) ]]
then
    echo "ERROR: \$WORKSAPCE is not set";
    exit 1;
fi

#setup the environment
export TSW_CONFIG=ci
source $WORKSPACE/tswsrc/scripts/setup-environment.sh


########################################################################################################################
#Execute the tests
########################################################################################################################
py.test -v -s --instafail \
    --junit-xml=../exec/$BUILD_NUMBER/ci.xml \
    $SELECTED_TESTS || true

########################################################################################################################
#update qa dashboard db with test results
python $WORKSPACE/tswsrc/scripts/external_reporting/update_qa_dashboard.py

#start puppet
python $WORKSPACE/tswsrc/scripts/py/remote-service-via-ssh.py puppet start

if  [[ `pgrep puppetd || echo "stopped"` != 'stopped' ]]
then
    echo "INFO: Puppet is running!"
else
    echo "ERROR: Unable to start puppet"
    exit 1
fi
