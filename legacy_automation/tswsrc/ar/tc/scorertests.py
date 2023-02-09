"""
Scorer Tests
"""

import unittest

from ar.arsql import ArSql
from framework.test import SandboxedTest
from lib.db.mssql import *
from lib.exceptions import TestFailure
from framework.ddt import testgen_file, tsadriver
from lib.db.u2_urls import U2Urls
from ar.arlib import Validate


@tsadriver
class ScorerTests(SandboxedTest):
    """
    """
    @classmethod
    def setUpClass(self):
        self.mssql_obj=TsMsSqlWrap(db='U2')
        self.urls_obj=U2Urls()
        
                               
    def test_01( self ):
        """mwg-1493:Scorer: Language scorer
        """
        url = 'http://MCAFEETESTING.NET23.NET/samples/cat-mk.html'
        url_id=self.urls_obj.get_id_from_url(url)
        logging.info ( 'Checking if nutch Language Scorer identified correct language for url %s with urlid %s '  % ( url , url_id ) )
        
        expected_output = [ '[u2.client.scorers.ChainedScorerExecutor] com.mcafee.tsw.scorer.executor.ChainedScorerExecutor.executeLanguageScorer Got language=English from nutch language determiner for url=*://MCAFEETESTING.NET23.NET/samples/cat-mk.html urlId=%s' %url_id ]
        check_obj = Validate()
        data = check_obj.get_scorer_data_for_url( runtime.SCORER.host , runtime.SCORER.scorer_log , url_id , ( url.split(':')[1] ))
        logging.warning (data)
        check_obj.validate_in_scorer_data ( data , expected_output )
        
        #check_obj.validate( envcon.SCORER.host , envcon.SCORER.scorer_log , expected_output )

    def test_02( self ):
        """mwg-1481:Scorer: Web fetcher scorer: sanity
        """
        url = 'http://MCAFEETESTING.NET23.NET/samples/cat-mk.html'
        url_id=self.urls_obj.get_id_from_url(url)
        logging.info ( 'Checking if Web Fetcher Scorer ran as the firs thing for url %s with urlid %s '  % ( url , url_id ) )



        check_obj = Validate()
        expected_output = [#'[u2.client.scorers.ScorerExecutorManager] com.mcafee.tsw.scorer.executor.ScorerExecutorManager.run Adding task to the crawlQueue. urlId=%s url=*://MCAFEETESTING.NET23.NET/samples/cat-mk.html' %url_id , \
                            #'Sending url to the WebPageFetcher. urlId=%s url=*://MCAFEETESTING.NET23.NET/samples/cat-mk.html' %url_id , \
                            #'Fetching content for urlId=%s url=http://MCAFEETESTING.NET23.NET/samples/cat-mk.html' %url_id , \
                            'Finished crawling URL. status=Succussful urlId=%s url=http://MCAFEETESTING.NET23.NET/samples/cat-mk.html httpCode=200 endURL=http://mcafeetesting.net23.net/samples/cat-mk.html' %url_id,
                            #'WebPageFetcher results. urlId=%s url=*://MCAFEETESTING.NET23.NET/samples/cat-mk.html returnCode=0' %url_id
                            ]
        data = check_obj.get_scorer_data_for_url( runtime.SCORER.host , runtime.SCORER.scorer_log , url_id , ( url.split(':')[1] ))
        logging.warning (data)
        check_obj.validate_in_scorer_data ( data , expected_output )

    
    @testgen_file('tsw/ar/scorer_test_04.json', 'tsw/ar/scorer_test_05.json')
    def test_03( self , data ):
        """mwg-1484:Scorer: RTC Scorer/mwg-1485:Scorer: RTC Scorer- blogs
        """
        url_id=self.urls_obj.get_id_from_url(data['url'])
        obj = ArSql( url_id , data , self.mssql_obj)
        obj.validate_results()

    def test_04( self ):
        """mwg-1633:Web Fetcher: Follows redirects in a redirect loop
        """
        url = 'http://MCAFEETESTING.NET23.NET/samples/rloop1.php'
        url_id=self.urls_obj.get_id_from_url(url)
        check_obj = Validate()
        #expected_output = [ '[u2.client.scorers] com.mcafee.tsw.scorer.WebFetcherScorer.scoreUrl Finished crawling URL. status=Unsuccessful urlId=%s url=http://MCAFEETESTING.NET23.NET/samples/rloop1.php' %url_id ]
        expected_output = [ 'Finished crawling URL. status=Unsuccessful urlId=%s' %url_id ]
        data = check_obj.get_scorer_data_for_url( runtime.SCORER.host , runtime.SCORER.scorer_log , url_id , ( url.split(':')[1] ))
        logging.warning ( data)
        check_obj.validate_in_scorer_data ( data , expected_output )

    def test_05( self ):
        """mwg-1632:Web Fetcher: Follows redirects and get content
        """
        url = 'http://MCAFEETESTING.NET23.NET/samples/redirect.php'
        url_id=self.urls_obj.get_id_from_url(url)
        check_obj = Validate()
        #expected_output = [ '[u2.client.scorers] com.mcafee.tsw.scorer.WebFetcherScorer.scoreUrl Finished crawling URL. status=Succussful urlId=%s url=http://MCAFEETESTING.NET23.NET/samples/redirect.php httpCode=200 endURL=http://www.mcafeetesting.net23.net/samples/m1.html' %url_id]
        expected_output = [ 'Finished crawling URL. status=Succussful urlId=%s url=http://MCAFEETESTING.NET23.NET/samples/redirect.php httpCode=200 endURL=http://www.mcafeetesting.net23.net/samples/m1.html' %url_id]
        data = check_obj.get_scorer_data_for_url( runtime.SCORER.host , runtime.SCORER.scorer_log , url_id , ( url.split(':')[1] ))
        logging.warning ( data)
        check_obj.validate_in_scorer_data ( data , expected_output )

    def test_06( self ):
        """mwg-1494:20130517-19:56:00 Scorer: Language scorer - Chinese
        """
        url = 'http://ZH.WIKIPEDIA.ORG'
        url_id=self.urls_obj.get_id_from_url(url)
        check_obj = Validate()
        expected_output = [ #'[u2.client.scorers] com.mcafee.tsw.scorer.WebFetcherScorer.scoreUrl Finished crawling URL. status=Succussful urlId=%s url=http://ZH.WIKIPEDIA.ORG httpCode=200 endURL=http://zh.wikipedia.org/wiki/Wikipedia:' %url_id , \
                            'Finished crawling URL. status=Succussful urlId=%s url=http://ZH.WIKIPEDIA.ORG httpCode=200 endURL=http://zh.wikipedia.org/wiki/Wikipedia:' %url_id ,
                             '[u2.client.scorers.cldlanguagescorer] com.mcafee.tsw.scorer.CLDLanguageScorer.scoreUrl Begin Chromium language detector scoring for url=*://ZH.WIKIPEDIA.ORG urlId=%s' %url_id  ,
                             '[u2.client.scorers.cldlanguagescorer] com.mcafee.tsw.scorer.CLDLanguageScorer.scoreUrl Got cldlanguage=zh for url=*://ZH.WIKIPEDIA.ORG urlId=%s' %url_id ,
                             '[u2.client.scorers.ChainedScorerExecutor] com.mcafee.tsw.scorer.executor.ChainedScorerExecutor.executeLanguageScorer Got language=Chinese from nutch language determiner for url=*://ZH.WIKIPEDIA.ORG urlId=%s' %url_id ,
                              ]
        data = check_obj.get_scorer_data_for_url( runtime.SCORER.host , runtime.SCORER.scorer_log , url_id , ( url.split(':')[1] ))
        logging.warning ( data)
        check_obj.validate_in_scorer_data ( data , expected_output )

    def test_07( self ):
        """mwg-1482:Scorer: Web fetcher scorer: 404
        """
        url = 'http://www.youtube.com/mcafeetesting.net23.net'
        url_id=self.urls_obj.get_id_from_url(url)
        check_obj = Validate()
        expected_output = [ #'[u2.client.scorers] com.mcafee.tsw.scorer.WebFetcherScorer.scoreUrl Finished crawling URL. status=Succussful urlId=%s url=http://YOUTUBE.COM/mcafeetesting.net23.net httpCode=404 endURL=http://youtube.com/mcafeetesting.net23.net' %url_id , \
                            'Finished crawling URL. status=Succussful urlId=%s url=http://YOUTUBE.COM/mcafeetesting.net23.net httpCode=404 endURL=http://youtube.com/mcafeetesting.net23.net' %url_id ,
                             '[u2.client.scorers.ChainedScorerExecutor] com.mcafee.tsw.scorer.executor.ChainedScorerExecutor.scoreUrl Content for url=*://YOUTUBE.COM/mcafeetesting.net23.net urlId=%s' %url_id  ,
                           ]
        data = check_obj.get_scorer_data_for_url( runtime.SCORER.host , runtime.SCORER.scorer_log , url_id , ( url.split(':')[1] ))
        logging.warning ( data)
        check_obj.validate_in_scorer_data ( data , expected_output )

    # this test case should be run when rtc scorer is disabled
    def test_08( self ):
        """mwg-1486:Scorer: RTC Scorer - Turn OFF
        """
        url_id=self.urls_obj.get_id_from_url('http://MCAFEETESTING.NET23.NET/samples/redirect.php')
        obj = ArSql( url_id , self.mssql_obj)
        try:
            obj.generate_rtc_result()
        except IndexError as err :
            logging.info ( err )

    # this testcase should be run after all the urls are autorated
    def test_09 ( self ):
        """mwg-1498:Dispatcher: maximum retries
        """
        ret = []
        ret = self.mssql_obj.get_select_data( "select dispatchCount , urlId from u2.dbo.WorkTask (NOLOCK) " )
        logging.info ( 'Checking if any url has dispatch count greater than 3' )

        for row in ret:
            if row['dispatchCount'] > 3:
                raise TestFailure ( 'Dispatch Count for url with urlID = %s is %s . Expected value was less than or equal to 3' % ( row['urlId'] , row['dispatchCount'] ) )
        logging.info ( 'No url has dispatch count greater than 3' )                

    
    @unittest.skip('should be run before wfa and scorer are started')
    def test_10 ( self ):
        """mwg-1497:Dispatcher: default value
        """
        ret = []
        ret = self.mssql_obj.get_select_data( "select dispatchCount , urlId from u2.dbo.WorkTask (NOLOCK) " )
        logging.info ( 'Checking that all the urls in WorkTask have dispatchCount = 0' )

        for row in ret:
            if not (row['dispatchCount'] == 0) :
                raise TestFailure ( 'Dispatch Count for url with urlID = %s is %s . Expected value was 0' % ( row['urlId'] , row['dispatchCount'] ) )
        logging.info ( 'Every url has dispatchCount = 0' )                
        

    
        
    




        

    

    



    
    