import os
import time
import pytest

#Important clarification , all of the fixtures works in this way, the commands before the yield, are executed pre-test/session, 
#and the commands before, are executed after the test/session finish


#This is a "tearup/down" for the session, that means, the setupPythonServer function is just invoked once 
@pytest.fixture(scope="session", autouse=True)
def setupPythonServer():
    start_pythonServer()
    yield
    kill_pythonServer()



#This is executed between the tests
@pytest.yield_fixture(autouse=True)
def run_around_test():
    os.system("mv workflows/WebFetcher/UserAgentTests/archive/urls.txt workflows/WebFetcher/UserAgentTests/src/")
    yield
    clean_pythonServerLog()


#We are starting the workflow with a Specified user agent with Windows  ChromeV40  on the properties file and checking if it matchs
def start_workflowWinChrome40UserAgent():
    os.system("/opt/sftools/bin/StartWorkflow.sh workflows/WebFetcher/UserAgentTests/webFetcherUserAgentTestWindowsChrome40.properties")
    uaLine =  get_userAgent()
    return uaLine.find("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36")

#We are starting the workflow with the Default Properties file(no user agent on it) and checking if it match with the default user Agent
def start_workflowDefaultUserAgent():
    os.system("/opt/sftools/bin/StartWorkflow.sh workflows/WebFetcher/UserAgentTests/webFetcherUserAgentTestDefaultUserAgent.properties")
    uaLine =  get_userAgent()
    return uaLine.find("Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko")

#We are starting the workflow with a Specified user agent with Linux  ChromeV24  on the properties file and checking if it matchs
def start_workflowLinuxChrome24UserAgent():
    os.system("/opt/sftools/bin/StartWorkflow.sh workflows/WebFetcher/UserAgentTests/webFetcherUserAgentTestLinuxChrome24.properties")
    uaLine =  get_userAgent()
    return uaLine.find("Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17")

def start_workflowCacheOff():
    os.system("/opt/sftools/bin/StartWorkflow.sh workflows/WebFetcher/UserAgentTests/webFetcherWorkerUserAgentTestDefaultUserAgentCachingOff.properties")
    result = isCachingEnabled()
    return result

def isCachingEnabled():
    log = get_log_file_contents()
    if 'Cache-Control: no-cache' in log:
        return 0
    return 1

def get_log_file_contents():
    data = ''
    with open('workflows/WebFetcher/UserAgentTests/outputWebServer.log', 'r') as myfile:
        data=myfile.read().replace('\n', '')
    return data

def start_pythonServer():
    os.system("python server.py &> workflows/WebFetcher/UserAgentTests/outputWebServer.log & ")

def clean_pythonServerLog():
    os.system("cat /dev/null > workflows/WebFetcher/UserAgentTests/outputWebServer.log")

def kill_pythonServer():
    os.system("ps axf | grep server.py | grep -v grep | awk '{print \"kill -9 \" $1}' | sh")


def get_userAgent():
    f = open("workflows/WebFetcher/UserAgentTests/outputWebServer.log", "r")
    userAgentLine = f.readline()
    
    f.close()
    print("UserAgentLine=", userAgentLine)
    return userAgentLine

@pytest.mark.order1
def test_WinChrome40UserAgent():
    resultFind = start_workflowWinChrome40UserAgent()

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

