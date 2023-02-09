"""
===================================
SFOH_Social Media Harvester tests
===================================
"""
import time
import shutil

from harvesters.harvester import *

from concat.tc.crawlertests import CrawlerExecutor
from harvesters.harvester_config import HarvesterConfig
import runtime
from tests.concat.tc.crawlerproperties import CrawlerProperties
from lib.exceptions import TestFailure


class HarvesterSFOHSocialMedia(HarvesterConfig):
    harvester_name = 'SFOH_SocialMedia'
    session_owner = 'SFOH_SocialMedia'
    properties_file = HarvesterConfig.base_conf + 'sfoh_socialmedia.properties'
    working_dir = HarvesterConfig.base_working + 'SFOH_SocialMedia/working/'
    processed_files = HarvesterConfig.base_working + 'SFOH_SocialMedia/processedFiles.txt'
    def __init__(self):
        HarvesterConfig.__init__(self)
        self.action_taken = {
            'Urls with Categories Appended': '0',
                            }
        self.rules_matched =  {
                    '(Salience=000000) Twitter - Categorize URL based on seedUrl categories': '0',
                    '(Salience=000001) Facebook - Categorize URL based on seedUrl categories': '0',
                    '(Salience=000002) Linkedin - Categorize URL based on seedUrl categories': '0',
                    '(Salience=000003) Youtube - Categorize URL based on seedUrl categories': '0',
                               }


class SFOH_SocialMedia(SandboxedHarvesterTest):
    default_har_config = HarvesterSFOHSocialMedia
    results_path = '/usr2/smartfilter/import/harvest_processor/data/SFOH_SocialMedia/working/'
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
    data=runtime.data_path+'/social_media_crawler_data/'
    def test_01(self):
        """
        Test Link id -
        Test for Accurate Rule Triggers
        """
        obj=CrawlerExecutor()

        data=self.data+'end-end.txt'
        dest=self.sourceDir+'/end-end.txt'
        shutil.copy(data, dest)
        logging.debug('File copied to source directory')
        obj.cmd_builder(crawler_path=CrawlerProperties.crawler_path,config_path=CrawlerProperties.config_path_end)
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
        #add a test for presence of all valid links
        hcon = HarvesterSFOHSocialMedia()
        hcon.action_taken['Urls with Categories Appended']='8'
        hcon.rules_matched['(Salience=000000) Twitter - Categorize URL based on seedUrl categories']='2'
        hcon.rules_matched['(Salience=000002) Linkedin - Categorize URL based on seedUrl categories']='2'
        hcon.rules_matched['(Salience=000001) Facebook - Categorize URL based on seedUrl categories']='2'
        hcon.rules_matched['(Salience=000003) Youtube - Categorize URL based on seedUrl categories']='2'
        hobj = Harvester(hcon,match_type='half')
        hobj.test_harvester_base('SFOHSocialMedia/empty.txt',hcon.action_taken, hcon.rules_matched)
        mssql_obj=TsMsSqlWrap(db='U2')
        query="select distinct c.cat_short from u2..categories c , U2..urls u where u.url_id=c.url_id and (u.url like '*://facebook.com/cisco' or\
               u.url like '*://twitter.com/mcafee' or u.url like '*://youtube.com/microsoft' or u.url like '*://linkedin.com/norton')"

        a=mssql_obj.get_select_data(query)
        logging.info(a)
        if(len(a)!=8):
            raise TestFailure('Errors in categories table')
        i=0
        for i in a:
            cat2=list(i.items())
            cat=cat2[0][1]
            if cat not in ('st','nt','md','sn','bu','bl','hw','tf'):
                raise TestFailure('Errors in categories table')
            
