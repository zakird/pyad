from adquery import *
from adbase import * 

_ad_query_obj = ADQuery()

def by_cn(cn, search_base=None, options={}):
    if not search_base: 
        search_base = ADBase.default_domain
    _ad_query_obj.reset()
    _ad_query_obj.execute_query(where_clause=("CN = '%s'" % cn), 
        base_dn=search_base, 
        server=options.get("server"), 
        port=options.get("port"), 
        type="GC")
    return _ad_query_obj.get_single_result()['distinguishedName']

def by_upn(upn, search_base=None, options={}):
    if not search_base: 
        search_base = ADBase.default_forest
    _ad_query_obj.reset()
    _ad_query_obj.execute_query(where_clause=("userPrincipalName = '%s'" % upn), 
        base_dn=search_base, 
        type="GC", 
        server=options.get("server"), 
        port=options.get("port"))
    return _ad_query_obj.get_single_result()['distinguishedName']

def by_sid(sid, search_base=None, options={}):
    if not search_base:
        search_base = ADBase.default_domain
    _ad_query_obj.reset()
    _ad_query_obj.execute_query(where_clause=("objectSid = '%s'" % sid), 
        base_dn=search_base, 
        server=options.get("server"), 
        port=options.get("port"), 
        type="GC")
    return _ad_query_obj.get_single_result()['distinguishedName']