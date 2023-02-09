export R_HOME=/usr/lib64/R
export LIBRARY_PATH=/usr/lib64/R/lib
export SFDBSERVERD2=TSWDB_QA_D2
export SFDBSERVERR2=TSWDB_QA_R2
export SFDBSERVERU2=TSWDB_QA_U2
cd /var/lib/jenkins/workspace/tsw-test-automation/workflow_automation/
/opt/rh/rh-python36/root/usr/bin/python start_automation.py GithubCommitsHarvestWorkflow/execution.txt GithubCommitsHarvestWorkflow files
#/opt/rh/rh-python36/root/usr/bin/python start_automation.py MrgEffitasHarvestWorkflow/execution.txt MrgEffitasHarvestWorkflow ftp
/opt/rh/rh-python36/root/usr/bin/python start_automation.py DRSprescanHarvestWorkflow/execution.txt DRSprescanHarvestWorkflow http
/opt/rh/rh-python36/root/usr/bin/python start_automation.py DRSblackHarvestWorkflow/execution.txt DRSblackHarvestWorkflow http
/opt/rh/rh-python36/root/usr/bin/python start_automation.py MUTEHarvestWorkflow/execution.txt MUTEHarvestWorkflow http
/opt/rh/rh-python36/root/usr/bin/python start_automation.py SURBLHarvestWorkflow/execution.txt SURBLHarvestWorkflow rsync
#/opt/rh/rh-python36/root/usr/bin/python start_automation.py ReseachTelemetryProcessorWorkflow/execution.txt ReseachTelemetryProcessorWorkflow files
