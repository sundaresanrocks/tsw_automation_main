#!/usr/bin/env python
import sys
from subprocess import call, TimeoutExpired, check_output
import time
import os
import shutil
import re
import socket

successful_execution = 0
automation_dir = "/opt/wsr-qa-automation/nas_workflow_automation/tsw-test-automation/workflow_automation/"
workflow_name = None


def invoke_property_files(arg):
    read_property_files = os.path.join(automation_dir, arg, "execution.txt")
    list_of_workflow_to_run = [
        line.rstrip('\n') for line in open(read_property_files)]
    if len(list_of_workflow_to_run) == 0:
        raise ValueError("CONFIG ERROR: No workflow properties are configured in the file")
    else:
        return list_of_workflow_to_run


# This method will execute the workflow and write logs to the given path
def call_workflow(wf, logs_path):
    time_out = 300
    if "provider" in wf.lower():
        time_out = 60
    if "webfetcher" in wf.lower():
        time_out = 100
    if "factgenerator" in wf.lower():
        time_out = 300
    if "consumer" in wf.lower():
        time_out = 500
    if "simplewebpage" in wf.lower():
        time_out = 300
    if "ruledirectiveprocessor" in wf.lower():
        time_out = 500

    print("##__Executing__" + wf + " timeout=" + str(time_out))
    val = True
    try:
        process = call(["/opt/sftools/bin/StartManagedWorkflow.sh " +  wf + " >> " + logs_path + " 2>&1" ], timeout=time_out, shell=True)
        return val
    except TimeoutExpired:
        print("Killing long running process and moving to the next worker")
        val = False
    return val


# Clean up the directories
def delete_contents(folder):
    if os.path.isdir(folder) == False:
        raise Exception("ERROR: Given directory= " + folder + " do not exist")
    else:
        for file_path in os.listdir(folder):
            file_path = os.path.join(folder, file_path)
            print("\n")
            try:
                if os.path.isfile(file_path):
                    print("##_____REMOVING file_____" + file_path)
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    print("##_____REMOVING directory_____" + file_path)
                    shutil.rmtree(file_path)
            except Exception:
                print("ERROR: Failed to delete files/directories")


def kill_processes():
    pattern = re.compile
    killed_processes = check_output(
        [os.path.join(automation_dir, "kill_processes.sh")], shell=True)
    print(str(killed_processes))

# Remove files from all directories which were created by the last workflow


def init():
    # print ("###____Cleaning the /data/urldb direcotry_________")
    # delete_contents("/data/urldb")
    print("###____Cleaning /tmp directory_________")
    delete_contents("/tmp")

def display_files(folder, match):
    files = os.listdir(folder)
    for each_file in files:
        _file = str(each_file)
        if re.match(match, _file):
            print(_file)


def check_urldb_files(wf_name):
    print("\n## Showing the URLDB files created by the workflow______")
    print("Workflow name=" + wf_name + " \n")
    display_files("/data/urldb", wf_name)


def check_sfimport_files():
    print("\n## Showing the sfimport files created by the workflow______")
    display_files("/tmp", "sfimport")

def get_workflow_directory(path_name):
    #dir_name = path_name.split("/")[0]
    return automation_dir + path_name


def check_not_found_in_sampledb_files(wf_name):
    print("\n## Showing the Not_found_in_SampleDB files created by the SimpleWebPageWorker______")
    display_files("/data/webcache/notFoundUrlsInSampleDBDest/src", wf_name)


def copy_files(source, destination):
    src_files = os.listdir(source)
    for file_name in src_files:
        full_file_name = os.path.join(source, file_name)
        if (os.path.isfile(full_file_name)):
            print("##___Copying files to src directory___" + full_file_name)
            shutil.copy(full_file_name, destination)


# A thorough cleaning will be done before the workflow starts.
def remove_last_run_data(wf_dir):
    # clean up the archive dir
    delete_contents(os.path.join(wf_dir, "archive"))
    # clean up src dir
    delete_contents(os.path.join(wf_dir + "/src"))
    # clean up working dir
    delete_contents(os.path.join(wf_dir + "/working"))
    # clean up error dir
    delete_contents(os.path.join(wf_dir + "/error"))
    # cleaning the download dir
    delete_contents(os.path.join(wf_dir + "/download"))
    # clean the content of previousfile.txt from the  previousrundata and
    # clean the content of downloadfile from previous downloaded data  before
    # running the workflow
    delete_contents(os.path.join(wf_dir + "/previousrundata"))
    delete_contents(os.path.join(wf_dir + "/previousdownloadeddata"))
    delete_contents(os.path.join(wf_dir + "/providedfile"))


def tear_down(log_file, wf_dir, wf_name):
    remove_last_run_data(wf_dir)
    # Check for the urldb files
    check_urldb_files(wf_name)
    # Check for the sfimport files
    check_sfimport_files()
    # check Not found urls in Sampledb
    check_not_found_in_sampledb_files(wf_name)

    # kill long running processes of the workflow
    kill_processes()

    print("\n##__________CHECK THE PROPERTIES FILE__________## \n")
    print(log_file + "\n\n")
    display_stats(log_file)


# check if the server is up and running
def server_test(host, port):
    args = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
    for family, socktype, proto, canonname, sockaddr in args:
        s = socket.socket(family, socktype, proto)
        try:
            s.connect(sockaddr)
        except socket.error:
            return False
        else:
            s.close()
            return True


# Show the number of errors and warnings
def display_stats(log_file):
    with open(log_file) as f:
        contents = f.read()
        count_error = contents.count("ERROR")  # look at smaller case
        count_error = count_error + contents.count("error")
        count_error = count_error + contents.count("Error")
        print("NUMBER OF ERRORS FOUND: " + str(count_error) + " \n")

        count_exceptions = contents.count("EXCEPTION")
        count_exceptions = count_exceptions + contents.count("Exception")
        count_exceptions = count_exceptions + contents.count("exception")
        print("NUMBER OF EXCEPTIONS FOUND: " + str(count_exceptions) + " \n")

        count_warning = contents.count("WARNING")
        count_warning = count_warning + contents.count("Warning")
        count_warning = count_warning + contents.count("warning")
        print("NUMBER OF WARNINGS FOUND: " + str(count_warning) + " \n")

        count_fatal = contents.count("FATAL")
        count_fatal = count_fatal + contents.count("fatal")
        count_fatal = count_fatal + contents.count("Fatal")
        print("NUMBER OF FATAL-WORD FOUND:" + str(count_fatal) + " \n")


# Main method
def main():
    log_file = None
    workflow_dir = None
    source_type = None
    workflow_name = None
    name = str(sys.argv[1])
    #name = None
    workflow_dir = automation_dir + name
    try:
        if len(sys.argv) != 2:
            raise Exception(
                "ERROR: Invalid arguments were given, aborting automation")
        else:
            props = invoke_property_files(str(name))
            print("Value for props " + str(props))
            source_type = invoke_property_files(str(name))
            print("Value for source_type " + str(source_type))
            
            if server_test("localhost", 8161):
                print(
                    "\n.......ActiveMQ server localhost:8161 is up and running...........")
            else:
                raise Exception(
                    "\n ERROR:__________ActiveMQ server localhost:8161 is not running_______CHECK NOW_______")

            # Cleaning process before workflow starts
            remove_last_run_data(workflow_dir)
            
            

            if source_type[0] == "http":
                print ("...Checking if the LOCALHOST:8000 is up and running....\n")
                if server_test("localhost", 8000):
                    print (".......cleaning the previousFiles.txt.......\n")
                    open(workflow_dir +"/previousrundata/previousfile.txt", 'w').close()

                else:
                    raise Exception("ERROR: _____LOCALHOST:8000 IS NOT RUNNING_____CHECK NOW____")

            elif source_type[0] == "ftp":
                # clean previousFiles and downloadedFiles
                print  (".......Cleaning the downloadedFiles.txt.....\n")
                open("/data/webcache/workflows/harvesters/" + name + "/downloadedfiles.txt", 'w').close()
                print  (".......Cleaning the previousFiles.txt.....")
                open(workflow_dir + "/previousrundata/previousfile.txt", 'w').close()
                print ("\n__DO YOU NEED UPDATE YOUR FTP_SERVER FOR NEW FILES__IF YES, CANCEL THE PROCESS NOW!!\n")
                time.sleep(5)

            elif source_type[0] == "rsync":
                
                print("......cleaning the previousFiles.txt....\n")
                open(workflow_dir +"/previousrundata/previousfile.txt", 'w').close()

            elif source_type[0] == "files":
                # Copy files from /source_unchanged to /src directory before executing the workflow
                copy_files(workflow_dir + "/source_unchanged", workflow_dir + "/src")
                print (".......cleaning the providedFiles.txt.....\n")
                open("/data/webcache/workflows/harvesters/" + name + "/providedFiles.txt", 'w').close()


            elif source_type[0] == "provider_no_change":
                print ("\n___DO YOU NEED TO UPDATE THE TIMESTAMP FILE__If YES, Cancel the process NOW!!")
                print ("<<<<<<If require update the timestamp or ____COPY from Production_____ to minimize input>>>>>>")
                time.sleep(5)


        print("##__________ Workflow_____ " + name + "___________##\n\n")
        workflow_name = name + str(time.time())
        log_file = workflow_dir + "/logs/" + workflow_name + ".log"

        # execute each workflow properties file in the order it was given
        for wf in range(1, len(props)):
            result = call_workflow(props[wf], log_file)
            #if not result:
            if result == False:
                continue
    finally:
        if log_file is None:
            print("############################################")
            print(
                "_____Automation did not start with expected parameters_____ABORTING__\n")
            print("#USAGE: python start_automation.py <WorkflowName>\n")
        else:
            tear_down(log_file, workflow_dir, name)


# Main
if __name__ == '__main__':
    init()
    main()
