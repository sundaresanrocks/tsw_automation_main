#!/bin/sh

# Code Coverage Directory setup check
codecoverage_check () {
    if [ ! -d $DIR_CC/cobertura ]   # All
        then  echo "Directory not Found : $DIR_CC/cobertura"
              echo "calling cobertura_setup script for first time environment setup"
              source $WORKSPACE/src/bin/qa-code-coverage-run/code_coverage_setup.sh
#    elif [ ! -d $DIR_CC ]       # extraction of package is required
#        then  echo "Directory not Found : cc/WER_R007"
#    elif [ ! -d $WORKSPACE/cc ]
#        then  echo "Directory not Found : cc/WER_R007/cobertura"
#    elif [ ! -d $DIR_CC/instrumented ]
#        then  echo "Directory not Found : cc/WER_R007/instrumented"
#    elif [ ! -d $DIR_CC/tsw ]
#        then  echo "Directory not Found : cc/WER_R007/tsw"
#    elif [ ! -d $DIR_CC/crawler ]
#        then  echo "Directory not Found : cc/WER_R007/crawler"

   fi
}


if [[ !(${WORKSPACE} && ${WORKSPACE-x}) ]]
then
    echo "ERROR: \$WORKSAPCE is not set";
    exit 1;
fi

#setup the environment
source $WORKSPACE/src/bin/setup-environment.sh

echo "setup cobertura environment if required"
TODAY=`date +%A`
# RUN_COVERAGE=`echo $CODE_COVERAGE_DAYS | grep $TODAY`
echo INFO:  [Jenkins]   CODE_COVERAGE_DAY = $CODE_COVERAGE_DAY
echo INFO:  [System]    TODAY = $TODAY


if [[ ${CODE_COVERAGE_DAY} = "" ]]
    then
        echo "INFO: No value selected for CODE_COVERAGE_DAY"

elif [ $CODE_COVERAGE_DAY != $TODAY ]
    then
        echo "INFO: CODE_COVERAGE_DAY not set for TODAY"

# [Avi] Will NOT work for multiple days selected in Jenkins
elif [ $CODE_COVERAGE_DAY = $TODAY ]
    then
        echo "INFO: Code coverage run is enabled for `date +%A`"
        echo "INFO: Using DIR_CC as $DIR_CC"
        # Check for Code Coverage Directory structure set up properly
        codecoverage_check
        echo "INFO: Removing previous qa-full.ser file $(rm -f $DIR_CC/qa-full.ser)"
        echo "INFO: Exporting Environment variables - CLASSPATH_PREFIX=${CLASSPATH_PREFIX}"
        export CLASSPATH_PREFIX=${DIR_CC}/instrumented/*:${DIR_CC}/cobertura/cobertura.jar:$CLASSPATH_PREFIX
        echo "INFO: CLASSPATH_PREFIX = $CLASSPATH_PREFIX"
        echo "INFO: Exporting Environment variables - JAVA_OPTS=${JAVA_OPTS}"
        export JAVA_OPTS="-XX:MaxPermSize=512M -Xms512M -Xmx1000M -Dnet.sourceforge.cobertura.datafile=${DIR_CC}/qa-full.ser"
        echo "INFO: JAVA_OPTS = $JAVA_OPTS"
else
    echo "SKIPPING CODE-COVERAGE --------------"
fi


########################################################################################################################
#Execute the tests
########################################################################################################################

${RUN_PY} -t "Harvester rules tests - full" ${full_harvester_rules}
${RUN_PY} -t "Harvester framework tests - full" ${full_harvester_framework}
${RUN_PY} -t "Agents tests - full" ${full_agents}
${RUN_PY} -t "Legacy tests - full" ${full_legacy}
${RUN_PY} -t "THF tests - full" ${full_thf}
${RUN_PY} -t "Domain IP full_  tests" ${full_domip}
${RUN_PY} -t "Mobile tests - full" ${full_mobile}
${RUN_PY} -t "Content categorization tests - full" ${full_contentcat}
${RUN_PY} -t "Ticketing System tests - full" ${full_ticketing_system}
${RUN_PY} -t "Autorating tests - full" ${full_autorating}
${RUN_PY} -t "MWGDCC tests - full" ${full_mwgdcc}
${RUN_PY} -t "MWGDCC UI tests - full" ${full_mwgdccui}

########################################################################################################################

# start puppet
python $WORKSPACE/tswsrc/scripts/py/remote-service-via-ssh.py puppet start

if  [[ `pgrep puppetd || echo "stopped"` != 'stopped' ]]
    then
        echo "INFO: Puppet is running!"
    else
        echo "ERROR: Unable to start puppet"
        exit 1
fi

