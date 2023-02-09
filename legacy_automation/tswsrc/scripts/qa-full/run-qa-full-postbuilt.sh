#!/bin/sh

# AUTHOR    = Avi Mehenwal
# DATE      = 18th-August-2014
# PURPOSE   = Code Coverage Post Build Part.
#             Placed as post built coz if any test suit fails we would still have code coverage reports
# TRIGGER   = Managened by Jenkins PostCondition Check on log 'INFO: Code coverage run is enabled for'

####################################################################################

# neede improvement with environment variables [avimehenwal] check if it could access jenkins env variable
DIR=workspace/qa-full
RELEASE_BRANCH=WEB_R010
export WORKSPACE=/home/toolguy/$DIR
export DIR_SRC=$WORKSPACE/src
export DIR_RES=$WORKSPACE/res
export DIR_CC=$WORKSPACE/cc/$RELEASE_BRANCH
export PYTHONPATH=$DIR_SRC:$PYTHONPATH;
export ACTIVE_CONFIG=nightly.x86_64
export ACTIVE_PROJECT=tsw;

if [ ! -f $DIR_CC/base-reference.ser ]
    then
        echo "INFO : cobertura : File not found $DIR_CC/base-reference.ser"
        exit
elif [ ! -f $DIR_CC/dev-unit-tests.ser ]
    then
        echo "INFO : cobertura : File not found $DIR_CC/dev-unit-tests.ser"
        exit
elif [ ! -f $DIR_CC/qa-full.ser ]
    then
        echo "INFO : cobertura : File not found $DIR_CC/qa-full.ser"
        exit
#elif [ ! -d $DIR_CC/instrumented ]
#    then
#        echo "INFO : cobertura : File not found $DIR_CC/instrumented"
#        exit
elif [ ! -d $DIR_CC/cobertura ]
    then
        echo "INFO : cobertura : File not found $DIR_CC/cobertura"
        exit
fi

REPORTS_DIR=`date +%Y-%m-%d-%T`
mkdir -pv $DIR_CC/CODE_COVERAGE_REPORTS/$REPORTS_DIR
cd $DIR_CC/cobertura
echo "INFO : Cobertura : Directory Created $REPORTS_DIR"

if [ `ls | grep .ser | wc --line` -ne 0  ]
    then
        echo "INFO : Cobertura : removing .ser files"
        rm -f *.ser
fi
cp -t $DIR_CC/cobertura $DIR_CC/qa-full.ser $DIR_CC/base-reference.ser $DIR_CC/dev-unit-tests.ser

# QA Only
sh cobertura-merge.sh base-reference.ser qa-full.ser
sh cobertura-report.sh --destination $DIR_CC/CODE_COVERAGE_REPORTS/$REPORTS_DIR/qa-only/
echo "INFO : Cobertura : QA Only reports Generated"

# DEV Only
echo "INFO : removing cobertura.ser"
rm -f cobertura.ser
sh cobertura-merge.sh base-reference.ser dev-unit-tests.ser
sh cobertura-report.sh --destination $DIR_CC/CODE_COVERAGE_REPORTS/$REPORTS_DIR/dev-only/
echo "INFO : Cobertura : DEV Only reports Generated"

# DEV+QA Only
echo "INFO : removing cobertura.ser"
rm -f cobertura.ser
sh cobertura-merge.sh dev-unit-tests.ser qa-full.ser base-reference.ser
sh cobertura-report.sh --destination $DIR_CC/CODE_COVERAGE_REPORTS/$REPORTS_DIR/dev+qa/
echo "INFO : Cobertura : QA+DEV reports Generated"

echo "INFO : Cobertura : End of post cobertura script"

echo "INFO : Post Clean-up"
echo "Removing `ls | grep *.ser`"
rm -f *.ser
cd $DIR_CC

#echo "Removing qa-full.ser"
#rm -f qa-full.ser
echo "END"