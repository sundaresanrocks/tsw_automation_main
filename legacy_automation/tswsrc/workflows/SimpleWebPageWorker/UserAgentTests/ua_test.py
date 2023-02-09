import os
import time
import pytest

#Important clarification , all of the fixtures works in this way, the commands before the yield, are executed pre-test/session,
#and the commands before, are executed after the test/session finish


#This is a "tearup/down" for the session, that means, the setupPytohnServer function is just invoked once
@pytest.fixture(scope="session", autouse=True)
def setupPythonServer():
    start_pythonServer()
    yield
    kill_pythonServer()



#This is executed between the tests
@pytest.yield_fixture(autouse=True)
def run_around_test():
    os.system("mv workflows/SimpleWebPageWorker/UserAgentTests/archive/urls.txt workflows/SimpleWebPageWorker/UserAgentTests/src/")
    yield
    clean_pythonServerLog()

#We are starting the workflow with the Default Properties file(no user agent on it) and checking if it match with the default user Agent
def start_workflowDefaultUserAgent():
    os.system("/opt/sftools/bin/StartWorkflow.sh workflows/SimpleWebPageWorker/UserAgentTests/SimpleWebPageWorkerUserAgentTestDefaultUserAgent.properties")
    uaLine =  get_userAgent()
    return uaLine.find("User-Agent: Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko")

#We are starting the workflow with a Specified user agent with Windows NT ChromeV40  on the properties file and checking if it matchs
def start_workflowChrome40UserAgent():
   # os.system("/opt/sftools/bin/StartWorkflow.sh SimpleWebPageWorkerUserAgentTestChrome40.properties")
    os.system("/opt/sftools/bin/StartWorkflow.sh workflows/SimpleWebPageWorker/UserAgentTests/SimpleWebPageWorkerUserAgentTestChrome40.properties")
    uaLine =  get_userAgent()
    return uaLine.find("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36")

#We are starting the workflow with a Specified user agent with Linux  ChromeV24  on the properties file and checking if it matchs
def start_workflowLinuxChrome24UserAgent():
    os.system("/opt/sftools/bin/StartWorkflow.sh workflows/SimpleWebPageWorker/UserAgentTests/SimpleWebPageWorkerUserAgentTestLinuxChrome24.properties")
    uaLine =  get_userAgent()
    return uaLine.find("Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17")



def start_workflowCacheOff():
    os.system("/opt/sftools/bin/StartWorkflow.sh workflows/SimpleWebPageWorker/UserAgentTests/SimpleWebPageWorkerUserAgentTestDefaultUserAgentCachingOff.properties")
    result = isCachingEnabled()
    return result

def start_workflowCacheOn():
    os.system("/opt/sftools/bin/StartWorkflow.sh workflows/SimpleWebPageWorker/UserAgentTests/SimpleWebPageWorkerUserAgentTestDefaultUserAgentCachingOn.properties")
    result = isCachingEnabled()
    return result

def isCachingEnabled():
   if 'Cache-Control: no-cache' in open('workflows/SimpleWebPageWorker/UserAgentTests/outputWebServer.log').read():
      return 0
   return 1


def start_pythonServer():
    os.system("python server.py &> workflows/SimpleWebPageWorker/UserAgentTests/outputWebServer.log & ")

def clean_pythonServerLog():
    os.system("cat /dev/null > workflows/SimpleWebPageWorker/UserAgentTests/outputWebServer.log")

def kill_pythonServer():
    os.system("ps axf | grep server.py | grep -v grep | awk '{print \"kill -9 \" $1}' | sh")


def get_userAgent():
    f = open("workflows/SimpleWebPageWorker/UserAgentTests/outputWebServer.log", "r")
    userAgentLine = f.readline()
    print(userAgentLine)

    f.close()
    return userAgentLine

@pytest.mark.order1
def test_Chrome40UserAgent():
    resultFind = start_workflowChrome40UserAgent()

    assert -1 != resultFind

@pytest.mark.order2
def test_RunningDefaultUserAgent():
    resultFind = start_workflowDefaultUserAgent()

    assert -1 != resultFind

@pytest.mark.order3
def test_LinuxChrome24UserAgent():
    resultFind = start_workflowLinuxChrome24UserAgent()

    assert -1 != resultFind

@pytest.mark.order4
def test_CacheOff():
    resultFind = start_workflowCacheOff()

    assert 0 == resultFind

@pytest.mark.order5
def test_CacheOn():
    resultFind = start_workflowCacheOn()

    assert 1 == resultFind


