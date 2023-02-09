#!/bin/sh
#setup the environment
source $WORKSPACE/src/bin/setup-environment.sh
export CLASSPATH_PREFIX=$DIR_SRC/java_tsw/src/main/java:$DIR_CC/cobertura/cobertura.jar:$DIR_CC/instrumented/:$CLASSPATH_PREFIX
export JAVA_OPTS="-XX:MaxPermSize=512M -Xms512M -Xmx1000M -Dnet.sourceforge.cobertura.datafile=$DIR_CC/qa-auto.ser"
find ./ -name cobertura.ser -exec rm -f {} \;
########################################################################################################################
#Execute the tests
########################################################################################################################
${RUN_PY} -t "Nightly - Legacy tests" ${nightly_legacy}
# ${RUN_PY} -t "Nightly - Harvester rules tests" ${nightly_harvester_rules}
${RUN_PY} -t "Nightly - Harvester framework tests" ${nightly_harvester_framework}
${RUN_PY} -t "Nightly - Agents tests" ${nightly_agents}
${RUN_PY} -t "Nightly - Prevalence tests" ${nightly_prevalence}
#${RUN_PY} -t "Nightly - TopSites tests" ${nightly_topsites}
${RUN_PY} -t "Nightly - URLDB" ${nightly_urldb}
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