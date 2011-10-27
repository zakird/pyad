from pyadunittest import *

class TestADQuery(ADTestCase):
    def setUp(self):
        self.ad_query = pyad.adquery.ADQuery()
    
    def test_dne_rowcount(self):
        query = "cn = '%s'" % self.KNOWN_DNE_OBJECT
        self.ad_query.execute_query(where_clause = query)
        self.assertEqual(self.ad_query.get_row_count(), 0)
        
    def test_dne_single_result(self):
        query = "cn = '%s'" % self.KNOWN_DNE_OBJECT
        self.ad_query.execute_query(where_clause = query)
        self.assertRaises(pyad.pyadexceptions.invalidResults, self.ad_query.get_single_result)
        
    def test_dne_all_results(self):
        query = "cn = '%s'" % self.KNOWN_DNE_OBJECT
        self.ad_query.execute_query(where_clause = query)
        self.assertEqual(self.ad_query.get_all_results(), [])
        
    def test_single_rowcount(self):
        query = "cn = '%s'" % self.KNOWN_EXISTS_USER
        self.ad_query.execute_query(where_clause = query)
        self.assertEqual(self.ad_query.get_row_count(), 1)
        
    def test_single_single_result(self):
        query = "cn = '%s'" % self.KNOWN_EXISTS_USER
        self.ad_query.execute_query(attributes=("cn","distinguishedname"),where_clause = query)
        self.assertEqual(self.ad_query.get_single_result()['cn'],self.KNOWN_EXISTS_USER)
        
    def test_single_all_results(self):
        query = "cn = '%s'" % self.KNOWN_EXISTS_USER
        self.ad_query.execute_query(attributes=("cn","distinguishedname"),where_clause = query)
        self.assertEqual(self.ad_query.get_all_results()[0]['cn'],self.KNOWN_EXISTS_USER)
        
    def test_multiple_rowcount(self):
        query = "cn = '%s' or cn = '%s'" % (self.KNOWN_EXISTS_USER, self.KNOWN_EXISTS_COMPUTER)
        self.ad_query.execute_query(where_clause = query)
        self.assertEqual(self.ad_query.get_row_count(), 2)
        
    def test_multiple_single_result(self):
        query = "cn = '%s' or cn = '%s'" % (self.KNOWN_EXISTS_USER, self.KNOWN_EXISTS_COMPUTER)
        self.ad_query.execute_query(where_clause = query)
        self.assertRaises(pyad.pyadexceptions.invalidResults, self.ad_query.get_single_result)
        
    def test_multiple_all_results(self):
        query = "cn = '%s' or cn = '%s'" % (self.KNOWN_EXISTS_USER, self.KNOWN_EXISTS_COMPUTER)
        self.ad_query.execute_query(attributes=("cn","distinguishedname"),where_clause = query)
        r = map(lambda x: x['cn'], self.ad_query.get_all_results())
        k = [self.KNOWN_EXISTS_USER, self.KNOWN_EXISTS_COMPUTER]
        self.assertEqual(r.sort(),k.sort())
 