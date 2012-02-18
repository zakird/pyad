from adobject import *
from aduser import ADUser
from adcomputer import ADComputer
from adgroup import ADGroup
import pyadconstants

class ADContainer(ADObject):
    def get_children_iter(self, recursive=False, filter_=None):
        for com_object in self._ldap_adsi_obj:
            q = ADObject.from_com_object(com_object)
            q.adjust_pyad_type()
            if q.type == 'organizationalUnit' and recursive:
                for c in q.get_children_iter(recursive=recursive):
                    if not filter_ or c.__class__ in filter_: 
                        yield c
            if not filter or q.__class__ in filter_: 
                yield q
    
    def get_children(self, recursive=False, filter_=None): 
        return list(self.get_children_iter(recursive=recursive, filter_=filter_))
    
    def __create_object(self, type_, name):
        prefix = 'ou' if type_ == 'organizationalUnit' else 'cn'
        prefixed_name = '='.join((prefix,name))
        return self._ldap_adsi_obj.Create(type_, prefixed_name)
    
    def create_user(self, name, password=None, upn_suffix=None, enable=True,optional_attributes={}):
        try:
            if not upn_suffix:
                upn_suffix = self.get_domain().get_default_upn()
            upn = '@'.join((name, upn_suffix))
            obj = self.__create_object('user', name)
            obj.Put('sAMAccountName', name)
            obj.Put('userPrincipalName', upn)
            obj.SetInfo()
            pyadobj = ADUser.from_com_object(obj)
            if enable:
                pyadobj.enable()
            if password:
                pyadobj.set_password(password)
            pyadobj.update_attributes(optional_attributes)
            return pyadobj
        except pywintypes.com_error, e: 
            pyadutils.pass_up_com_exception(e)

    def create_group(self, name, security_enabled=True, scope='GLOBAL', optional_attributes={}):
        try:
            obj = self.__create_object('group', name)
            obj.Put('sAMAccountName',name)
            val = pyadconstants.ADS_GROUP_TYPE[scope]
            if security_enabled: 
                val = val | pyadconstants.ADS_GROUP_TYPE['SECURITY_ENABLED']
            obj.Put('groupType',val)
            obj.SetInfo()
            pyadobj = ADGroup.from_com_object(obj)
            pyadobj.update_attributes(optional_attributes)
            return pyadobj
        except pywintypes.com_error, e: 
            pyadutils.pass_up_com_exception(e)

    def create_container(self, name, optional_attributes={}):
        try:
            obj = self.__create_object('organizationalUnit', name)
            obj.SetInfo()
            pyadobj = ADContainer.from_com_object(obj)
            pyadobj.update_attributes(optional_attributes)
            return pyadobj
        except pywintypes.com_error, e: 
            pyadutils.pass_up_com_exception(e)

    def create_computer(self, name, enable=True,optional_attributes={}):
        try:
            obj = self.__create_object('computer', name)
            obj.Put('sAMAccountName', name)
            obj.SetInfo()
            pyadobj = ADComputer.from_com_object(obj)
            if enable:
                pyadobj.enable()
            pyadobj.update_attributes(optional_attributes)
            return pyadobj
        except pywintypes.com_error, e: 
            pyadutils.pass_up_com_exception(e)

    def remove_child(self, child):
        self._ldap_adsi_obj.Delete(child.type, child.prefixed_cn)
        
ADObject._py_ad_object_mappings['organizationalUnit'] = ADContainer
