import sys
import datetime
import time
import types
import xml.dom.minidom as xml

# Since we're depending on ADSI, you have to be on windows...
if sys.platform != 'win32':
    raise Exception("Must be running Windows in order to use pyad.")

try:
    import win32api
    import pywintypes
    import win32com.client
except ImportError:
    raise Exception("pywin32 library required. Download from http://sourceforge.net/projects/pywin32/")
    
# Import constants and other common elements.
from pyadconstants import *
from pyadexceptions import *

# create connection to ADSI COM object
_adsi_provider = win32com.client.Dispatch('ADsNameSpaces')

# Discover default domain and forest information
__default_domain_obj = _adsi_provider.GetObject('',"LDAP://rootDSE")

# connecting to rootDSE will connect to the domain that the 
# current logged-in user belongs to.. which is generally the 
# domain under question and therefore becomes the default domain. 
_default_detected_forest = __default_domain_obj.Get("rootDomainNamingContext")
_default_detected_domain = __default_domain_obj.Get("defaultNamingContext")

class ADBase(object):
    """Base class that is utilized by all objects within package to help
    store defaults. (search, query, all AD objects)"""
    default_ldap_server = None
    default_gc_server = None
    default_ldap_port = None
    default_gc_port = None
    default_domain = _default_detected_domain
    default_forest = _default_detected_forest
    adsi_provider = _adsi_provider

def set_defaults(**kwargs):
    for k, v in kwargs.iteritems():
        assert k in ('ldap_server','gc_server','ldap_port','gc_port')
        setattr(ADBase, '_'.join(('default',k)), v)