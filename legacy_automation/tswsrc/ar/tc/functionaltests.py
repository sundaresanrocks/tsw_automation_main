"""
Functional Tests
"""

from ar.arsql import ArSql
from framework.test import SandboxedTest
from lib.db.mssql import *
from lib.exceptions import TestFailure
from framework.ddt import testgen_file, tsadriver
from lib.db.u2_urls import U2Urls
from lib.db.u2_worktask import WorkTask
from lib.db.u2_categories import U2Categories
from ar.arlib import Validate


@tsadriver
class FunctionalTests(SandboxedTest):
    """
    """

    @classmethod
    def setUpClass(self):
        self.mssql_obj = TsMsSqlWrap(db='U2')
        self.urls_obj = U2Urls()
        self.worktask_obj = WorkTask(self.mssql_obj)

    def test_01(self):
        """mwg-1635:Run Autorating: Schedule URL
        """
        url_id = self.urls_obj.get_id_from_url('http://MCAFEETESTING.NET23.NET/samples/cat-mk.html')
        # url_id=self.urls_obj.get_id_from_url('http://JOCOCUPS.COM')



        ## check to see if scheduled count has been updated in the url_state table
        ret = []
        ret = self.urls_obj.get_row_by_url_id_from_url_state(url_id)
        scheduled_count = ( ret.pop() )['scheduled_count']
        logging.info('Checking the scheduled count of url in url state table')
        if scheduled_count != 1:
            raise TestFailure(
                'scheduled count for url id %s Found is %s , it should have been 1' % ( url_id, scheduled_count ))
        logging.info('scheduled count for the url in url state table is 1 as expected')

        ## check to see whether the url was inserted in the WorkTask table
        ret = []
        ret = self.worktask_obj.get_row_by_url_id(url_id)
        row_count = len(ret)
        logging.info('Checking the url in the WorkTask table')
        if row_count != 1:
            raise TestFailure(
                'There are %s rows for that url in WorkTask table. There should be only one row' % row_count)
        businessProcessId = ( ret.pop() )['businessProcessId']
        if businessProcessId != 5:
            raise TestFailure('The business process id of the url with url id %s is %s , it should have been 5' % (
                url_id, businessProcessId  ))
        logging.info('The url exists in the WorkTask table as expected')


    def test_02(self):
        """mwg-1636:Run Autorating: Dispatch URL
        """
        url_id = self.urls_obj.get_id_from_url('http://MCAFEETESTING.NET23.NET/samples/cat-mk.html')

        # # check to see whether the dispatch count is 1 and dispatch date is not NULL in the WorkTask table
        ret = []
        ret = self.worktask_obj.get_row_by_url_id(url_id)
        row_count = len(ret)
        if row_count != 1:
            raise TestFailure(
                'There are %s rows for that url in WorkTask table. There should be only one row' % row_count)
        logging.info('Checking dispatch date and dispatch count of the url in the WorkTask table')
        row = ret.pop()
        dispatchCount, dispatchDate = row['dispatchCount'], row['dispatchDate']
        if dispatchCount != 1:
            raise TestFailure(
                'dispatchCount of the url with uril id %s is %s , expected value was  1 ' % ( url_id, dispatchCount ))
        if ( type(dispatchDate) ) == type(None):
            raise TestFailure('dispatchDate of the url with uril id %s is %s , expected value was a Not NULL value ' % (
                url_id, dispatchDate ))

    # here we have to put any data file which will have category
    @testgen_file('tsw/ar/functional_test_03.json')
    def test_03(self, data):
        """mwg-1503:Run Autorating: Verify in category table
        """
        url_id = self.urls_obj.get_id_from_url('http://www.BUTTALBUM.COM')
        cat_obj = U2Categories(url_id, data, self.mssql_obj)
        logging.info('Generating actual results for category')
        cat_obj.generate_category()
        logging.info('Comparing actual and expected results')
        cat_obj.compare_categories()

    # for this test case the url entered through sfimport should have queue 86 , other criterias of LQM should be matched
    def test_04(self):
        """mwg-1514:Legacy Queue Monitor: Queue id 86
        """
        url_id = self.urls_obj.get_id_from_url('http://PORN-RANK.COM/cgi-bin/sw.cgi')

        ## check to ensure that the url with queue 86 does not exist in the WorkTask table
        ret = []
        ret = self.worktask_obj.get_row_by_url_id(url_id)
        row_count = len(ret)
        logging.info('Checking whether the url with url id %s exist in WorkTask table ' % url_id)
        if row_count != 0:
            raise TestFailure('There are %s rows for that url in WorkTask table. There should be NO row' % row_count)
        logging.info(' As expected , url with url id %s doesn\'t exist in WorkTask table  ' % url_id)

    # for this test case the url entered through sfimport should have queue 352 , other criterias of LQM should be matched
    def test_05(self):
        """mwg-1515:Legacy Queue Monitor: Queue id 352
        """
        url_id = self.urls_obj.get_id_from_url('http://CUMFIESTA.COM')

        ## check to ensure that the url with queue 352 does not exist in the WorkTask table
        ret = []
        ret = self.worktask_obj.get_row_by_url_id(url_id)
        row_count = len(ret)
        logging.info('Checking whether the url with url id %s exist in WorkTask table ' % url_id)
        if row_count != 0:
            raise TestFailure('There are %s rows for that url in WorkTask table. There should be NO row' % row_count)
        logging.info(' As expected , url with url id %s doesn\'t exist in WorkTask table  ' % url_id)


    # for this test case , after sfimport , the url should be tweaked to have stateid != 1
    def test_06(self):
        """mwg-1516:Legacy Queue Monitor: state id != 1
        """
        url_id = self.urls_obj.get_id_from_url('http://INCHSONG.COM/morecash')

        ## check to ensure that the url with state id !=1 does not exist in the WorkTask table
        ret = []
        ret = self.worktask_obj.get_row_by_url_id(url_id)
        row_count = len(ret)
        logging.info('Checking whether the url with url id %s exist in WorkTask table ' % url_id)
        if row_count != 0:
            raise TestFailure('There are %s rows for that url in WorkTask table. There should be NO row' % row_count)
        logging.info(' As expected , url with url id %s doesn\'t exist in WorkTask table  ' % url_id)

    # for this test case , after sfimport , the url should be tweaked to have scheduled count != 0 
    def test_07(self):
        """mwg-1519:Legacy Queue Monitor: schedule count != 0
        """
        url_id = self.urls_obj.get_id_from_url('http://INCHSONG.COM/morecash')

        ## check to ensure that the url with scheduled count != 0 does not exist in the WorkTask table
        ret = []
        ret = self.worktask_obj.get_row_by_url_id(url_id)
        row_count = len(ret)
        logging.info('Checking whether the url with url id %s exist in WorkTask table ' % url_id)
        if row_count != 0:
            raise TestFailure('There are %s rows for that url in WorkTask table. There should be NO row' % row_count)
        logging.info(' As expected , url with url id %s doesn\'t exist in WorkTask table  ' % url_id)

    @testgen_file('tsw/ar/functional_test_08.json')
    def test_08(self, data):
        """mwg-1502:Run Autorating: Verify scorer execution
        """
        url_id = self.urls_obj.get_id_from_url('http://www.mcafeetesting.net23.net/samples/all_cross_threshold.html')

        obj = ArSql(url_id, data, self.mssql_obj)
        obj.validate_results()


    def test_09(self):
        """mwg-1526:Disable all scorers except Chain scorer, autorate url
        """
        url = 'http://MCAFEETESTING.NET23.NET/samples/redirect.php'
        url_id = self.urls_obj.get_id_from_url(url)

        check_obj = Validate()
        expected_output = [
            '[u2.client.scorers] com.mcafee.tsw.scorer.WebFetcherScorer.scoreUrl Finished crawling URL. status=Succussful urlId=%s url=http://MCAFEETESTING.NET23.NET/samples/redirect.php httpCode=200 endURL=http://www.mcafeetesting.net23.net/samples/m1.html' % url_id,
            '[u2.client.scorers.ChainedScorerExecutor] com.mcafee.tsw.scorer.executor.ChainedScorerExecutor.executeCLDLanguageScorer CLDLanguageScorer scoring url=*://MCAFEETESTING.NET23.NET/samples/redirect.php',
            '[u2.client.scorers.cldlanguagescorer] com.mcafee.tsw.scorer.CLDLanguageScorer.scoreUrl Got cldlanguage=en for url=*://MCAFEETESTING.NET23.NET/samples/redirect.php',
            '[u2.client.scorers.ChainedScorerExecutor] com.mcafee.tsw.scorer.executor.ChainedScorerExecutor.executeCLDLanguageScorer CLD Lang for url=*://MCAFEETESTING.NET23.NET/samples/redirect.php cldlanguage=en',
            '[u2.client.scorers.Language] com.mcafee.tsw.scorer.PassthroughScorer.getPassthroughResult Scoring URL *://MCAFEETESTING.NET23.NET/samples/redirect.php',
            '[u2.client.scorers.ChainedScorerExecutor] com.mcafee.tsw.scorer.executor.ChainedScorerExecutor.executeLanguageScorer Got language=English from nutch language determiner for url=*://MCAFEETESTING.NET23.NET/samples/redirect.php',
            '[u2.client.scorers.ChainedScorerExecutor] com.mcafee.tsw.scorer.executor.ChainedScorerExecutor.scoreUrl Scoring *://MCAFEETESTING.NET23.NET/samples/redirect.php'
            ]
        data = check_obj.get_scorer_data_for_url(runtime.SCORER.host, runtime.SCORER.scorer_log, url_id,
                                                 ( url.split(':')[1] ))
        logging.warning(data)
        
    
    