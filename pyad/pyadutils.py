from adbase import *

def convert_error_code(error_code):
    return error_code % 2 ** 32

def interpret_com_exception(excp, additional_info={}): #expects the actualy pywintypes.com_error exception that's thrown... 
    d = {}
    d['error_num'] = convert_error_code(excp.args[2][5])
    # for some reason hex() includes the L for long in the hex... however since it's a string, we don't care... since L would never be in a hex code, we can safely just remove it. 
    d['error_code'] = hex(d['error_num']).rstrip('L')
    if d['error_code'][0:7] == '0x80005':
        if d['error_num'] in GENERIC_ADSI_ERRORS.keys():
            d['exception_type'] = 'known_generic_adsi_error'
            d['error_constant'] = GENERIC_ADSI_ERRORS[d['error_num']][0]
            d['message'] = ' '.join(GENERIC_ADSI_ERRORS[d['error_num']][1:3])
        else: # this supposedly should not happen, but I'd rather be ready for the case that Microsoft made a typo somewhere than die weirdly. 
            d['error_constant'] = None
            d['exception_type'] = 'unknown_generic_adsi_error'
            d['message'] = 'unknown generic ADSI error'
            d['exception'] = genericADSIException
    elif d['error_code'][0:6] == '0x8007':
        d['exception_type'] = 'win32_error'
        d['error_constant'] = None
        d['message'] = win32api.FormatMessage(d['error_num']) # returns information about error from winerror.h file... 
    elif d['error_num'] in GENERIC_COM_ERRORS.keys():
        d['exception_type'] = 'generic_com_error'
        d['error_constant'] = GENERIC_COM_ERRORS[d['error_num']][0]
        d['message'] = GENERIC_COM_ERRORS[d['error_num']][1]
    else:
        d['exception_type'] = 'unknown'
        d['error_constant'] = None
        d['message'] = excp.args[2][4]
    d['additional_info'] = additional_info={}
    return d

def pass_up_com_exception(excp, additional_info={}):
    if excp.__class__ in (genericADSIException, comException, win32Exception):
        raise excp
    else:
        info = interpret_com_exception(excp)
        type_ = info['exception_type']
        if type_ == 'win32_error':
            # raise exception defined in WIN32_ERRORs if there is one... otherwise, just raise a generic win32Exception
            raise WIN32_ERRORS.get(info['error_num'], win32Exception)(error_info=info, additional_info=additional_info)
        elif type_ == 'known_generic_adsi_error':
            raise GENERIC_ADSI_ERRORS[info['error_num']][3](error_info=info, additional_info=additional_info)
        elif type_ == 'unknown_generic_adsi_error':
            raise genericADSIException(error_info=info, additional_info=additional_info)
        else:
            raise comException(error_info=info, additional_info=additional_info)

def convert_datetime(adsi_time_com_obj):
    """Converts 64-bit integer COM object representing time into a python datetime object."""
    # credit goes to John Nielsen who documented this at http://docs.activestate.com/activepython/2.6/pywin32/html/com/help/active_directory.html. 
    return datetime.datetime.fromtimestamp((((long(adsi_time_com_obj.highpart) << 32)\
        + long(adsi_time_com_obj.lowpart)) - 116444736000000000L)/10000000)

def convert_guid(guid_object):
    return pywintypes.IID(guid_object, True)

def convert_sid(sid_object):
    return pywintypes.SID(sid_object)

def generate_list(input):
    if type(input) is list:
        return input
    elif type(input) in (set,tuple):
        return list(input)
    else:
        return [input,]
        
def escape_path(path):
    escapes = (
        ('\\','\\5c'),
        ('*','\\2a'),
        ('(','\\28'),
        (')','\\29'),
        ('/','\\2f'),
        (chr(0),'\\00')
    )
    for char, escape in escapes:
        path = path.replace(char, escape)
    return path

def generate_ads_path(distinguished_name, type_, server=None, port=None):
    """Generates a proper ADsPath to be used when connecting to an active directory object or when searching active directory.
    
    Keyword arguments:
     - distinguished_name: DN of object or search base such as 'cn=zakir,ou=users,dc=mycompany,dc=com' (required).
     - type: 'GC' (global-catalog) or 'LDAP' to determine what directory to be searched (required).
     - server: FQDN of domain controller if necessary to connect to a particular server (optional unless port is defined).
     - port: port number for directory service if not default port. If port is specified, server must be specified (optional)."""
    
    if type_ == "LDAP":
        server = server if server else ADBase.default_ldap_server
        port = port if port else ADBase.default_ldap_port
    elif type_ == "GC":
        server = server if server else ADBase.default_gc_server
        port = port if port else ADBase.default_gc_port
    else:
        raise Exception("Invalid type specified.")
        
    ads_path = ''.join((type_,'://'))
    if server:
        ads_path = ''.join((ads_path,server))
        if port:
            ads_path = ':'.join((ads_path,str(port)))
        ads_path = ''.join((ads_path,'/'))
    ads_path = ''.join((ads_path,escape_path(distinguished_name)))
    return ads_path