# coding=utf-8
"""
======================================
 Regex security workflow worker test cases
======================================
"""


__author__ = 'nikitha'


import unittest
import runtime
from conf.files import PROP
from runtime import data_path
from conf.properties import set_prop_application
from conf.properties import prop_regex_security_workflow
from urldb.workflow_lib import Workflow
from conf.files import DIR
import logging
from path import Path

LOCAL_AGENT_PROP_FILE = Path('agent.properties')

APPLICATION_PROPERTY=PROP.application
WORKFLOW_PROPERTY = PROP.regex_security_workflow
DEFAULT_SRCFILE_DEST = DIR.provider_sourceDir
DEFAULT_WORKFILE_DEST = DIR.provider_workingDir
DEFAULT_ARCFILE_DEST = DIR.provider_archiveDir


class TestRegexSecurityWorkflowMechRun1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Runs regex security workflow once for a group of testcases
        """
        ap_obj=set_prop_application()
        prop_regex_security_workflow()
        regex_file_path= data_path.joinpath('urldb/regex_security_workflow/regexes.txt')
        ap_obj['cloudPatterns.inputFile']=regex_file_path
        ap_obj.write_to_file(APPLICATION_PROPERTY)

        if not DEFAULT_SRCFILE_DEST.exists():
               DEFAULT_SRCFILE_DEST.makedirs()

        if not DEFAULT_WORKFILE_DEST.exists():
               DEFAULT_WORKFILE_DEST.makedirs()
        if not DEFAULT_ARCFILE_DEST.exists():
               DEFAULT_ARCFILE_DEST.makedirs()

    def stage_input_files_to_srcdirectory(self,filename):
        """
        move input file to source directory
        """
        input_file= data_path.joinpath('urldb/regex_security_workflow/input.txt')
        target_file = DEFAULT_SRCFILE_DEST.joinpath(filename)
        input_file.copyfile(target_file, follow_symlinks=False)

    def write_url_inputfile(self,url):
        """
        writes url to input file
        """
        input_file_path= data_path.joinpath('urldb/regex_security_workflow/input.txt')
        open(input_file_path,mode='w').write(url)
        self.stage_input_files_to_srcdirectory('input.txt')

    def check_string_stdout(self,string,output):
        """
        checks the string in shell output
        :param string:
        :param output:
        :return:
        """
        if string in output:
            return True
        else:
            return False


    def setUp(self):
        super(TestRegexSecurityWorkflowMechRun1, self).setUp()
        self.workflow_cobj = Workflow()


    def test_url_with_querystring(self):
        """
        tests whether url's with query string are generating appropriate facts
        """

        workflow_obj = Workflow()
        self.write_url_inputfile('http://www.abctentjs.com/abc?a=1')
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        logging.info(stdo)
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, cloudPatternRegexList=(?i).*tentjs.*, url=http://www.abctentjs.com/abc?a=1, cloudPatternRegexMatch=true'
        assert self.check_string_stdout(expected_string,stdo)==True

    def test_url_with_uppercase(self):
        """
        tests whether uppercase url's are generating appropriate facts
        """

        workflow_obj = Workflow()
        self.write_url_inputfile('HTTP://HELLOJS-PAGENATIONS.COM')
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        logging.info(stdo)
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, cloudPatternRegexList=(?i).*js(\.|\/|\?|=|-|_)pagenations.*, url=HTTP://HELLOJS-PAGENATIONS.COM, cloudPatternRegexMatch=true'
        assert self.check_string_stdout(expected_string,stdo)==True

    def test_single_url_multiple_regexpattern(self):
        """
        tests whether single url matches more than one regex pattern
        """

        workflow_obj = Workflow()
        self.write_url_inputfile('https://msn.com/nph-proxy.pl123/p.bin')
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        logging.info(stdo)
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, cloudPatternRegexList=(?i).*/p\.bin$.*|(?i).*/nph-proxy\.pl.*, url=https://msn.com/nph-proxy.pl123/p.bin, cloudPatternRegexMatch=true'
        assert self.check_string_stdout(expected_string,stdo)==True

    def test_single_url_single_regexpattern(self):
        """
        tests whether an url matches only one regex pattern
        """

        workflow_obj = Workflow()
        self.write_url_inputfile('www.rest/o.bin')
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        logging.info(stdo)
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, cloudPatternRegexList=(?i).*/o\.bin$.*, url=www.rest/o.bin, cloudPatternRegexMatch=true'
        assert self.check_string_stdout(expected_string,stdo)==True

    def test_url_not_matching_regexpattern(self):
        """
        tests whether an url does not match any regex pattern
        """

        workflow_obj = Workflow()
        self.write_url_inputfile('www.querystring123.com/path?htm=129')
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        logging.info(stdo)
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, url=www.querystring123.com/path?htm=129, cloudPatternRegexMatch=false'
        assert self.check_string_stdout(expected_string,stdo)==True

    def test_multiple_url_same_regexpattern(self):
        """
        tests whether same regex pattern matches multiple urls
        """

        workflow_obj = Workflow()
        input_file_path= data_path.joinpath('urldb/regex_security_workflow/input.txt')
        file=open(input_file_path,mode='w')
        file.write('www.gmail.com/tor/server/123.exe\n')
        file.write('https://msn.com/tor/server')
        file.close()
        self.stage_input_files_to_srcdirectory('input.txt')

        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, cloudPatternRegexList=(?i).*/tor/server.*, url=www.gmail.com/tor/server/123.exe, cloudPatternRegexMatch=true'
        assert self.check_string_stdout(expected_string,stdo)==True
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, cloudPatternRegexList=(?i).*/tor/server.*, url=https://msn.com/tor/server, cloudPatternRegexMatch=true'
        assert self.check_string_stdout(expected_string,stdo)== True
        word='cloudPatternRegexList=(?i).*/tor/server.*'
        string_count=stdo.count(word)
        assert string_count==4

    def test_empty_infile(self):
        """
        tests when input file is empty facts are not generated
        """

        workflow_obj = Workflow()
        self.write_url_inputfile('')
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success'
        assert self.check_string_stdout(expected_string,stdo)== False

    def test_url_port(self):
        """
        tests whether url's with port number are generating appropriate facts
        """

        workflow_obj = Workflow()
        self.write_url_inputfile('www.googlecom:80/site/.*/files')
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        logging.info(stdo)
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, cloudPatternRegexList=(?i).*:80.*, url=www.googlecom:80/site/.*/files, cloudPatternRegexMatch=true'
        assert self.check_string_stdout(expected_string,stdo)== True

    def test_url_string_end(self):
        """
        tests whether url's will match end of the string $ regex and generating appropriate facts
        """

        workflow_obj = Workflow()
        self.write_url_inputfile('www.gmail.com/e.bin')
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        logging.info(stdo)
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, cloudPatternRegexList=(?i).*/e\.bin$.*, url=www.gmail.com/e.bin, cloudPatternRegexMatch=true'
        assert self.check_string_stdout(expected_string,stdo)== True

    def test_same_pattern_twice_url(self):
        """
        tests whether cloudPatternRegexList will contain the pattern only once irrepective of number of occurance of the same pattern in an URL
        """

        workflow_obj = Workflow()
        self.write_url_inputfile('http://testmail.com/tentjs/tentjs?key=test')
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, cloudPatternRegexList=(?i).*tentjs.*, url=http://testmail.com/tentjs/tentjs?key=test, cloudPatternRegexMatch=true'
        assert self.check_string_stdout(expected_string,stdo)== True
        #pattern_count=stdo.count('(?i).*tentjs.*')
        pattern_count=stdo.count('(?i).*tentjs.*')
        assert pattern_count == 2

    def test_url_with_protocol(self):
        """
        tests whether url's with protocol are generating appropriate facts
        """

        workflow_obj = Workflow()
        self.write_url_inputfile('https://outlook.co/lbr.bin')
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        logging.info(stdo)
        out_file_path=runtime.data_path+'/urldb/regex_security_workflow/out.txt'
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, cloudPatternRegexList=(?i).*/lbr\.bin$.*, url=https://outlook.co/lbr.bin, cloudPatternRegexMatch=true'
        assert self.check_string_stdout(expected_string,stdo)== True

    def test_url_without_protocol(self):
        """
        tests whether url's without protocol are generating appropriate facts
        """

        workflow_obj = Workflow()
        self.write_url_inputfile('www.gmail.com/tentjs.exe')
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        logging.info(stdo)
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, cloudPatternRegexList=(?i).*tentjs.*, url=www.gmail.com/tentjs.exe, cloudPatternRegexMatch=true'
        assert self.check_string_stdout(expected_string,stdo)== True

    def test_url_with_ip(self):
        """
        tests whether url's with ip address are generating appropriate facts
        """

        workflow_obj = Workflow()
        self.write_url_inputfile('http://12.43.76.123/tor/status.com?html')
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        logging.info(stdo)
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, cloudPatternRegexList=(?i).*/tor/status.*, url=http://12.43.76.123/tor/status.com?html, cloudPatternRegexMatch=true'
        assert self.check_string_stdout(expected_string,stdo)== True


class TestRegexSecurityWorkflowMechRun2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Runs regex security workflow once for a group of testcases
        """
        ap_obj=set_prop_application()
        regex_file_path= data_path.joinpath('urldb/regex_security_workflow/regexes1.txt')
        ap_obj['cloudPatterns.inputFile']=regex_file_path
        ap_obj.write_to_file(APPLICATION_PROPERTY)

    def setUp(self):
        super(TestRegexSecurityWorkflowMechRun2, self).setUp()
        self.workflow_cobj = Workflow()

    def test_same_pattern_multiple_times_regexesfile(self):
        """
        tests when same regex pattern is available multiple times  in regex file
        """

        workflow_obj = Workflow()
        testrun_obj=TestRegexSecurityWorkflowMechRun1()
        testrun_obj.write_url_inputfile('www.rest/o.bin')
        regex_file_path= data_path.joinpath('urldb/regex_security_workflow/regexes1.txt')
        file=open(regex_file_path,mode='w')
        file.write('(?i).*/o\.bin$.*\n')
        file.write('(?i).*/o\.bin$.*')
        file.close()
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, cloudPatternRegexList=(?i).*/o\.bin$.*|(?i).*/o\.bin$.*, url=www.rest/o.bin, cloudPatternRegexMatch=true'
        assert testrun_obj.check_string_stdout(expected_string,stdo)== True

class TestRegexSecurityWorkflowMechRun3(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Runs regex security workflow once for a group of testcases
        """
        ap_obj=set_prop_application()
        regex_file_path= data_path.joinpath('urldb/regex_security_workflow/regexes1.txt')
        ap_obj['cloudPatterns.inputFile']=regex_file_path
        ap_obj.write_to_file(APPLICATION_PROPERTY)


    def setUp(self):
        super(TestRegexSecurityWorkflowMechRun3, self).setUp()
        self.workflow_cobj = Workflow()

    def test_empty_regexesfile(self):
        """
        tests when regex file is empty the fact generated where in cloudPatternRegexMatch is false
        """

        workflow_obj = Workflow()
        testrun_obj=TestRegexSecurityWorkflowMechRun1()
        testrun_obj.write_url_inputfile('www.rest/o.bin')
        empty_regex_file_path= data_path.joinpath('urldb/regex_security_workflow/regexes1.txt')
        ap_obj=set_prop_application()
        #regex_file_path= data_path.joinpath('urldb/regex_security_workflow/regexes1.txt')
        ap_obj['cloudPatterns.inputFile']=empty_regex_file_path
        fp = open(empty_regex_file_path,'w')
        fp.write('')
        fp.close()
        ap_obj.write_to_file(APPLICATION_PROPERTY)
        stdo,stde=workflow_obj.run_security_workflow(workflow_property=runtime.PROP.regex_security_workflow)
        expected_string = 'factGeneratorExitStatus=Success, cloudPatternVerboseMessage=N/A, cloudPatternExitStatus=success, url=www.rest/o.bin, cloudPatternRegexMatch=false'
        assert testrun_obj.check_string_stdout(expected_string,stdo)== True
