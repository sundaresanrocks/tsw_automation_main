Code Coverage using cobertura
=============================

Copy source code via Jenkins
----------------------------

Run the jenkins job with correct release branch and target system

``http://tsbuild64.wsrlab:8080/job/QA-Compress-for-code-coverage/build?delay=0sec``

New tar.gz file will be present in ``/tmp/`` folder

Extract the to the target directory
This is a one time setup.
::

    export RELEASE_BRANCH_NAME=WEB_R010
    export WORKSPACE=/home/toolguy/workspace/qa-full/
    export DIR_CC=$WORKSPACE/cc/$RELEASE_BRANCH_NAME

    mkdir -p $WORKSPACE/cc
    mkdir -p $DIR_CC
    cp /tmp/$RELEASE_BRANCH_NAME.tar.gz $WORKSPACE/cc/
    cd $WORKSPACE/cc
    tar xzf $RELEASE_BRANCH_NAME.tar.gz
    cd $DIR_CC

Download and setup cobertura
----------------------------
This is a one time setup.
.. highlight :: bash

::

    cd $DIR_CC
    wget http://qaautoui.wsrlab/tsa/cc/cobertura-2.0.3.tar.gz
    tar xzf cobertura-2.0.3.tar.gz
    cd $DIR_CC


Collect unit test runs
----------------------
This is a one time setup. Ensure that you do not delete dev-unit-tests.ser.
The report generated from the output ser file of this step contains execution data for developer(java) unit tests.
::

    cd $DIR_CC
    rm cobertura.ser
    find ./ -name cobertura.ser -exec sh ./cobertura/cobertura-merge.sh {} \;
    mv ./cobertura.ser ./dev-unit-tests.ser

Create base reference ser files
-------------------------------
The report generated from the output ser file of this step contains with zero lines of execution data.
::

    cd $DIR_CC/tsw/tools/system/
    mvn clean cobertura:cobertura -Dmaven.test.skip=true

    cd $DIR_CC
    rm cobertura.ser
    find ./ -name cobertura.ser -exec sh ./cobertura/cobertura-merge.sh {} \;
    mv ./cobertura.ser ./base-reference.ser

    #remove all cobertura.ser files
    find ./ -name cobertura.ser -exec rm -f {} \;


Generate Base and QA reports:
-----------------------------

Base report - zero covered lines

. highlight :: bash

::


    cd $DIR_CC/cobertura
    rm *.ser
    cp -t . ../base-reference.ser
    sh cobertura-merge.sh base-reference.ser
    sh cobertura-report.sh --destination ../base-zero/

Dev Only report

. highlight :: bash

::


    cd $DIR_CC/cobertura
    rm *.ser
    cp -t . ../dev-unit-tests.ser
    sh cobertura-merge.sh dev-unit-tests.ser
    sh cobertura-report.sh --destination ../dev-only/


Modify POM File
---------------
If perl scripts don't work, do these steps manually.

#. Remove/comment the cobertura goal

::

    cd $DIR_CC/tsw/tools/system/
    perl -e "s|<goal>cobertura</goal>|<\!--<goal>cobertura</goal>-->|g;" -pi.save pom.xml


Build Instrumented jars
-----------------------
#. Copy the root folder from jenkins for current release(WEB_R010)
#. change directory to the folders of pom files(listed at the end) and run the mvn command for each of the folders

::

    cd $DIR_CC/tsw/tools/system
    mvn -P instrument package -Dmaven.test.skip=true

Copy instrumented jars to new directory
---------------------------------------
The instrumented jars must be copied to ``$DIR_CC/instrumented/``
::

    mkdir -p $DIR_CC/instrumented/
    cd $DIR_CC/instrumented/
    find $DIR_CC/tsw/tools/system/ -maxdepth 3 -name *.jar | grep '/target/' | grep -v sources | grep -v thf-url-queues-ejb-remote-client | xargs cp -t $DIR_CC/instrumented/ $1
    find $DIR_CC/instrumented/ -name '*.jar' -print0 -exec unzip -oq {} \;

Run Instrumented code:
----------------------

#. replace all jar files in /opt/sftools/java/lib with instrumented jar files

::

    export CLASSPATH_PREFIX=$DIR_SRC/java_tsw/src/main/java:$DIR_CC/cobertura/cobertura.jar:$DIR_CC/instrumented/:$CLASSPATH_PREFIX:.
    export JAVA_OPTS="-XX:MaxPermSize=512M -Xms512M -Xmx1000M -Dnet.sourceforge.cobertura.datafile=$DIR_CC/qa-auto.ser"

    cd /home/toolguy/code-coverage/WEB_R010/tsw/tools


Generate reports:
-----------------


::

    export DIR_CC_SRC=$(find /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/ -type d -name java | grep 'src/main/java$' | xargs echo)


QA Only report

. highlight :: bash

::

    cd $DIR_CC/cobertura
    rm *.ser
    cp -t . ../qa-auto.ser ../base-reference.ser
    sh cobertura-merge.sh base-reference.ser qa-auto.ser
    sh cobertura-report.sh --destination ../qa-only/ $DIR_CC_SRC

Without source:
::

    sh cobertura-report.sh --destination ../qa-only/


Dev + QA combined report

. highlight :: bash

::

    cd $DIR_CC/cobertura
    rm *.ser
    cp -t . ../dev-unit-tests.ser ../qa-auto.ser ../base-reference.ser
    sh cobertura-merge.sh dev-unit-tests.ser qa-auto.ser base-reference.ser
    sh cobertura-report.sh --destination ../dev+qa/

Fix jboss EAP build issue
-------------------------
::

    cd ~/.m2/repository
    wget http://tsdevnfs01.wsrlab/eap-repo/jboss-eap-6.1.1-repo-patched.zip
    unzip jboss-eap-6.1.1-repo-patched.zip

===============
UNVERIFIED DOCS
===============
The following docs are not verified and these are present just as is. They will not work most probably.


Install instrumented jars to local maven repository
---------------------------------------------------
Sometimes, not all jars might be present. You might need to install the right jars into local mvn repository
The groupId, version and file must be correctly set as in pom.xml
::

    mvn install:install-file -DgroupId=man-local -DartifactId=common -Dversion=1.3.48 -Dpackaging=jar -Dfile=/opt/sftools/java/lib/common-1.3.48.jar

Build ear(Not working)
----------------------

Execute the following command in each of the respective folders (mwgdc, coreui, scorers, dictionary-core, harvesters,
common, thf-url-queues
::

    mvn -P instrument clean package install -Dmaven.test.skip=true

Copy the required jars into the ear target folder
::

    cd /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/j2ee-app/target/j2ee-app-1.3.48

    cp /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/mwgdc-ui/target/mwgdc-ui-1.3.48.war mwgdc-ui.war
    cp /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/coreui/target/coreui-1.3.48.war coreui.war
    cp /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/scorers/target/scorers-1.3.48.jar scorers.jar
    cp /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/thf-url-queues/target/thf-url-queues-1.3.48.jar     thf-url-queues.jar
    cp /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/dictionary-core/target/dictionary-core-1.3.48.jar  dictionary-core.jar
    cp /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/harvesters/target/harvesters-1.3.48.jar harvesters.jar
    cp /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/common/target/common-1.3.48.jar common.jar

#echo copy all files to dependency folder
::

    find /home/toolguy/code-coverage/WEB_R010/tsw/tools/system -name *.jar -type f | grep "target/[a-z0-9.\-]\+.jar$" | grep -v sources | xargs -I file cp file  /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/j2ee-app/target/dependency
    find /home/toolguy/code-coverage/WEB_R010/tsw/tools/system -name *.war -type f | grep "target/[a-z0-9.\-]\+.war$" | grep -v sources | xargs -I file cp file  /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/j2ee-app/target/dependency
    find /home/toolguy/code-coverage/WEB_R010/tsw/tools/system -name *.jar -type f | grep "target/[a-z0-9.\-]\+.jar$" | grep -v sources | xargs -I file cp file  /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/j2ee-app/target/j2ee-app-1.3.48/lib/
    find /home/toolguy/code-coverage/WEB_R010/tsw/tools/system -name *.war -type f | grep "target/[a-z0-9.\-]\+.war$" | grep -v sources | xargs -I file cp file  /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/j2ee-app/target/j2ee-app-1.3.48/lib/

Instrument the ear file(not working)
------------------------------------
::

    cd /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/j2ee-app/

    mvn -P instrument package -Dmaven.test.skip=true

    mkdir -p '/tmp/jcc/instrumented/'
    cp /home/toolguy/code-coverage/WEB_R010/tsw/tools/system/j2ee-app/target/j2ee-app-1.3.48.ear /tmp/jcc/instrumented/j2ee-app-1.3.48.ear


