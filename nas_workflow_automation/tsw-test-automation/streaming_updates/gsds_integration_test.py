import httplib
import sys
import os
import json
import collections
import os
import subprocess
import shlex
import time
import zipfile
import ast
import pytest
import hashlib

__server__ = "http://ldvrdbsrst0001.corpzone.internalzone.com/reputation/url/v1.0"
__inputFile__ = "streaming_updates/testUrls.txt"
__restClientPath__ = "streaming_updates/rest_reference_client.py"
__restClientConfig__ = "streaming_updates/configuration.cfg"


def generateGSDSQueries(urlList):
    queries = ''
    fileCounter = 0
    fileQuery = open("query" + str(fileCounter) + ".txt", "w+")
    queryCounter = 0
    fileQuery.write('{"q": [\n')

    for key, value in urlList.iteritems():
        queries += '{"val": "' + key + '" },\n'
        queryCounter += 1
        if queryCounter == 5 and urlList.keys()[-1] != key:
            queries = queries[:-2]
            fileQuery.write(queries)
            fileQuery.write('\n]}')
            fileQuery.close()
            fileCounter += 1
            fileQuery = open("query" + str(fileCounter) + ".txt", "w+")
            queryCounter = 0
            fileQuery.write('{"q": [')
            queries = ''
    queries = queries[:-2]
    fileQuery.write(queries)
    fileQuery.write('\n]}')
    fileQuery.close()
    return fileCounter


def parsingInputData():
    urlList = {}
    with open(__inputFile__) as inf:
        line = inf.readline()
        while line:
            lineParsed = line.split(" ")

            # Generate SHA256 of the URL with the prefix
            hash_object = hashlib.sha256("*://" + lineParsed[0])
            hex_dig = hash_object.hexdigest()

            # Load the testCases into the structure
            # lineParsed[0] URL, lineParsed[1][0] Hash, lineParsed[1][1] rep
            # .. [1][2] cat ,[1][3] cache, [1][4] Expected rep, [1][5] expected cat ,
            # [1][6] expected cacheable, [1][7] Insert in GSDS Client (True or False)
            try:
                urlList[lineParsed[0]] = [hex_dig, lineParsed[1], lineParsed[2], lineParsed[3], lineParsed[4],
                                          lineParsed[5], lineParsed[6], lineParsed[7].replace('\n', '')]
            except IndexError:
                print('error processing line ' + str(line))

            line = inf.readline()
    return urlList


def testGSDSClientFromFile():
    totalErrors = 0
    # urlList = {}
    inserts = 0
    urlList = parsingInputData()

    # Generate a file with INSERT Streaming Update events
    ctime = str(int(time.time()))
    ctime = ctime + "-1"
    incrementalRep = 16
    f = open("url-" + ctime + ".txt", "w+")

    # Insert every event from the input to a streaming update output file if the flag is set to True
    for value in urlList.iteritems():
        if value[1][7] == 'True':
            f.write("1 " + value[1][0] + " " + str(value[1][1]) + " " + str(value[1][2]) + " " + value[1][3] + " 0\n")
            inserts += 1
    f.close()
    if inserts > 0:
        z = zipfile.ZipFile("url-" + ctime + ".zip", "w")
        z.write("url-" + ctime + ".txt")
        z.close()

        # Copy the file over
        os.system("scp url-" + ctime + ".zip gsdsuser@10.45.123.29:/home/gsdsuser/Incremental/")

        # Delay to allow GSDS time to process the file
        print("File sent. Waiting...")
        time.sleep(300)

    # Generate queries to the GSDS Client to query every URL
    fileCounter = generateGSDSQueries(urlList)

    # Run the queries
    resList = list()
    for i in range(0, fileCounter + 1):
        asd_local = ("python2.7 " + __restClientPath__ + " -q query" + str(i) + ".txt -c " + __restClientConfig__)
        args = shlex.split(asd_local)
        try:
            resList.append(ast.literal_eval((subprocess.check_output(args))))
        except SyntaxError:
            print("ERROR GETTING RESULT OF query" + str(i) + ".txt")
    iter = 0
    iterFiles = 0
    for value in urlList.iteritems():
        if str(value[1][4]) != str(resList[iterFiles][iter]['rep']):
            print(" ERROR rep for URL " + str(value[0]) + " = " + str(
                resList[iterFiles][iter]['rep']) + " expected " + str(value[1][4]))
            totalErrors += 1

        # Remove '[' and ']' from the cat string
        cat = str(resList[iterFiles][iter]['cat']).replace('[', '').replace(']', '')
        cat = ''.join(cat.split())
        resCat = cat.strip().split(",")
        expectedCat = value[1][5].strip().split(",")
        if not all(elem in resCat for elem in expectedCat):
            # if(value[1][5] != cat):
            print(" ERROR cat for URL " + str(value[0]) + " = " + str(resCat) + " expected " + str(
                expectedCat) + "-- " + str(value[1][5]))
            totalErrors += 1
        iter += 1
        if iter == 5:
            iterFiles += 1
            iter = 0

    # Generate delete events and move them to the GSDS DB
    if inserts > 0:
        ctime = str(int(time.time()))
        ctime = ctime + "-1"
        f = open("url-" + ctime + ".txt", "w+")

        # Write the delete event for the urls that were True
        for value in urlList.iteritems():
            if value[1][7] == 'True':
                f.write("2 " + value[1][0] + "\n")
        f.close()

        z = zipfile.ZipFile("url-" + ctime + ".zip", "w")
        z.write("url-" + ctime + ".txt")
        z.close()

        # Move the events to GSDS
        os.system("scp url-" + ctime + ".zip gsdsuser@10.45.123.29:/home/gsdsuser/Incremental/")

        # Delay to allow the GSDS to process the deletes
        time.sleep(500)

    assert totalErrors == 0
