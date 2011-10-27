from pyadexceptions import *

# http://msdn.microsoft.com/en-us/library/aa772263(VS.85).aspx
ADS_GROUP_TYPE = { 
    'GLOBAL':0x2,
    'LOCAL':0x4,
    'UNIVERSAL':0x8,
    'SECURITY_ENABLED':-0x80000000}

# http://msdn.microsoft.com/en-us/library/aa772300.aspx 
ADS_USER_FLAG = { 
    'SCRIPT':0x1,
    'ACCOUNTDISABLE':0x2,
    'HOMEDIR_REQUIRED':0x8,
    'LOCKOUT':0x10,
    'PASSWD_NOTREQD':0x20,
    'PASSWD_CANT_CHANGE':0x40,
    'ENCRYPTED_TEXT_PASSWORD_ALLOWED':0x80,
    'TEMP_DUPLICATE_ACCOUNT':0x100,
    'NORMAL_ACCOUNT':0x200,
    'INTERDOMAIN_TRUST_ACCOUNT':0x800,
    'WORKSTATION_TRUST_ACCOUNT':0x1000,
    'SERVER_TRUST_ACCOUNT':0x2000,
    'DONT_EXPIRE_PASSWD':0x10000,
    'MNS_LOGON_ACCOUNT':0x20000,
    'SMARTCARD_REQUIRED':0x40000,
    'TRUSTED_FOR_DELEGATION':0x80000,
    'NOT_DELEGATED':0x100000,
    'USE_DES_KEY_ONLY':0x200000,
    'DONT_REQUIRE_PREAUTH':0x400000,
    'PASSWORD_EXPIRED':0x800000,
    'TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION':0x1000000}

PYAD_CATEGORY_TYPE_OVERRIDE_MAPPPINGS = {
    "Person":"user",
    "Organizational-Unit":"organizationalUnit",
    "Domain-DNS":"domain"}

WIN32_ERRORS = {
    0x80072030:InvalidObjectException,
    0x80072020:InvalidObjectException}

# http://msdn.microsoft.com/en-us/library/aa705940(VS.85).aspx
GENERIC_ADSI_ERRORS = {
    0x00005011L:('S_ADS_ERRORSOCCURRED','During a query, one or more errors occurred.','Verify that the search preference can be legally set and, if so, that it is properly set.',win32Exception),
    0x00005012L:('S_ADS_NOMORE_ROWS','The search operation has reached the last row.','Move on to the rest of the program.',win32Exception),
    0x00005013L:('S_ADS_NOMORE_COLUMNS','The search operation has reached the last column for the current row.','Move on to next row.',win32Exception),
    0x80005000L:('E_ADS_BAD_PATHNAME','An invalid ADSI pathname was passed.','Verify that the object exists on the directory server and check for typographic errors of the path.',win32Exception),

    0x80005001L:('E_ADS_INVALID_DOMAIN_OBJECT','An unknown ADSI domain object was requested','Verify the path of the domain object.',win32Exception),
    0x80005002L:('E_ADS_INVALID_USER_OBJECT','An unknown ADSI user object was requested.','Verify the existence of the user object, check for typos of the path and the user access right',win32Exception),
    0x80005003L:('E_ADS_INVALID_COMPUTER_OBJECT','An unknown ADSI computer object was requested.','Verify the existence of the computer object, check for typos of the path and the computer access rights.',win32Exception),
    0x80005004L:('E_ADS_UNKNOWN_OBJECT','An unknown ADSI object was requested.','Verify the name of and the access rights to the object.',win32Exception),
    
    0x80005005L:('E_ADS_PROPERTY_NOT_SET','The specified ADSI property was not set.','',win32Exception),
    0x80005006L:('E_ADS_PROPERTY_NOT_SUPPORTED','The specified ADSI property is not supported.','Verify that the correct property is set.',win32Exception),
    0x80005007L:('E_ADS_PROPERTY_INVALID','The specified ADSI property is invalid.','Verify that the search preference can be legally set and, if so, that it is properly set.',win32Exception),
    0x80005008L:('E_ADS_BAD_PARAMETER','One or more input parameters are invalid.','Verify that the search preference can be legally set and, if so, that it is properly set.',win32Exception),
    
    0x80005009L:('E_ADS_OBJECT_UNBOUND','The specified ADSI object is not bound to a remote resource.','Call GetInfo on a newly created object after SetInfo has been called.',win32Exception),
    0x8000500AL:('E_ADS_PROPERTY_NOT_MODIFIED','The specified ADSI object has not been modified','',win32Exception),
    0x8000500BL:('E_ADS_PROPERTY_MODIFIED','The specified ADSI object has been modified.','',win32Exception),
    0x8000500CL:('E_ADS_CANT_CONVERT_DATATYPE','The data type cannot be converted to/from a native DS data type.','Verify that the correct data type is used and/or that there is sufficient schema data available to perform data type conversion.',win32Exception),

    0x8000500DL:('E_ADS_PROPERTY_NOT_FOUND','The property cannot be found in the cache.','Verify that attribute exists for particular object.',win32Exception),
    0x8000500EL:('E_ADS_OBJECT_EXISTS','The ADSI object already exists.','Use a different name to create the object.',win32Exception),
    0x8000500FL:('E_ADS_SCHEMA_VIOLATION','The attempted action violates the directory service schema rules.','',win32Exception),
    0x80005010L:('E_ADS_COLUMN_NOT_SET','The specified column in the ADSI was not set.','',win32Exception),
    0x80005014L:('E_ADS_INVALID_FILTER','The specified search filter is invalid.','Use the correct format of the filter accepted by the directory server.',win32Exception)}
    
# http://msdn.microsoft.com/en-us/library/aa705941(VS.85).aspx
GENERIC_COM_ERRORS = { 
    0x80004004:('E_ABORT','Operation aborted.'),
    0x80004005:('E_FAIL','Unspecified error.'),
    0x80004002:('E_NOINTERFACE','Interface not supported.'),
    0x80004001:('E_NOTIMPL','Not implemented.'),
    0x80004003:('E_POINTER','Invalid pointer.'),
    0x8000FFFF:('E_UNEXPECTED','Catastrophic failure.')}
