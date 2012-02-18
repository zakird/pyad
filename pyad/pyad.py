from adobject import *
from pyadexceptions import InvalidObjectException, invalidResults
import aduser, adcomputer, addomain, addomain, adgroup, adobject, pyadconstants, adcontainer

def from_cn(common_name, search_base=None, options={}):
    try:
        q = ADObject.from_cn(common_name, search_base, options)
        if q.type in ADObject._py_ad_object_mappings.keys():
            q.__class__ = ADObject._py_ad_object_mappings[q.type]
        return q
    except invalidResults:
        return None

def from_dn(distinguished_name, options={}):
    try:
        q = ADObject.from_dn(distinguished_name,options)
        if q.type in ADObject._py_ad_object_mappings.keys():
            q.__class__ = ADObject._py_ad_object_mappings[q.type]
        return q
    except InvalidObjectException:
        return None

