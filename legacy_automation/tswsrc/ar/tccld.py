"""
=============================
Autorating: CLD test cases
=============================


"""

import logging

from lib.exceptions import ValidationError
from framework.test import SandboxedTest
from lib.u2.u2_scorers import ScorerMap, ScorerFactGenerator
from lib.db.u2_urls import U2Urls
from lib.db.mssql import TsMsSqlWrap
from lib.exceptions import TestFailure


def validate_cld(url):
    """Validates an url by executing test_canon and verifying if error is
    encounterd in stdout/stderr streams
    """


from framework.ddt import testgen_file, tsadriver, testdata_file
@tsadriver
class CLD(SandboxedTest):
    """CLD Language scorer related tests cases"""

    cld_id = ScorerMap.get_id('CLDLanguageScorer')
    qry = '''select SE.url_id, SED.result_value, urls.url from urls, scorer_event_detail as SED, (select event_id, url_id from scorer_event where scorer_id=%(cld_id)s) as SE where SED.event_id = SE.event_id and SE.url_id = urls.url_id'''
    u2_con = TsMsSqlWrap('U2')

    def verify_url(self, url, lang):
        """function to verify language for one url"""
        url_id = U2Urls().get_id_from_url(url)
        #url_id = '56516239'
        #todo: hook u2_CON with common autorating system
        cld_facts = ScorerFactGenerator(url_id).get_cld_languages()
        logging.info('CLD Facts: %s' % cld_facts)
        for fact_value in cld_facts:
            if fact_value != lang:
                with open('man.tmp', 'a+') as fp:
                    fp.write(lang + '\n')
                raise TestFailure('CLD Language Mismatch:\n\texpected lang:' \
                    '%s \n\tactual lang:%s \n\turl: %s ' % 
                    (lang, cld_facts, url))
        if len(cld_facts) == 0:
            raise TestFailure('URLNOTFOUND: Cld score not found for %s' % url)

    @testgen_file('tsw/ar/cld-list.csv')
    def test_cld_(self, url_tuple):
        self.verify_url(url_tuple[0], url_tuple[1])
        
    @testdata_file('tsw/ar/cld-bz888338.csv')
    def test_cld_bz_888338(self, url_tuples):
        msg = ''
        for url_t in url_tuples:
            try:
                self.verify_url(url_t[0], url_t[1])
            except TestFailure as err:
                msg += '\n\n' + err.args[0]
        if msg != '':
            raise TestFailure(msg)

    def test_bigint_value_in_detail_table(self):
        """mwg-1638:Autorating: Detail_id in scorer_event_detail table should be big int

        """
        url = 'en.wikipedia.org'
        url_id = U2Urls().get_id_from_url(url)
        events = ScorerFactGenerator(url_id).get_all_event_details()
        if not (len(events) >= 1):
            raise ValidationError('No Event details found!')
        if not (events[0]['detail_id'] > 72000000000000):
            raise ValidationError('Event deail should be greater than 72000000000000. Please initialize with dbcc query if needed!')



    def test_cld_2(self):
        """CLD: CLD must be run for all urls when Chained Scorer is enabled
        The number of events for Web fetcher and cld scorere are equal
        """
        #for each url_id:
        #    ensure that count(web fetcher) == count(cld)

    @testdata_file('tsw/ar/cld-func.csv')
    def test_cld_func(self, data):
        """test template for functional tests"""
