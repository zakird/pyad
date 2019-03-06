from __future__ import absolute_import
from .adquery import *
from .adbase import * 

_ad_query_obj = ADQuery()

def by_cn(cn, search_base=None, options={}):
    if not search_base:
        if not ADBase.default_domain:
            raise Exception("Unable to detect default domain. Must specify search base.")
        search_base = ADBase.default_domain
    _ad_query_obj.reset()
    
    _ad_query_obj.execute_query(where_clause=("CN = '%s'" % cn), 
        base_dn=search_base,
        options=options,
        type="GC")
    return _ad_query_obj.get_single_result()['distinguishedName']

def by_upn(upn, search_base=None, options={}):
    if not search_base: 
        if not ADBase.default_forest:
            raise Exception("Unable to detect default forest. Must specify search base.")
        search_base = ADBase.default_forest
    _ad_query_obj.reset()
    _ad_query_obj.execute_query(where_clause=("userPrincipalName = '%s'" % upn), 
        base_dn=search_base, 
        type="GC", 
        options=options)
    return _ad_query_obj.get_single_result()['distinguishedName']

def by_sid(sid, search_base=None, options={}):
    if not search_base:
        if not ADBase.default_domain:
            raise Exception("Unable to detect default domain. Must specify search base.")
        search_base = ADBase.default_domain
    _ad_query_obj.reset()
    _ad_query_obj.execute_query(where_clause=("objectSid = '%s'" % sid), 
        base_dn=search_base, 
        options=options, 
        type="GC")
    return _ad_query_obj.get_single_result()['distinguishedName']

def all_results_by_cn(cn, search_base=None, options={}):
    if not search_base:
        if not ADBase.default_domain:
            raise Exception("Unable to detect default domain. Must specify search base.")
        search_base = ADBase.default_domain
    _ad_query_obj.reset()
    
    _ad_query_obj.execute_query(where_clause=("CN = '%s'" % cn), 
        base_dn=search_base,
        options=options,
        type="GC")
    return [result['distinguishedName'] for result in _ad_query_obj.get_all_results()]

def all_results_by_upn(upn, search_base=None, options={}):
    if not search_base: 
        if not ADBase.default_forest:
            raise Exception("Unable to detect default forest. Must specify search base.")
        search_base = ADBase.default_forest
    _ad_query_obj.reset()
    _ad_query_obj.execute_query(where_clause=("userPrincipalName = '%s'" % upn), 
        base_dn=search_base, 
        type="GC", 
        options=options)
    return [result['distinguishedName'] for result in _ad_query_obj.get_all_results()]

def all_results_by_sid(sid, search_base=None, options={}):
    if not search_base:
        if not ADBase.default_domain:
            raise Exception("Unable to detect default domain. Must specify search base.")
        search_base = ADBase.default_domain
    _ad_query_obj.reset()
    _ad_query_obj.execute_query(where_clause=("objectSid = '%s'" % sid), 
        base_dn=search_base, 
        options=options, 
        type="GC")
    return [result['distinguishedName'] for result in _ad_query_obj.get_all_results()]