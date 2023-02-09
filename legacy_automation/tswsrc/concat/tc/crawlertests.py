"""
===================================
Social Media Crawler tests

Dev Contact - Paramasivam, Thamizhannal <Thamizhannal_Paramasivam@McAfee.com>
QA Contact  - Vemuri, Anurag <Anurag_Vemuri@McAfee.com>
===================================
"""

__author__ = 'Anurag'

import datetime
import time
import os
import shutil
import glob

import runtime
from lib.exceptions import FileNotFoundException
from libx.process import ShellExecutor
from concat.tc.crawlerproperties import CrawlerProperties
from lib.exceptions import TestFailure
from framework.test import SandboxedTest
import logging


class CrawlerExecutor(ShellExecutor):
    """
    Builds command for running the Social Media Crawler
    """


    def cmd_builder(self, **kwargs):

        self.config_path=kwargs['config_path']
        self.crawler_path=kwargs['crawler_path']
        system_time= ""
        time_now = datetime.datetime.now()
        system_time= ""+str(time_now.month)+str(time_now.day)+time.strftime("%I",time.localtime())+str(time_now.minute)+str(time_now.second)
        self.cmd.append("%s %s"%(self.crawler_path,self.config_path))


class CrawlerTests(SandboxedTest):
    """
    Social Media Crawler Tests
    """
    results_path = '/home/toolguy/tswaexec/social_media_crawler/results/'
    workingDirectory = '/home/toolguy/tswaexec/social_media_crawler/'
    sourceDir = '/home/toolguy/tswaexec/social_media_crawler/source/'
    archivePath = '/home/toolguy/tswaexec/social_media_crawler/results/'
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    if not os.path.exists(workingDirectory):
        os.makedirs(workingDirectory)
    if not os.path.exists(sourceDir):
        os.makedirs(sourceDir)
    if not os.path.exists(archivePath):
        os.makedirs(archivePath)


    files = [os.path.join(results_path, fname) for fname in os.listdir(results_path)]
    count=len(files)
    starttime=time.time()
    regexout=[]
    regex_mask=[]
    data=runtime.data_path.joinpath('/social_media_crawler_data/')

    def setUp(self):
        """
        Records Start time and sets error and output masks
        """
        SandboxedTest.setUp(self)
        self.starttime=time.time()
        count=len(self.files)
        self.regexout = ['ERROR','Unexpected error']
        self.regex_mask = [False, False]
    def tearDown(self):
        """

        """
        SandboxedTest.tearDown(self)




    def test_01(self):
        """TS-919:Test for starting the crawler
        Expects a NullPointerException
        Raises TestFailure on fail
        """

        obj=CrawlerExecutor()
        if  not os.path.exists(CrawlerProperties.config_path):
            raise FileNotFoundException('Crawler Config File not found')

        if not os.path.exists(CrawlerProperties.crawler_path):
            raise FileNotFoundException('Crawler executable File not found')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate(['NullPointerException'], [True],
                                self.regexout, self.regex_mask
                                )
        file_list=self.results_path+'*.txt'
        r = glob.glob(file_list)
        for i in r:
           os.remove(i)
        logging.debug('Emptied Results')
        file_list='/home/toolguy/tswaexec/social_media_crawler/source/working/'+'*.txt'
        r = glob.glob(file_list)
        for i in r:
           os.remove(i)
        logging.debug('Emptied Working')
        file_list='/home/toolguy/tswaexec/social_media_crawler/source/archive/'+'*.txt'
        r = glob.glob(file_list)
        for i in r:
           os.remove(i)
        logging.debug('Emptied Archives')
        file_list='/home/toolguy/tswaexec/social_media_crawler/source/'+'*.txt'
        r = glob.glob(file_list)
        for i in r:
           os.remove(i)
        logging.debug('Emptied Source')

        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path)]
        print((self.count,' ',len(fileslist)))
        if len(fileslist)==(self.count)+1:
            raise TestFailure('Output file generated even if no input file')
        print('No output file generated')


    def test_02(self):
        """TS-1019:Test for crawling with an invalid seed URL format
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        dest=self.sourceDir+'/one.txt'
        fp=open(dest,'w')
        fp.write('http:/www.anurag.com')
        fp.close()
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        if len(fileslist)==(self.count)+1:
            raise TestFailure('Output file generated for an invalid URL')



    def test_03(self):
        """TS-920:Test the generation of valid output file
        Testing with a dummy URL to crawl
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'dummy.txt'
        dest=self.sourceDir+'/dummy.txt'
        shutil.copy(data, dest)
        logging.debug('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        if len(fileslist)==(self.count)+1:
            raise TestFailure('Output file generated for dummy URL')
        print('No output file generated')


    def test_04(self):
        """TS-912:Test for crawling a dead URL
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'dead.txt'
        dest=self.sourceDir+'/tinyurl.txt'
        shutil.copy(data, dest)
        logging.debug('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        self.count+=1
        if len(fileslist)==(self.count)+1:
            pass

    def test_05(self):
        """TS-916:Test Crawling with a tiny URL
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()

        data=self.data+'tinyurl.txt'
        dest=self.sourceDir+'/tinyurl.txt'
        shutil.copy(data, dest)
        logging.debug('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')
        checking='seedUrl='+inp.read()
        if checking not in otp.read():
            raise TestFailure('Input URL nor found in output file')
        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure('No output file generated')

    def test_06(self):
        """TS-921:Test Crawling a HTTPS URL
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'https.txt'
        dest=self.sourceDir+'/tinyurl.txt'
        shutil.copy(data, dest)
        print('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')
        checking='seedUrl='+inp.read()
        if checking not in otp.read():
            raise TestFailure('Input URL nor found in output file')
        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure('No output file generated')

    def test_07(self):
        """TS-911:Tests the number of hops of the Crawler
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'enhanced.txt'
        dest=self.sourceDir+'/enhanced.txt'
        shutil.copy(data, dest)
        logging.debug('File copied to source directory')

        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path_07)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')
        checking='seedUrl='+inp.read()
        if checking not in otp.read():
            raise TestFailure('Input URL nor found in output file')
        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure('No output file generated')
        if os.path.getmtime(latest)>self.starttime:
            print(('output file generated is ',latest))
            f=open(latest, 'r+')
            if 'http://www.icann.org/topics/idn/' in f.read():
                         raise TestFailure('Failure due to invalid Hops')

            f.close()



    def test_08(self):
        """TS-922:Test crawling a FTP URL
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'ftp.txt'
        dest=self.sourceDir+'/tinyurl.txt'
        shutil.copy(data, dest)
        print('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')
        checking='seedUrl='+inp.read()
        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure('Expected Failure : Cannot Crawl FTP urls')

    def test_09(self):
        """TS-923:Test for crawling forums
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'forums.txt'
        dest=self.sourceDir+'/tinyurl.txt'
        shutil.copy(data, dest)
        print('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')
        checking='seedUrl='+inp.read()
        if checking not in otp.read():
            raise TestFailure('Input URL nor found in output file')
        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure('No output file generated')

    def test_10(self):
        """TS-1021:Test for crawling with a redirect URL
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'redirect.txt'
        dest=self.sourceDir+'/tinyurl.txt'
        shutil.copy(data, dest)
        print('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')
        checking='seedUrl='+inp.read()
        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure('No output file generated')

    def test_11(self):
        """TS-915:Tests crawler with IPV6 URL's
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'ipv6.txt'
        dest=self.sourceDir+'/ipv6.txt'
        shutil.copy(data, dest)
        logging.debug('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')
        checking='seedUrl='+inp.read()
        if checking not in otp.read():
            raise TestFailure('Input URL nor found in output file')
        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure('No output file generated')
        if os.path.getmtime(latest)>self.starttime:
            print(('output file generated is ',latest))

    def test_12(self):
        """TS-1024:Test to check accurate generation of fields in output file
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'enhanced.txt'
        dest=self.sourceDir+'/enhanced.txt'
        shutil.copy(data, dest)
        print('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        self.count+=1
        latest = max(fileslist, key=os.path.getmtime)
        fp=open(latest,'r')
        output_str = fp.readlines()
        for line in output_str:
            arr = line.split('\t')
            if arr[0]!='SocialMediaScorer':
                raise TestFailure('1st field of output file is not SocialMediaScorer')
            if not arr[2].startswith('is_social_media='):
                logging.warning(arr[2])
                raise TestFailure('3rd field is not is_social_media')
            if not arr[3].startswith('seedUrl='):
                logging.warning(arr[3])
                raise TestFailure('4th field is not seedURL')


    def test_13(self):
        """TS-917:Test Crawling for IPaddressset of URL's
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'ipaddress.txt'
        dest=self.sourceDir+'/tinyurl.txt'
        shutil.copy(data, dest)
        print('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')

        if inp.read() not in otp.read():
            raise TestFailure('Input URL nor found in output file')
        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure('No output file generated')
        if os.path.getmtime(latest)>self.starttime:
            print(('output file generated is ',latest))


    def test_14(self):
        """TS-913:Test for the Crawling time
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'ipaddress.txt'
        dest=self.sourceDir+'/tinyurl.txt'
        shutil.copy(data, dest)
        print('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path_14)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        self.count+=1
        latest = max(fileslist, key=os.path.getmtime)
        if os.path.getctime(latest)>self.starttime:
                print('File present even after crawltime is -1')

    def test_15(self):
        """TS-923:Test for crawling forums
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'socialmedia.txt'
        dest=self.sourceDir+'/tinyurl.txt'
        shutil.copy(data, dest)
        print('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')
        checking='seedUrl='+inp.read()
        if checking not in otp.read():
            raise TestFailure('Input URL nor found in output file')
        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure('No output file generated')


    def test_16(self):
        """TS-1023:Test with an image URL
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'fb_image.txt'
        dest=self.sourceDir+'/tinyurl.txt'
        shutil.copy(data, dest)
        print('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')
        num_lines = sum(1 for line in otp)
        otp.seek(0,0)

        checking='seedUrl='+inp.read()
        if checking not in otp.read():
            raise TestFailure('Input URL nor found in output file')
        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure('No output file generated')

    def test_17(self):
        """TS-961:Test for presence of all valid links
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'mysite.txt'
        dest=self.sourceDir+'/tinyurl.txt'
        shutil.copy(data, dest)
        logging.debug('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')
        if inp.read() not in otp.read():
            raise TestFailure('Input URL nor found in output file')
        otp.seek(0,0)
        _str=otp.read()
        if 'http://www.mcafeetesting.net23.net/main.html' not in _str :
            raise TestFailure('Link not present')
        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure('No output file generated')

    def test_18(self):
        """TS-918:Crawling sites with robots.txt specified
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'rei.txt'
        dest=self.sourceDir+'/rei.txt'
        shutil.copy(data, dest)
        print('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')
        if inp.read() not in otp.read():
            raise TestFailure('Input URL nor found in output file')
        otp.seek(0,0)
        inp.seek(0,0)
        _str = otp.read()

        if 'facebook.com/rei' not in _str :
            raise TestFailure('Facebook URL not presnet')
        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure
        checking='seedUrl='+inp.read()
        otp.seek(0,0)
        if checking not in otp.read():
            raise TestFailure('Input URL nor found in output file')


    def test_19(self):
        """TS-1020:Testing by ignoring robots.txt
        Raises TestFailure on fail
        """
        obj=CrawlerExecutor()
        data=self.data+'rei.txt'
        dest=self.sourceDir+'/tinyurl.txt'
        shutil.copy(data, dest)
        logging.debug('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path_19)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')
        if inp.read() not in otp.read():
            raise TestFailure
        otp.seek(0,0)
        inp.seek(0,0)
        _str=otp.read()
        otp.seek(0,0)
        if 'http://www.facebook.com/rei' in _str :
            raise TestFailure('Facebook URL present')
        checking='seedUrl='+inp.read()
        if checking not in otp.read():
            raise TestFailure('Input URL nor found in output file')

        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure('Output file not created')

    def test_20(self):
        """TS-1214:Check if https links are converted to normalised links
        Check for presence of Generalised URL format
        """
        obj=CrawlerExecutor()
        data=self.data+'enhanced.txt'
        dest=self.sourceDir+'/enhanced.txt'
        shutil.copy(data, dest)
        logging.debug('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path_19)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')
        if inp.read() not in otp.read():
            raise TestFailure
        otp.seek(0,0)
        inp.seek(0,0)
        _str=otp.read()
        otp.seek(0,0)
        print(_str)
        if '*://' not in _str:
            raise TestFailure('Expected a generalised URL')
        https_list = ['https://facebook.com/anurag' , 'https://twitter.com/anurag' , 'https://linkedin.com/anurag' , 'https://youtube.com/anurag' , 'https://anurag.com']
        for i  in https_list :
            if i in _str:
                raise TestFailure('https URL present')
        checking='seedUrl='+inp.read()
        if checking not in otp.read():
            raise TestFailure('Input URL nor found in output file')

        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure('Output file not created')

    def test_21(self):
        """TS-1213:Check for availability of proper terms in properties file
        """
        obj=CrawlerExecutor()
        data=self.data+'enhanced.txt'
        dest=self.sourceDir+'/enhanced.txt'
        shutil.copy(data, dest)
        logging.debug('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path_21)
        result = obj.run_and_validate([], [],
                                self.regexout, self.regex_mask
                                )
        fileslist = [os.path.join(self.results_path , fname) for fname in os.listdir(self.results_path )]
        print((self.count,' ',len(fileslist)))
        latest = max(fileslist, key=os.path.getmtime)
        inp=open(data,'r')
        otp=open(latest,'r')
        if inp.read() not in otp.read():
            raise TestFailure('input url not in output file')
        otp.seek(0,0)
        inp.seek(0,0)
        _str=otp.read()
        otp.seek(0,0)
        print(_str)
        if '*://' not in _str:
            raise TestFailure('Expected a generalised URL')
        https_list = [ '://twitter.com/' , '://linkedin.com/' , '://youtube.com/' ]
        for i  in https_list :
            if i in _str:
                raise TestFailure('Social Media Domains other than allowed domains are present')
        checking='seedUrl='+inp.read()
        if checking not in otp.read():
            raise TestFailure('Input URL nor found in output file')

        if os.path.getmtime(latest)<self.starttime:
            raise TestFailure('Output file not created')


if __name__ == "__main__" :
    obj1=CrawlerTests()
    #print obj1.count
    #obj1.test_18()
    #obj1.test_05()
    #obj1.test_03()
    #obj1.test_04()
    #obj1.test_05()
    #obj1.test_06()
    #obj1.test_07()
    #obj1.test_08()
    #obj1.test_09()
    #obj1.test_10()
    #obj1.test_11()
    #obj1.test_12()
    #obj1.test_13()
    #obj1.test_14()