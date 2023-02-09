#!/bin/sh

if [[ !(${WORKSPACE} && ${WORKSPACE-x}) ]]
then
    echo "ERROR: \$WORKSAPCE is not set";
    exit 1;
fi

#setup the environment
source $WORKSPACE/src/bin/setup-environment.sh


########################################################################################################################
#Execute the tests
########################################################################################################################



########################################################################################################################
#start puppet
python $WORKSPACE/tswsrc/scripts/py/remote-service-via-ssh.py puppet start

if  [[ `pgrep puppetd || echo "stopped"` != 'stopped' ]]
then
    echo "INFO: Puppet is running!"
else
    echo "ERROR: Unable to start puppet"
    exit 1
fi

