"""
Tests for DCC Scorer
"""

import os.path

import runtime
from ar.arsql import ArSql
from framework.test import SandboxedTest
from lib.db.mssql import *
from lib.exceptions import TestFailure, ExecutionError
from framework.ddt import testgen_file, tsadriver
from lib.db.u2_urls import U2Urls
from lib.u2.u2_scorers import ScorerMap, ScorerFactGenerator


@tsadriver
class DCCTests(SandboxedTest):
    """
    """
    @classmethod
    def setUpClass(self):
        self.mssql_obj=TsMsSqlWrap(db='U2')
        self.urls_obj=U2Urls()
        
    @testgen_file('tsw/ar/sp.json',
                  'tsw/ar/bl.json',
                  'tsw/ar/bu.json',
                  'tsw/ar/gm.json',
                  'tsw/ar/sx.json',
                  'tsw/ar/mk.json',
                  'tsw/ar/il.json',
                  'tsw/ar/en_fr.json',
                  'tsw/ar/en_wiki.json'
                  
                  )
    def test_cat(self,data):
        """
        mwg-1629, mwg-1622, mwg-1621, mwg-1624, mwg-1628, 1627, mwg-1625,mwg-1614
        cat-sp
        Check for categories and scores
        """
        url_id=self.urls_obj.get_id_from_url(data['url'])
        
        ar_obj = ArSql(url_id, data)
        ar_obj. generate_dcc_result() 
        ar_obj.compare_scorer_event_detail()
    
    def test_02(self):
        """
        mwg-1609
        path to rules package in scorer.properties
        """
        ssh_obj = runtime.get_ssh(runtime.SCORER.host, 'toolguy')
        ssh_obj.get(runtime.SCORER.prop_scorer,'./scorer.properties')
        if not os.path.exists('./scorer.properties'):
            raise ExecutionError('Unable to copy scorer.properties from scorer machine')
        
        fp = open('./scorer.properties','r')
        for line in fp.readlines():
            if 'DCCScorer.rulePackage' in line:
                var = line.split('=')
                var[1]=var[1].strip()
                if var[1]!='/opt/sftools/conf/dcc/mwgdc-rules.zip':
                    raise TestFailure('Rules.zip not present in properties file in ' + runtime.SCORER.prop_scorer)
        try:
            os.remove('/tmp/scorer.properties')
        except Exception as e:
            logging.error(e)
            
    def test_03(self):
        """
        mwg-1610
        Check for DCC Scorer entry in Database
        """
        
        query="select * from u2.dbo.scorers where name = '" + ScorerMap.get_name('DCCScorer') + "'"
        row_count=self.mssql_obj.get_row_count(query)
        if row_count==0:
            raise TestFailure('DCC Scorer Entry not present in the Database')
        elif row_count>1:
            raise TestFailure('DCC Scorer Entry present more than once in Database')
    
    def test_04(self):
        """
        mwg-1611
        Check if DCC Scorer is enabled in Database
        """
        query="select scorer_id,enabled from u2.dbo.scorers where name='" + ScorerMap.get_name('DCCScorer') + "'"
        result_set = self.mssql_obj.get_select_data(query)
        if not (result_set[0])['enabled']:
                raise TestFailure('DCC Scorer is not enabled in database')
            
            
    def test_05(self):
        """
        mwg-1618
        URL with pdf
        """
        url_id = self.urls_obj.get_id_from_url('http://www.mcafeetesting.net23.net/samples/documentation.pdf')
        sc_obj = ScorerFactGenerator(url_id)
        result = sc_obj.get_dcc_facts()
        if len(result) != 0:
            raise TestFailure('DCC Scorer returned a value for a URL pointing to a PDF file')
        
    def test_06(self):
        """
        mwg-1619
        URL with Jpeg
        """
        url_id=self.urls_obj.get_id_from_url('http://www.mcafeetesting.net23.net/samples/pic2.jpg')
        sc_obj = ScorerFactGenerator(url_id)
        result = sc_obj.get_dcc_facts()
        if len(result) != 0:
            raise TestFailure('DCC Scorer returned a value for a URL pointing to a JPEG file')
    
    def test_07(self):
        """
        mwg-1616
        404 URL
        """
        url_id=self.urls_obj.get_id_from_url('http://www.ineverexisted.com')
        sc_obj = ScorerFactGenerator(url_id)
        result = sc_obj.get_dcc_facts()
        if len(result) != 0:
            raise TestFailure('DCC Scorer returned a value for a URL with no content')
    
    @testgen_file('tsw/ar/cld-ko.json',
                  'tsw/ar/cld-hi.json',
                  'tsw/ar/cld-kk.json')
    def test_08(self,data):
        """
        mwg-1612
        Korean Language URL
        """
        url_id=self.urls_obj.get_id_from_url(data['url'])
        
        ar_obj = ArSql(url_id, data)
        sc_obj = ScorerFactGenerator(url_id)
        cld_result = sc_obj.get_cld_languages()
        if len(cld_result) == 0:
            raise TestFailure('CLD Scorer did not determine any language for '+str(url_id))
        dcc_result = sc_obj.get_dcc_facts()
        if len(dcc_result) != 0:
            raise TestFailure('DCC Scorer returned a value for a URL for which CLD returned language other than english')
    
    @testgen_file('tsw/ar/redirect.json')    
    def test_09(self,data):
        """

        URL redirecting to a different page
        """
        url_id=self.urls_obj.get_id_from_url( data['url'] )
        ar_obj = ArSql(url_id, data)
        ar_obj. generate_dcc_result() 
        ar_obj.compare_scorer_event_detail()
        
    def test_10(self):
        """
        Cyclic redirect
        """
        url_id=self.urls_obj.get_id_from_url( 'http://www.mcafeetesting.net23.net/samples/rloop1.php' )
        sc_obj = ScorerFactGenerator(url_id)
        result = sc_obj.get_dcc_facts()
        if len(result) != 0:
            raise TestFailure('DCC Scorer returned a value for an infinite looping URL')
        
        
    
        
    
        
        
