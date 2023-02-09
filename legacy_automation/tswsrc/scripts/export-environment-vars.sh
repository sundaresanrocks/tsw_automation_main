#!/bin/sh

# Check if $WORKSPACE directory is set. If not, exit immediately.
if [[ ${WORKSPACE} && ${WORKSPACE-x} ]]
then
    echo "INFO: Using env var: \$WORKSPACE=$WORKSPACE";
else
    echo "ERROR: \$WORKSAPCE is not set. It is base folder inside which source, data folders are checked out";
    exit 1;
fi


# Check if $TSW_CONFIG is set. If not, exit immediately.
if [[ ${TSW_CONFIG} && ${TSW_CONFIG-x} ]]
then
    echo "INFO: Using env var: \$TSW_CONFIG=$TSW_CONFIG";
else
    echo "ERROR: \$TSW_CONFIG is not set. Example: ci";
    exit 1;
fi

# Check if $RELEASE_BRANCH_NAME is set. If not, exit immediately.
#if [[ ${RELEASE_BRANCH} && ${RELEASE_BRANCH-x} ]]
#then
#    echo "INFO: Using env var: \$RELEASE_BRANCH=$RELEASE_BRANCH";
#else
#    echo "ERROR: \$RELEASE_BRANCH is not set. Example: WEB_R020";
#    exit 1;
#fi


#Export all the required variables
export PYTHONPATH=$WORKSPACE/tswsrc:$WORKSPACE/packages:$PYTHONPATH
export R_HOME=/usr/lib64/R
export LIBRARY_PATH=/usr/lib64/R/lib
echo "INFO: Exported env var -  \$PYTHONPATH=${PYTHONPATH}"
