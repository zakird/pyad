import adsearch
import pyadutils
from adbase import *

class ADObject(ADBase):
    """Python object that represents any active directory object."""
    _ldap_adsi_obj = None
    _gc_adsi_obj = None
    _schema_adsi_obj = None
    _domain_pyad_obj = None
    _mandatory_attributes = None
    _optional_attributes = None
    _py_ad_object_mappings = {}

    def __init__(self, distinguished_name=None, adsi_ldap_com_object=None, options={}):
        if adsi_ldap_com_object:
            self._ldap_adsi_obj = adsi_ldap_com_object
        elif distinguished_name:
            if 'server' in options: 
                self.default_ldap_server = options['server']
            if 'port' in options:
                self.default_ldap_port = options['port']
            self.__ads_path = pyadutils.generate_ads_path(distinguished_name, 'LDAP', self.default_ldap_server, self.default_ldap_port)
            try:
                self._ldap_adsi_obj = self.adsi_provider.getObject('',self.__ads_path)
            except pywintypes.com_error, excpt: 
                additional_info = {
                    'distinguished_name':distinguished_name,
                    'server':self.default_ldap_server,
                    'port':self.default_ldap_port
                }
                pyadutils.pass_up_com_exception(excpt, additional_info)
        else:
            raise Exception("Either a distinguished name or a COM object must be provided to create an ADObject")
            
        # by pulling the DN from object instead of what is passed in, we gaurantee correct capitalization
        self.__distinguished_name = self.get_attribute('distinguishedName', False)
        self.__object_guid = pyadutils.convert_guid(self.get_attribute('objectGUID', False))
        # Set pyAD Object Type
        occn = self.get_attribute('objectCategory',False)
        if occn:
            # pull out CN from DN
            object_category_cn = occn.split('=',1)[1].split(",",1)[0]
            # some object categories are not very human readable so we provide the option to override
            if object_category_cn in PYAD_CATEGORY_TYPE_OVERRIDE_MAPPPINGS:
                self._type = PYAD_CATEGORY_TYPE_OVERRIDE_MAPPPINGS[object_category_cn]
            else:
                self._type = object_category_cn.lower()
        else:
            self._type = 'unknown'

    @classmethod
    def from_guid(cls, guid, options={}):
        "Generates ADObject based on  GUID"
        guid = "<GUID=%s>" % guid.strip('}').strip('{')
        return cls.from_dn(guid, options)

    @classmethod
    def from_dn(cls, distinguished_name, options={}):
        "Generates ADObject based on distinguished name"
        return cls(distinguished_name, None, options)
    
    @classmethod
    def from_cn(cls, cn, search_base=None, options={}): 
        return cls(adsearch.by_cn(cn, search_base, options), None, options)

    @classmethod 
    def from_com_object(cls, com_object): 
        "Generates ADObject based on an existing ADSI com object"
        return cls(distinguished_name=None, adsi_ldap_com_object=com_object)
    
    def __get_prefixed_cn(self): 
        prefix = 'ou' if self.type == 'organizationalUnit' else 'cn'
        return '='.join((prefix, self.get_attribute(prefix, False)))

    def __get_object_sid(self):
        sid = self.objectSid
        return pyadutils.convert_sid(sid) if sid else None

    dn = property(fget=lambda self: self.__distinguished_name, doc="Distinguished Name (DN) of the object")
    prefixed_cn = property(fget=__get_prefixed_cn, doc="Prefixed CN (such as 'cn=mycomputer' or 'ou=mycontainer' of the object")
    guid = property(fget=lambda self: self.__object_guid, doc="Object GUID of the object")
    adsPath = property(fget=lambda self: self.__ads_path, doc="ADsPath of Active Directory object (such as 'LDAP://cn=me,...,dc=com'")
    type = property(fget=lambda self: self._type, doc="pyAD object type (user, computer, group, organizationalUnit, domain).")
    parent_container_path = property(fget=lambda self: self.dn.split(',',1)[1], doc="Returns the DN of the object's parent container.")
    guid_str = property(fget=lambda self: str(self.guid)[1:-1], doc="Object GUID of the object")
    sid = property(fget=__get_object_sid, doc='Get the SID of the Active Directory object')
    
    def __hash__(self): 
        # guid is always unique so that we can depend on that for providing a unique hash
        return hash(self.guid)

    def __str__(self): 
        return "<%s '%s'>" % (self.__class__.__name__, self.dn)

    __repr__ = __str__

    def __cmp__(self, other): 
        # it doesn't make sense why you'd ever have to decide if one GUID was larger than the other, 
        # but it's important to be able to know if two pyAD objects represent the same AD object.
        if (self.guid == other.guid): 
            return 0
        elif (self.guid < other.guid): 
            return -1
        else: 
            return 1

    def __getattr__(self, attribute):
        # allow people to call for random attributes on the ADObject
        # as long as they exist in Active Directory.
        if hasattr(self._ldap_adsi_obj, attribute):
            return self.get_attribute(attribute, False)
        else:
            raise AttributeError(attribute)

    def _flush(self):
        "Commits any changes to the AD object."
        return self._ldap_adsi_obj.SetInfo()

    def _init_global_catalog_object(self, options={}): 
        """Initializes the global catalog ADSI com object to be 
        used when querying the global catalog instead of the domain directly."""
        if not self._gc_adsi_obj:
            self._gc_adsi_obj = _adsi_provider.GetObject('',pyadutils.generate_ads_path(self.dn, 'GC', options.get('server'), options.get('port')))
    
    def _init_schema_object(self): 
        if not self._schema_adsi_obj:
            self._schema_adsi_obj = win32com.client.GetObject(self._ldap_adsi_obj.schema)
            
    def get_mandatory_attributes(self): 
        """Returns a list of mandatory attributes for the particular object. 
        These attributes are guaranteed to be defined."""
        self._init_schema_object()
        if not self._mandatory_attributes:
            self._mandatory_attributes = list(self._schema_adsi_obj.MandatoryProperties)
        return self._mandatory_attributes

    def get_optional_attributes(self): 
        """Returns a list of optional attributes for the particular object. 
        These attributes may be defined, but are not guaranteed to be."""
        self._init_schema_object()
        if not self._optional_attributes:
            self._optional_attributes = list(self._schema_adsi_obj.OptionalProperties)
        return self._optional_attributes

    def get_allowed_attributes(self): 
        """Returns a list of allowed attributes for the particular object. 
        These attributes may be defined, but are not guaranteed to be."""
        return list(set(self.get_mandatory_attributes() + self.get_optional_attributes()))

    def get_attribute(self, attribute, always_return_list=True, source='LDAP'): 
        """Returns the value of any allowable LDAP attribute of the specified object.

            Keyword arguments:
              attribute -- any schema-allowed LDAP attribute (case insensitive). The attribute does not need to be defined. 
              always_return_list -- if an attribute has a single value, this specifies whether to return only the
                value or to return a list containing the single value. Similarly, if true, a query on an undefined
                attribute will return an empty list instead of a None object. If querying an attribute known to only
                contain at most one element, then it is easier to set to false. Otherwise, if querying a potentially
                multi-valued attribute, it is safest to leave at default. 
              source -- either 'LDAP' or 'GC'

            Note to experienced ADSI users:
              - If an attribute is undefined, getAttribute() will return None or [] and will not choke on the attribute.
              - In regards to always_return_list, True has similar behavior to getEx() whereas False is similar to Get()."""

        if not hasattr(self._ldap_adsi_obj, attribute):
            raise InvalidAttribute(self.dn, attribute)
        else:
            try:
                if source == 'LDAP':
                    value = self._ldap_adsi_obj.GetEx(attribute)
                elif source == 'GC':
                    self._init_global_catalog_object()
                    value = self._gc_adsi_obj.GetEx(attribute)
                if len(value) == 1 and not always_return_list:
                    return value[0]
                else:
                    return list(value) 
            # this just means that the attribute doesn't have a value which 
            # we imply means null instead of throwing an error..
            except pywintypes.com_error, excpt: 
                if pyadutils.interpret_com_exception(excpt)['error_constant'] == 'E_ADS_PROPERTY_NOT_FOUND':
                    return [] if always_return_list else None
                else:
                    pyadutils.pass_up_com_exception(excpt, {'attribute':attribute})

    def _set_attribute(self, attribute, action, new_value): 
        if not hasattr(self._ldap_adsi_obj, attribute):
            raise InvalidAttribute(self.dn, attribute)
        else:
            try: 
                self._ldap_adsi_obj.putEx(action, attribute, new_value)
            except pywintypes.com_error, excpt:
                pyadutils.pass_up_com_exception(excpt)

    def clear_attribute(self, attribute): 
        """Clears (removes) the specified LDAP attribute from the object. 
        Identical to setting the attribute to None or []."""
        if self.get_attribute(attribute) != []:
            self._set_attribute(attribute, 1, [])
            self._flush()

    def update_attribute(self, attribute, newvalue, no_flush=False): 
        """Updates any mutable LDAP attribute for the object. If you are adding or removing 
        values from a multi-valued attribute, see append_to_attribute and remove_from_attribute."""
        if newvalue in ((),[],None,''):
            return self.clear_attribute(attribute)
        elif pyadutils.generate_list(newvalue) != self.get_attribute(attribute):
            self._set_attribute(attribute, 2, pyadutils.generate_list(newvalue))
            if not no_flush: 
                self._flush()
            
    def update_attributes(self, attribute_value_dict): 
        """Updates multiple attributes in a single transaction
        attribute_value_dict should contain a dictionary of values keyed by attribute name"""
        for k, v in attribute_value_dict.iteritems():
            self.update_attribute(k,v,True)
        self._flush()

    def append_to_attribute(self, attribute, valuesToAppend): 
        """Appends values in list valuesToAppend to the specified multi-valued attribute. 
        valuesToAppend can contain a single value or a list of multiple values."""
        difference = list(set(pyadutils.generate_list(valuesToAppend)) - set(self.get_attribute(attribute)))
        if len(difference) != 0:
            self._set_attribute(attribute,3,difference)
            self._flush()

    def remove_from_attribute(self, attribute, valuesToRemove): 
        """Removes any values in list valuesToRemove from the specified multi-valued attribute."""
        difference = list(set(pyadutils.generate_list(valuesToRemove)) & set(self.get_attribute(attribute)))
        if len(difference) != 0:
            self._set_attribute(attribute,4,difference)
            self._flush()
    
    def get_user_account_control_settings(self): 
        """Returns a dictionary of settings stored within UserAccountControl.
        Expected keys for the dictionary are the same as keys in the ADS_USER_FLAG dictionary.
        Further information on these values can be found at
        http://msdn.microsoft.com/en-us/library/aa772300.aspx."""
        d = {}
        auc = self.get_attribute('UserAccountControl',False)
        for key, value in ADS_USER_FLAG.iteritems():
            d[key] = True if auc & value == value else False
        return d
            
    def set_user_account_control_setting(self, userFlag, newValue): 
        """Sets a single setting in UserAccountControl. 
        
        UserFlag must be a value from ADS_USER_FLAG dictionary keys. 
        More information can be found at http://msdn.microsoft.com/en-us/library/aa772300.aspx.
        newValue accepts boolean values"""
        if userFlag not in ADS_USER_FLAG.keys():
            raise InvalidValue("userFlag",userFlag,list(ADS_USER_FLAG.keys()))
        elif newValue not in (True, False):
            raise InvalidValue("newValue",newValue,[True,False])
        else: 
            # retreive the userAccountControl as if it didn't have the flag in question set. 
            if self.get_attribute('userAccountControl',False) & ADS_USER_FLAG[userFlag] :
                nv = self.get_attribute('userAccountControl',False) ^ ADS_USER_FLAG[userFlag] 
            else:
                nv = self.get_attribute('userAccountControl',False)
            # i f the flag is true, then the value is present and 
            # we add it to the starting point with B-OR. 
            # Otherwise, if it's false, it's just not present, 
            # so we leave it without any mention of the flag as in previous step. 
            if newValue:
                nv = nv | ADS_USER_FLAG[userFlag]
            self.update_attribute('userAccountControl',nv)
    
    def disable(self): 
        try:
            if self._ldap_adsi_obj.AccountDisabled == False:
                self._ldap_adsi_obj.AccountDisabled = True
                self._flush()
        except pywintypes.com_error, excpt: 
            pyadutils.pass_up_com_exception(excpt)

    def enable(self): 
        try:
            if self._ldap_adsi_obj.AccountDisabled == True:
                self._ldap_adsi_obj.AccountDisabled = False
                self._flush()
        except pywintypes.com_error, excpt: 
            pyadutils.pass_up_com_exception(excpt)

    def _get_password_last_set(self): 
        # http://www.microsoft.com/technet/scriptcenter/topics/win2003/lastlogon.mspx
        # kudos to http://docs.activestate.com/activepython/2.6/pywin32/html/com/help/active_directory.html
        return pyadutils.convert_datetime(self.get_attribute('pwdLastSet',False))
    
    def move(self, new_ou_object):
        """Moves the object to a new organizationalUnit. 
        
        new_ou_object expects a ADContainer object where the current object will be moved to."""
        try:
            new_ou_object._ldap_adsi_obj.MoveHere(('LDAP://'+self.dn),self.prefixed_cn)
            new_ou_object._flush()
        except pywintypes.com_error, excpt: 
            pyadutils.pass_up_com_exception(excpt)
        new_dn = ','.join((self.prefixed_cn,new_ou_object.dn))
        time.sleep(.5)
        self.__ads_path = pyadutils.generate_ads_path(new_dn, 'LDAP', self.default_ldap_server, self.default_ldap_port)
        self._ldap_adsi_obj = _adsi_provider.getObject('',self.__ads_path)
        self.__distinguished_name = self.get_attribute('distinguishedName',False)
    
    def rename(self, new_name, set_sAMAccountName=True):
        """Renames the current object within its current organizationalUnit.
        new_name expects the new name of the object (just CN not prefixed CN or distinguishedName)."""
        parent = self.get_parent_container()
        if self.type == 'organizationalUnit': pcn = 'ou='
        else: pcn = 'cn='
        pcn += new_name
        try:
            if self.type in ('user','computer','group') and set_sAMAccountName:
                self._ldap_adsi_obj.Put('sAMAccountName', new_name)
            parent._ldap_adsi_obj.MoveHere(('LDAP://'+self.dn), pcn)
            self._ldap_adsi_obj.GetInfoEx((distinguishedName, cn), 0)
            self.__distinguishedName = self.get_attribute('distinguishedName',False)
        except pywintypes.com_error, excpt: 
            pyadutils.pass_up_com_exception(excpt)
    
    def add_to_group(self, group): 
        """Adds current object to the specified group.
        group expects an ADGroup object."""
        group.add_members(self)
        
    def remove_from_group(self, group): 
        """Removes current object from the specified group.
        group expects an ADGroup object to which the current object belongs."""
        group.remove_members(self)
    
    def set_managedby(self, user):
        """Sets managedBy on object to the specified user"""
        if user:
            assert manager.__class__.__str__ == 'ADUser'
            self.update_attribute('managedBy', user.dn)
        else:
            self.clear_attribute('managedBy')

    def clear_managedby(self):
        """Sets object to be managedBy nobody"""
        return self.set_manager(None)
        
    def dump_to_xml(self, whitelist_attributes=[], blacklist_attributes=[]):
        if len(whitelist_attributes) == 0:
            whitelist_attributes = self.get_allowed_attributes()
        attributes = list(set(whitelist_attributes) - set(blacklist_attributes))
     
        doc = xml.Document()
        adobj_xml_doc = doc.createElement("ADObject")
        adobj_xml_doc.setAttribute("objectGUID", str(self.guid).lstrip('{').rstrip('}'))
        adobj_xml_doc.setAttribute("pyADType", self.type)
        doc.appendChild(adobj_xml_doc)

        for attribute in attributes:
            node = doc.createElement("attribute")
            node.setAttribute("name", attribute)
            value = self.get_attribute(attribute,False)
            if str(type(value)).split("'",2)[1] not in ('buffer','instance') and value is not None:
                if type(value) is not list:
                    try:
                        ok_elem=True
                        node.setAttribute("type", str(type(value)).split("'",2)[1])
                        try: 
                            text = doc.createTextNode(str(value))
                        except:
                            text = doc.createTextNode(value.encode("latin-1", 'replace'))
                        node.appendChild(text)
                    except: 
                        print 'attribute: %s not xml-able' % attribute
                else:
                    node.setAttribute("type", "multiValued")
                    ok_elem = False
                    try:
                        for item in value:
                            if str(type(item)).split("'",2)[1] not in ('buffer','instance') and value is not None:
                                valnode = doc.createElement("value")
                                valnode.setAttribute("type", str(type(item)).split("'",2)[1])
                                text = doc.createTextNode(str(item))
                                valnode.appendChild(text)
                                node.appendChild(valnode)
                                ok_elem=True
                    except: 
                        print 'attribute: %s not xml-able' % attribute
                if ok_elem: adobj_xml_doc.appendChild(node)
        return doc.toxml(encoding="UTF-8")
    
    def adjust_pyad_type(self):
        """Adjusts pyAD class to match object pyad type."""
        if self.type in self._py_ad_object_mappings.keys():
            self.__class__ = self._py_ad_object_mappings[self.type]
        else:
            raise Exception("Unkown type. Adjustment not possible.")
            
    def __get_parent_container(self): 
        q = ADObject.from_dn(self.parent_container_path, 
            options={'server':self.default_ldap_server,'port':self.default_ldap_port})
        q.adjust_pyad_type()
        return q
    parent_container = property(__get_parent_container)
    
    def delete(self):
        parent = self.parent_container
        if not parent:
            raise Exception("Object does not have a parent container. Cannot be deleted")
        else:
            parent.remove_child(self)
