#!/bin/sh
export PYTHONPATH=$WORKSPACE:PYTHONPATH
export TSAROOT=$WORKSPACE
TSA_TMP_WORK_DIR=$PWD
cd $WORKSPACE/tsa/mwgdcc/ui/
mvn clean
mvn compile
mvn package
cd $TSA_TMP_WORK_DIR