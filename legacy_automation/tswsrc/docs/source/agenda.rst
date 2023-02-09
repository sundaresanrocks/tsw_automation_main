Agenda 
======

Framework takes care of
- Reports
- Logging
- Creating sandbox folder structure


Directory Structure
common - old functions that will be converted into new format
docs - complete documentation 
framework - all framework related code will be placed here
 - config
libts - all modules relating to ts only
libx - all generic modules

project - directory in tsa
--(preifx)config.py
--libraries = specific to project
--tc - test cases
--scripts - adhoc scripts for a project

Configuration variables
  --- framwork level - mostly fixed, need not modify
  --- environment(system specific) - framework/config
  --- project level - project specific


SandboxedTest Super Class must take care of
- cleaning direcotry/ setup common for test suite/project
- copying generic files back to sandbox after test execution

Test case must take care of 
- logging with proper levels
- Execution
- raising exceptions
- copyinig files to sandbox




Write testcases
--- What needs to be done?

How to handle exceptions
 --- In libraries
 --- In tests
How are exceptions defined

How to run tests
- difference between modules and packages
- run from a file

Shell executor

Docstrings