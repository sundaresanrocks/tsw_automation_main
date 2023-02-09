#!/bin/bash

FactGenPid=$(jps -m | grep 'FactGenerator' |grep -v grep | awk '{print $1}')
WebFetcherPid=$(jps -m | grep 'Webfetcher' |grep -v grep | awk '{print $1}')
WebFetcherWorker=$(jps -m | grep 'WebFetcherWorker' |grep -v grep | awk '{print $1}')
Consumer=$(jps -m | grep 'Consumer' |grep -v grep | awk '{print $1}')
SimpleWebPageWorker=$(jps -m | grep 'SimpleWebPageWorker' |grep -v grep | awk '{print $1}')
RuleDirectiveProcessor=$(jps -m | grep 'RuleDirectiveProcessor' |grep -v grep | awk '{print $1}')

if [ -z $WebFetcherWorker ]
 then
   echo ""
else
    echo "Killing the workflow WebFetcherWorker"
   `kill -9 $WebFetcherWorker`
fi



if [ -z $RuleDirectiveProcessor ]
 then
   echo ""
else
    echo "Killing the workflow RuleDirectiveProcessor"
   `kill -9 $RuleDirectiveProcessor`
fi


if [ -z $SimpleWebPageWorker ]
 then
   echo ""
else
    echo "Killing the workflow SimpleWebPageWorker"
   `kill -9 $SimpleWebPageWorker`
fi


if [ -z $Consumer ]
 then
   echo ""
else
    echo "Killing the workflow consumer"
   `kill -9 $Consumer`
fi


if [ -z $FactGenPid ]
then
   echo ""
else
    echo "Killing workflow factgenerator"
   `kill -9 $FactGenPid`
fi

if [ -z $WebFetcherPid ]
then
   echo ""
else
    echo "Killing workflow webfetcher"
   `kill -9 $WebFetcherPid`
fi


