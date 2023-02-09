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

${RUN_PY} -i -desc "import check" -t "Harvester rules tests - full" ${full_harvester_rules}
${RUN_PY} -i -desc "import check" -t "Harvester framework tests - full" ${full_harvester_framework}
${RUN_PY} -i -desc "import check" -t "Agents tests - full" ${full_agents}
${RUN_PY} -i -desc "import check" -t "Legacy tests - full" ${full_legacy}
${RUN_PY} -i -desc "import check" -t "THF tests - full" ${full_thf}
${RUN_PY} -i -desc "import check" -t "Domain IP full_  tests" ${full_domip}
${RUN_PY} -i -desc "import check" -t "Mobile tests - full" ${full_mobile}
${RUN_PY} -i -desc "import check" -t "Content categorization tests - full" ${full_contentcat}
${RUN_PY} -i -desc "import check" -t "Ticketing System tests - full" ${full_ticketing_system}
${RUN_PY} -i -desc "import check" -t "Autorating tests - full" ${full_autorating}
${RUN_PY} -i -desc "import check" -t "MWGDCC tests - full" ${full_mwgdcc}
${RUN_PY} -i -desc "import check" -t "MWGDCC UI tests - full" ${full_mwgdccui}

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

