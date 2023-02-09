import os
import time
import pytest
import subprocess
from subprocess import call
import logging
import json
import re
import os

class workflowAPI():


 logging.basicConfig(level=logging.DEBUG)

 WF_SCRIPT = "/opt/sftools/bin/StartWorkflow.sh"
 SFIMPORT_SCRIPT = "/usr2/smartfilter/import/sfimport"
 WF_PROP_DIR = ""
 AutomationLog = ""
 configMap = {}

 def __init__(self):
  print(" Welcome to the Testing World ") 


#This method start a workflow and save the log in the object.log variable, this run_workflow WAIT for the workflow to finish
 def run_workflow(self, prop_dir, prop_file, AutomationLog):

   AutomationLog.debug('STARTING WORKFLOW')
   current_milli_time = lambda: int(round(time.time() * 1000))

   proc = subprocess.Popen([self.WF_SCRIPT, os.path.join(prop_dir, prop_file)], stdout=subprocess.PIPE)

   AutomationLog.debug('WORKFLOW FINISHED')
   
   self.workflowProcess = proc
   self.log = proc.stdout.read()

   with open("WorkflowTestOutput" + str(current_milli_time()) , "w") as text_file:
     text_file.write(self.log)
   
 def kill_workflow(self):
   self.workflowProcess.kill()

 def run_workflowUnstoppable(self, prop_dir, prop_file, AutomationLog):
   AutomationLog.debug('STARTING WORKFLOW')
   FNULL = open(os.devnull, 'w')
   proc = subprocess.Popen([self.WF_SCRIPT, os.path.join(prop_dir, prop_file)], stdout=FNULL, stderr=FNULL)

   AutomationLog.debug('WORKFLOW FINISHED')

   self.workflowProcess = proc



 def loadApplicationProperties(self):
   
   with open("/opt/sftools/conf/application.properties") as myfile:
        for line in myfile:
            name, var = line.partition("=")[::2]
            self.configMap[name.strip()] = (var).replace('\r', '').replace('\n', '')



