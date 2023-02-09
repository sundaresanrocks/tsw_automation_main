"""
Class to get data from scorer_events , scorer_event_details , WorkTask tables

"""

from lib.db.mssql import *
from lib.exceptions import TestFailure


class ArSql:
    """Class for getting data from autorating related tables"""

    def __init__(self, urlid, expected_results=None, u2_con=None):
        if isinstance(u2_con, TsMsSqlWrap):
            self.u2_con = u2_con
        else:
            self.u2_con = TsMsSqlWrap('U2')
        self.urlid = urlid
        self.actual_results = {
            "scorer_event_detail": {}
        }
        self.query_order_by_scorer_id = self.u2_con.get_select_data(
            "select * from u2.dbo.scorer_event (NOLOCK) where url_id = %s order by scorer_id" % self.urlid)

        # To be moved to taqaap04.py
        self.scorer_ids = {'webfetcher_scorer': 1, 'language_scorer': 3, 'rtc_scorer': 2, 'cld_scorer': 24,
                           'dcc_scorer': 23}

        self.set_by = runtime.AR.set_by
        self.expected_results = expected_results
        # To be brought in from runtime.data_path


    def verify_scorer_events(self):
        """This function will verify that for a particular url , all the scorers have uniquely recorded their event id in the scorer_event table
        """
        ret = []
        scorer_count = 0
        ret = self.query_order_by_scorer_id
        row_count = self.u2_con.get_row_count(
            "select * from u2.dbo.scorer_event (NOLOCK) where url_id = %s" % self.urlid)
        if row_count == 0:
            raise AssertionError('NO RECORD FOUND : url id %s doesn\'t exist in scorer_event table ' % self.urlid)
        if row_count < len(self.expected_results['scorer_event']):
            raise AssertionError(
                'LESS RECORDS FOUND : url id %s doesn\'t have events for all the scorers ' % self.urlid)
        if row_count > len(self.expected_results['scorer_event']):
            raise AssertionError(
                'MORE RECORDS FOUND : url id %s has more events entry than the number of scorers ' % self.urlid)
        for scorer_id in self.expected_results['scorer_event']:
            for item in ret:
                if item['scorer_id'] == scorer_id:
                    scorer_count += 1
                    break
        if not scorer_count == len(self.expected_results['scorer_event']):
            raise AssertionError('url id %s doesn\'t have unique entry for all the scorers ' % self.urlid)
        logging.info('SCORER_EVENTS VERIFIED')
        return 1

    def verify_web_fetcher_scorer(self):

        """This function verifies that no entry has been made for the language scorer
        """
        ret = []
        ret = self.u2_con.get_select_data(
            "select event_id from u2.dbo.scorer_event (NOLOCK) where url_id = %s and scorer_id = %s" % (
                self.urlid, self.scorer_ids['webfetcher_scorer'] ))
        row_count = self.u2_con.get_row_count(
            "select * from u2.dbo.scorer_event_detail (NOLOCK) where event_id = %s " % ( ( ret.pop() )['event_id'] ))
        if row_count != 0:
            raise AssertionError("Unexpectedly! there is a record for web fetcher scorer")
        logging.info('WEB_FETCHER_SCORER_VERIFIED')

    def verify_language_scorer(self):
        """This function verifies that no entry has been made for the language scorer
        """
        ret = []
        ret = self.u2_con.get_select_data(
            "select event_id from u2.dbo.scorer_event (NOLOCK) where url_id = %s and scorer_id = %s" % (
                self.urlid, self.scorer_ids['language_scorer'] ))
        row_count = self.u2_con.get_row_count(
            "select * from u2.dbo.scorer_event_detail (NOLOCK) where event_id = %s " % ( ( ret.pop() )['event_id'] ))
        if row_count != 0:
            raise AssertionError("Unexpectedly! there is a record for language scorer")
        logging.info('LANGUAGE_SCORER_VERIFIED')


    def generate_rtc_result(self):
        """This function verifie if the RTC scorer gave the expected result for that url
        """
        ret = []
        ret = self.u2_con.get_select_data(
            "select event_id from u2.dbo.scorer_event (NOLOCK) where url_id = %s and scorer_id = %s" % (
                self.urlid, self.scorer_ids['rtc_scorer'] ))
        event_id = ( ret.pop() )['event_id']
        rows = self.u2_con.get_select_data(
            "select result_value , detail_id from U2..scorer_event_detail (NOLOCK) where event_id = %s  order by result_index , result_type_name " % (
                event_id ))

        # ###############################################################################################################################################
        # ## Lines of code below were written to directly take the data from the self.expected_results and match it with the actual data in the table ###

        #logging.info(rows)
        #logging.info(( self.expected_results['scorer_event_detail'] )['2'])
        #for category in ( self.expected_results['scorer_event_detail'] )['2'] :
        #    count = 0
        #    for row in rows:
        #        if category in row['result_value']:
        #            count+=1
        #            index = rows.index(row)
        #    if count == 0:
        #        raise AssertionError(' Category %s is not listed in the table ' %category)
        #    if count != 1:
        #        raise AssertionError(' Category %s is listed more than one time in the table ' %category)
        #    score_for_category = ( rows.__getitem__(index+1) )['result_value']
        #    if not score_for_category == ( ( self.expected_results['scorer_event_detail'] )['2'] )['%s' %category]:
        #        raise AssertionError(' Score for Category %s is not as expected ' %category)
        ###############################################################################################################################################


        ###################################################
        ##         generating in json format             ##
        ###################################################
        (self.actual_results['scorer_event_detail'] ).update({"2": {}})

        keyword = 'category'
        for row in rows:
            if keyword == 'category':
                category = row['result_value']
                ((self.actual_results['scorer_event_detail'] )['2'] ).update({'%s' % category: ''})
                keyword = 'score'
            else:
                score = row['result_value']
                ( ((self.actual_results['scorer_event_detail'] )['2'] ) )['%s' % category] = '%s' % score
                keyword = 'category'
        return 1

    def generate_dcc_result(self):
        """This function verifies if the DCC scorer gave the expected result for that url
        """
        ret = []
        ret = self.u2_con.get_select_data(
            "select event_id from u2.dbo.scorer_event (NOLOCK) where url_id = %s and scorer_id = %s" % (
                self.urlid, self.scorer_ids['dcc_scorer'] ))
        if len(ret) == 0:
            raise TestFailure("Returned empty result set from DB")
        event_id = ( ret.pop() )['event_id']
        rows = self.u2_con.get_select_data(
            "select result_value , detail_id from U2..scorer_event_detail (NOLOCK) where event_id = %s  order by result_index , result_type_name " % (
                event_id ))

        # ###############################################################################################################################################
        # ## Lines of code below were written to directly take the data from the self.expected_results and match it with the actual data in the table ###

        #logging.info(rows)
        #logging.info(( self.expected_results['scorer_event_detail'] )['2'])
        #for category in ( self.expected_results['scorer_event_detail'] )['23'] :
        #    count = 0
        #    for row in rows:
        #        if category in row['result_value']:
        #            count+=1
        #            index = rows.index(row)
        #    if count == 0:
        #        raise AssertionError(' Category %s is not listed in the table ' %category)
        #    if count != 1:
        #        raise AssertionError(' Category %s is listed more than one time in the table ' %category)
        #    score_for_category = ( rows.__getitem__(index+2) )['result_value']
        #    rawscore_for_category = ( rows.__getitem__(index+1) )['result_value']
        #    threshold_for_category = ( rows.__getitem__(index+3) )['result_value']
        #    if not score_for_category == ( ( ( self.expected_results['scorer_event_detail'] )['23'] )['%s' %category] )['score']:
        #       raise AssertionError(' Score for Category %s is not as expected ' %category)
        #    if not rawscore_for_category == ( ( ( self.expected_results['scorer_event_detail'] )['23'] )['%s' %category] )['rawscore']:
        #        raise AssertionError(' RawScore for Category %s is not as expected ' %category)
        #    if not threshold_for_category == ( ( ( self.expected_results['scorer_event_detail'] )['23'] )['%s' %category] )['threshold']:
        #        raise AssertionError(' Threshold for Category %s is not as expected ' %category)
        ################################################################################################################################################


        ###################################################
        ##         generating in json format             ##
        ###################################################
        (self.actual_results['scorer_event_detail'] ).update({"23": {}})

        keyword = 'category'
        for row in rows:
            if keyword == 'category':
                category = row['result_value']
                ((self.actual_results['scorer_event_detail'] )['23'] ).update({'%s' % category: {}})
                keyword = 'rawscore'
            elif keyword == 'rawscore':
                rawscore = row['result_value']
                ( ( ((self.actual_results['scorer_event_detail'] )['23'] ) )['%s' % category] ).update(
                    {'rawscore': '%s' % rawscore})
                keyword = 'score'
            elif keyword == 'score':
                score = row['result_value']
                ( ( ((self.actual_results['scorer_event_detail'] )['23'] ) )['%s' % category] ).update(
                    {'score': '%s' % score})
                keyword = 'threshold'
            elif keyword == 'threshold':
                threshold = row['result_value']
                ( ( ((self.actual_results['scorer_event_detail'] )['23'] ) )['%s' % category] ).update(
                    {'threshold': '%s' % threshold})
                keyword = 'category'
        return 1

    def compare_scorer_event_detail(self):
        """This function compares the scorer_event_detail in expected result and actual result
        """
        diff = 0
        for key in self.expected_results['scorer_event_detail']:
            for scorer_key in self.expected_results['scorer_event_detail'][key]:
                if ( self.expected_results['scorer_event_detail'] )[key][scorer_key] != \
                        ( self.actual_results['scorer_event_detail'] )[key][scorer_key]:
                    logging.info(( self.expected_results['scorer_event_detail'] )[key][scorer_key])
                    logging.info(( self.actual_results['scorer_event_detail'] )[key][scorer_key])
                    diff = 1
                    break
        if diff == 0:
            logging.info("EXPECTED AND ACTUAL SCORER_EVENT_DETAIL RESULTS MATCH ")
        elif diff == 1:
            logging.info("EXPECTED AND ACTUAL SCORER_EVENT_DETAIL RESULTS DO NOT MATCH AT KEY %s" %
                         ( self.actual_results['scorer_event_detail'] )[key][scorer_key])
            raise AssertionError("EXPECTED AND ACTUAL SCORER_EVENT_DETAIL RESULTS DO NOT MATCH AT KEY %s" %
                                 ( self.actual_results['scorer_event_detail'] )[key][scorer_key])

    def compare_categories(self):
        """
        This function compares the categories in the expected result against the actual result
        """
        diff = 0

        for key in self.expected_results['categories']:

            if ( self.expected_results['categories'] )['%s' % key] != ( self.actual_results['categories'] )['%s' % key]:
                # logging.info(( self.expected_results['categories'] )['%s'%key])
                # logging.info(( self.actual_results['categories'] )['%s'%key])
                raise AssertionError("Expected value for key %s was %s . But Found %s" % (
                    key, ( self.expected_results['categories'] )['%s' % key],
                    ( self.actual_results['categories'] )['%s' % key] ))

        if diff == 0:
            logging.info("EXPECTED AND ACTUAL CATEGORY RESULTS MATCH")


    def generate_category(self):
        """This function will verify if a given url has been aptly categorized by autorating or not
        """
        (self.actual_results).update({"categories": {}})
        rows = []
        rows = self.u2_con.get_select_data(
            "select * from u2.dbo.categories (NOLOCK) where url_id = %s and set_by = %s" % ( self.urlid, self.set_by ))
        if len(rows) == 0:
            logging.info("Autorating didn't append any category for the url with urlid %s " % self.urlid)
        elif len(rows) != 1:
            raise AssertionError(
                "There are multiple categories for the url with urlid %s set by Autorating " % self.urlid)
        elif len(rows) == 1:
            for row in rows:
                (self.actual_results['categories']).update({'set_by': '%s' % row['set_by']})
                (self.actual_results['categories']).update({'cat': '%s' % row['cat_short']})
        return 1


    def generate_worktask(self):
        """This function will verify if a given url has appropriate enries in the worktask table
        """
        (self.actual_results).update({"worktask": {}})
        rows = []
        rows = self.u2_con.get_select_data("select * from u2.dbo.worktask (NOLOCK) where urlid = %s" % ( self.urlid ))
        if len(rows) == 0:
            logging.info("No Autorating Task for the url with urlid %s " % self.urlid)
        elif len(rows) != 1:
            raise AssertionError("There are multiple entries in WorkTask for the url with urlid %s  " % self.urlid)
        elif len(rows) == 1:
            for row in rows:
                (self.actual_results['worktask']).update({'message': '%s' % row['message']})
                (self.actual_results['worktask']).update({'returnCode': '%s' % row['returnCode']})
        return 1

    def compare_worktask(self):
        """
        This function compares the WorkTask in the expected result against the actual result
        """
        diff = 0

        for key in self.expected_results['worktask']:
            if ( self.expected_results['worktask'] )['%s' % key] != ( self.actual_results['worktask'] )['%s' % key]:
                raise AssertionError("Expected value for key %s was %s , But Found %s" % (key, (
                    self.expected_results['worktask'] )['%s' % key], ( self.actual_results['worktask'] )['%s' % key]))

        if diff == 0:
            logging.info("EXPECTED AND ACTUAL WORKTASK RESULTS MATCH")


    def generate_actual_results(self):
        """This function will generate the actual result dictionary
        """

        # self.verify_scorer_events()
        ret = []
        ret = self.query_order_by_scorer_id
        for row in ret:

            if row['scorer_id'] == 1:
                self.verify_web_fetcher_scorer()
            elif row['scorer_id'] == 3:
                self.verify_language_scorer()
            elif row['scorer_id'] == 2:
                self.generate_rtc_result()
            elif row['scorer_id'] == 24:
                self.generate_cld_result()
            elif row['scorer_id'] == 23:
                self.generate_dcc_result()
        self.generate_category()
        self.generate_worktask()
        # self.compare_scorer_event_detail()
        #self.compare_categories()

        return 1

    def generate_cld_result(self):
        """This function verifies if the CLD scorer gave the expected result for that url
        """
        ret = []
        ret = self.u2_con.get_select_data(
            "select event_id from u2.dbo.scorer_event (NOLOCK) where url_id = %s and scorer_id = %s" % (
                self.urlid, self.scorer_ids['cld_scorer'] ))
        rows = ((self.u2_con.get_select_data(
            "select * from u2.dbo.scorer_event_detail (NOLOCK) where event_id = %s " % ( ( ret.pop() )['event_id'] )) ))

        # ###############################################################################################################################################
        # ## Lines of code below were written to directly take the data from the self.expected_results and match it with the actual data in the table ###

        #for row in rows:
        #    if ( '%s'%row['result_value'] != ( ( self.expected_results['scorer_event_detail'] )['24'] )['result_value'] ) and ( '%s'%row['result_type_name'] != ( ( self.expected_results['scorer_event_detail'] )['24'] )['result_type_name'] ):
        #        raise AssertionError ( 'Language found in table is not same as the expected results. Language %s was found in table' %result_value )
        ################################################################################################################################################


        ###################################################
        ##        generating in json format              ##
        ###################################################
        (self.actual_results['scorer_event_detail'] ).update({"24": {}})
        for row in rows:
            ((self.actual_results['scorer_event_detail'] )['24'] ).update({'result_value': '%s' % row['result_value']})
            ((self.actual_results['scorer_event_detail'] )['24'] ).update(
                {'result_type_name': '%s' % row['result_type_name']})
        return 1


    def compare_cld_result(self):
        """
        This function compares the CLD in the expected result against the actual result
        """
        diff = 0

        for key in (self.expected_results['scorer_event_detail'] )['24']:
            if ( (self.expected_results['scorer_event_detail'] )['24'])['%s' % key] != \
                    ((self.actual_results['scorer_event_detail'] )['24'] )['%s' % key]:
                raise AssertionError("Expected value for key %s was %s , But Found %s" %
                                     (key, (self.expected_results['scorer_event_detail'] ['24'])['%s' % key],
                                      ((self.actual_results['scorer_event_detail'] )['24'] )['%s' % key]))

        if diff == 0:
            logging.info("EXPECTED AND ACTUAL CLD LANGUAGE RESULTS MATCH")


    def validate_results(self):
        self.generate_actual_results()
        self.compare_scorer_event_detail()
        try:
            if len(self.expected_results['categories']) == 0:
                logging.warning("There are no 'set_by' and 'cat' items in categories in expected results")
            else:
                # self.generate_category()
                self.compare_categories()
            if len(self.expected_results['worktask']) == 0:
                logging.warning("There are no 'message' and 'returnCode' items in worktask in expected results")
            else:
                # self.generate_worktask()
                self.compare_worktask()
        except KeyError as err:
            logging.error("Expected results doesn't have categories result")
            logging.error("Expected results doesn't have worktask result")
            raise KeyError(err)
        return 1


if __name__ == '__main__':
    u2_con = TsMsSqlWrap('U2')
    data = ArSql('56516200', u2_con)
    data.generate_cld_result()
    data.compare_cld_result()
    
