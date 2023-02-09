"""
 Tests for CLD Scorer
"""
from ar.arsql import ArSql
from framework.test import SandboxedTest


class CLDTests(SandboxedTest):
    """
    """
    def test_01(self):
        """
        """
        data = ArSql('56516200')
        data.expected_results = self.expected_results = {
    "url": "*://FR.WIKIPEDIA.ORG",
    "scorer_event_detail": {
        "24" : {
                "result_value" : "fr" ,
                "result_type_name" : "cldlanguage"
              }
        }
       
 
}

        data.generate_cld_result()
        data.compare_cld_result()
        
    def test_02(self):
        """ """