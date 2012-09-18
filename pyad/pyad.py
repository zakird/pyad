from adobject import *
from pyadexceptions import InvalidObjectException, invalidResults
import aduser, adcomputer, addomain, addomain, adgroup, adobject, pyadconstants, adcontainer

def from_cn(common_name, search_base=None, options={}):
    try:
        q = ADObject.from_cn(common_name, search_base, options)
        q.adjust_pyad_type()
        return q
    except invalidResults:
        return None

def from_dn(distinguished_name, options={}):
    try:
        q = ADObject.from_dn(distinguished_name,options)
        q.adjust_pyad_type()
        return q
    except InvalidObjectException:
        return None

def from_guid(cls, guid, options={}):
    "Generates ADObject based on  GUID"
    try:
        guid = "<GUID=%s>" % guid.strip('}').strip('{')
        q = ADObject.from_dn(guid, options)
        q.adjust_pyad_type()
        return q
    except InvalidObjectException:
        return None
