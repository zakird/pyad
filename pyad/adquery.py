from adbase import *
import pyadutils

class ADQuery(ADBase):
    def __init__(self):
        self.__adodb_conn = win32com.client.Dispatch("ADODB.Connection")
        self.__adodb_conn.Open("Provider=ADSDSOObject")
        self.reset()
    
    def reset(self):
        self.__rs = self.__rc = None
        self.__queried = False

    def execute_query(self, attributes=["distinguishedName"], where_clause=None, type="LDAP", base_dn=None, server=None, port=None):
        if not base_dn:
            if type == "LDAP": 
                base_dn = self.default_domain
            if type == "GC": 
                base_dn = default_forest
        query = "SELECT %s FROM '%s'" % (','.join(attributes), pyadutils.generate_ads_path(base_dn, type, server, port))
        if where_clause:
            query = ' '.join((query, 'WHERE', where_clause))
        self.__rs,self.__rc = self.__adodb_conn.Execute(query)
        self.__queried = True

    def get_row_count(self):
        return self.__rs.RecordCount

    def get_single_result(self):
        if self.get_row_count() != 1:
            raise invalidResults(self.get_row_count())
        self.__rs.MoveFirst()
        d = {}
        for f in self.__rs.Fields:
            d[f.Name] = f.Value
        return d

    def get_results(self):
        if not self.__queried:
            raise noExecutedQuery
        if not self.__rs.EOF:
            self.__rs.MoveFirst()
        while not self.__rs.EOF:
            d = {}
            for f in self.__rs.Fields:
                d[f.Name] = f.Value
            yield d
            self.__rs.MoveNext()

    def get_all_results(self):
        if not self.__queried:
            raise noExecutedQuery
        l = []
        for d in self.get_results():
            l.append(d)
        return l