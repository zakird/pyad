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
__default_domain_obj = _adsi_provider.GetObject('', "LDAP://rootDSE")

# connecting to rootDSE will connect to the domain that the
# current logged-in user belongs to.. which is generally the
# domain under question and therefore becomes the default domain.
_default_detected_forest = __default_domain_obj.Get("rootDomainNamingContext")
_default_detected_domain = __default_domain_obj.Get("defaultNamingContext")


class ADBase(object):
    """Base class that is utilized by all objects within package to help
    store defaults. (search, query, all AD objects)"""
    
    DEFAULTS_OPTIONS_MAPPINGS = (
        ("default_ldap_server", "server"),
        ("default_gc_server", "gc_server"),
        ("default_ldap_port", "port"),
        ("default_gc_port" "gc_port"),
        ("default_ldap_protocol", ),
        ("default_ldap_usn", "username"),
        ("default_ldap_pwd", "password"),
        ("default_ldap_authentication_flag", "authentication_flag"),
    )
    
    default_ldap_server = None
    default_gc_server = None
    default_ldap_port = None
    default_gc_port = None
    default_ldap_protocol = 'LDAP'
    default_ldap_usn = None
    default_ldap_pwd = None
    default_ldap_authentication_flag = 0  # No credentials
    default_domain = _default_detected_domain
    default_forest = _default_detected_forest
    adsi_provider = _adsi_provider

    def _set_defaults(options):
        if 'ssl' in options and options['ssl'] is True:
            self.default_ldap_protocol = 'LDAPS'
        for default, key in ADBase.DEFAULTS_OPTIONS_MAPPINGS:
            if key in options:
                setattr(self, default, options[key])
    
    def _make_options(self):
        options = dict()
        if self.default_ldap_protocol == 'LDAPS':
            options['ssl'] = True
        for default, key in ADBase.DEFAULTS_OPTIONS_MAPPINGS:
            val = getattr(self, default)
            if val:
                options[key] = val
        return options


def set_defaults(**kwargs):
    for k, v in kwargs.iteritems():
        assert k in ('ldap_server', 'gc_server', 'ldap_port',
                        'gc_port', 'ldap_protocol',
                        'ldap_authentication_flag', 'ldap_usn', 'ldap_pwd')
        setattr(ADBase, '_'.join(('default', k)), v)
