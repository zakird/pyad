from __future__ import absolute_import
from .adobject import *
from .pyadexceptions import InvalidObjectException, invalidResults
from . import aduser, adcomputer, addomain, addomain, adgroup, adobject, pyadconstants, adcontainer

def from_cn(common_name, search_base=None, options={}):
    Escape = {"\\":"\\5C","*":"\\2A","(":"\\28",")":"\\29"}
    common_name = "".join([Escape.get(char, char) for char in common_name])
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

def from_guid(guid, options={}):
    "Generates ADObject based on  GUID"
    try:
        q = ADObject.from_guid(guid, options)
        q.adjust_pyad_type()
        return q
    except InvalidObjectException:
        return None
