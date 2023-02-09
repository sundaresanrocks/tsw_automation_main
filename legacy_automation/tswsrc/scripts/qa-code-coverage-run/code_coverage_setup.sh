#!/bin/sh

# AUTHOR    = Avi Mehenwal
# DATE      = 21th-August-2014
# PURPOSE   = Code Coverage Set Up Script
#
# TRIGGER   = When Failure found in run-qa-full.sh for code coverage part
# Precondtion = Latest build tar should be extracted at ~/workspace/qa-full/cc/ location

####################################################################################

echo $DIR_CC

instrument_code () {
    cd $DIR_CC/tsw/tools/system
    mvn -P instrument package -Dmaven.test.skip=true
    mkdir -p $DIR_CC/instrumented/
    cd $DIR_CC/instrumented/
    find $DIR_CC/tsw/tools/system/ -maxdepth 3 -name *.jar | grep '/target/' | grep -v sources | grep -v thf-url-queues-ejb-remote-client | xargs cp -t $DIR_CC/instrumented/ $1
    find $DIR_CC/instrumented/ -name '*.jar' -print0 -exec unzip -oq {} \;
}


if [ -d $DIR_CC ]
    then echo "Directory Found $DIR_CC"

    if [ -d $DIR_CC/cobertura ]
        then echo "Directory Found $DIR_CC/cobertura"
        else wget -P $DIR_CC/cc http://qaautoui.wsrlab/tsa/cc/cobertura.tar.gz
             tar xzf $DIR_CC/cc/cobertura.tar.gz
    fi

    # Collect dev unit tests
    cd $DIR_CC
    rm cobertura.ser
    find ./ -name cobertura.ser -exec sh $DIR_CC/cobertura/cobertura-merge.sh {} \;
    mv ./cobertura.ser ./dev-unit-tests.ser

    # Create base reference ser files
    cd $DIR_CC/tsw/tools/system/
    mvn clean package -Dmaven.test.skip=true
    cd $DIR_CC
    rm cobertura.ser
    find ./ -name cobertura.ser -exec sh $DIR_CC/cc/cobertura/cobertura-merge.sh {} \;
    mv ./cobertura.ser ./base-reference.ser

    #remove all cobertura.ser files
    find ./ -name cobertura.ser -exec rm -f {} \;

    # Modify POM File
    python $WORKSPACE/src/bin/qa-code-coverage-run/pom_modification.py

    if [ -d $DIR_CC/instrumented ]
        then echo "Directory Found $DIR_CC/instrumented"
             exit
        else instrument_code
             echo "Folder $DIR_CC/instrumented prepared"
    fi

    else echo "ERROR : Directory Not Found $DIR_CC"
         echo "Kindly run jenkins job to get the latest build tar on machine and extract it at ~/workspace/qa-full/cc/ location"
         exit
fi



