from adobject import *
from adsearch import _ad_query_obj

class ADUser(ADObject):
    
    @classmethod
    def create(cls, name, container_object, password=None, upn_suffix=None, enable=True, optional_attributes={}):
        return container_object.create_user(name=name,
            password=password,
            upn_suffix=upn_suffix,
            enable=enable,
            optional_attributes=optional_attributes)

    def set_password(self, password):
        try:
            self._ldap_adsi_obj.SetPassword(password)
            self._flush()
        except pywintypes.com_error, excpt: 
            pyadutils.pass_up_com_exception(excpt)

    def force_pwd_change_on_login(self): 
        self.update_attribute('PwdLastSet',0)
    
    def grant_password_lease(self): 
        self.update_attribute('PwdLastSet',-1)

    def get_password_last_set(self): 
        """Returns datetime object of when user last reset their password."""
        return self._get_password_last_set()
        
    def set_expiration(self, dt):
        self._ldap_adsi_obj.AccountExpirationDate = dt
        self._flush()
            
ADObject._py_ad_object_mappings['user'] = ADUser