from adobject import *
import aduser, adcomputer, addomain, addomain, adgroup, adobject, pyadconstants, adcontainer

def pyAD(distinguished_name, options={}): 
    q = ADObject(distinguished_name=distinguished_name,options=options)
    if q.type in __py_ad_object_mappings.keys():
        q.__class__ = __py_ad_object_mappings[q.type]
    return q
