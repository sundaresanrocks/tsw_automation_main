import os
import time
import pytest
import subprocess
import logging
import json
import re


logging.basicConfig(level=logging.DEBUG)

WF_SCRIPT = "/opt/sftools/bin/StartWorkflow.sh"
WF_PROP_DIR = ""
AutomationLog = ""



def run_workflow(prop_dir, prop_file, AutomationLog):

   AutomationLog.debug('STARTING WORKFLOW')
   current_milli_time = lambda: int(round(time.time() * 1000))

   proc = subprocess.Popen([WF_SCRIPT, os.path.join(prop_dir, prop_file)], stdout=subprocess.PIPE)
   output = ""
   while True:
    outputLine = proc.stdout.readline()
    if outputLine != '':
     #we are skipping log4j lines as we want to keep everything in json format (we should use the json format as we discussed)
     if not outputLine.startswith('log4j'):
      outputLine = re.sub(r'\[(.*?)\]', '' , outputLine)
      output = output + outputLine 
    else:
     break
   with open("WorkflowTestOutput" + str(current_milli_time()) , "w") as text_file:
    text_file.write(output)
   
   AutomationLog.debug('WORKFLOW FINISHED')
   #before return everything as a JSON object we need to finish the JsonOutputConsumer
   
   #output = json.load(output)
   return output

#This is a "tearup/down" for the session, that means, the setupPytohnServer function is just invoked once
@pytest.fixture(scope="session", autouse=True)
def setupPythonServer():
    start_pythonServer()
    yield
    kill_pythonServer()



#This is executed between the tests
@pytest.yield_fixture(autouse=True)
def run_around_test():
    os.system("mv archive/urls.txt src/")
    os.system("mv error/urls.txt src/")
    os.system("mv working/urls.txt src/")

    yield
    clean_pythonServerLog()


def start_pythonServer():
    os.system("python server.py &> outputWebServer.log & ")

def clean_pythonServerLog():
    os.system("cat /dev/null > outputWebServer.log")

def kill_pythonServer():
    os.system("ps axf | grep server.py | grep -v grep | awk '{print \"kill -9 \" $1}' | sh")


def get_userAgent():
    f = open("outputWebServer.log", "r")
    userAgentLine = f.readline()
    print(userAgentLine)

    f.close()
    return userAgentLine

@pytest.mark.order1
def test_Chrome40UserAgent():
    #To pass this test, we have to have the SimpleWebPageWorkerUserAgentTestChrome40.properties ,and the user agent setted up to Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36
    #Test Example using the new startWorkflow
    AutomationLog = logging.getLogger('test_Chrome40UserAgent')

    workflowLog = run_workflow(WF_PROP_DIR, "SimpleWebPageWorkerUserAgentTestChrome40.properties", AutomationLog)
    uaLine =  get_userAgent()
    match = uaLine.find("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36")
    AutomationLog.debug('POSITION OF THE MATCH is ' + str(match))
#Match it will be different than one if the User agent matches with the user agent of the property file, also, we are verifying than the workflow log was generated
    if match != -1 and len(workflowLog) != 0:
       sucess = True
    else:
       sucess = False

    assert sucess
