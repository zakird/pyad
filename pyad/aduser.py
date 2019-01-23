from __future__ import absolute_import
from .adobject import *
from .adsearch import _ad_query_obj
import datetime

class ADUser(ADObject):
    
    @classmethod
    def create(cls, name, container_object, password=None, upn_suffix=None,
                    enable=True, optional_attributes={}):
        """Creates and returns a new active directory user"""
        return container_object.create_user(
            name=name,
            password=password,
            upn_suffix=upn_suffix,
            enable=enable,
            optional_attributes=optional_attributes
        )

    def set_password(self, password):
        """Sets the users password"""
        try:
            self._ldap_adsi_obj.SetPassword(password)
            self._flush()
        except pywintypes.com_error as excpt: 
            pyadutils.pass_up_com_exception(excpt)

    def force_pwd_change_on_login(self): 
        """Forces the user to change their password the next time they login"""
        self.update_attribute('PwdLastSet',0)
    
    def grant_password_lease(self): 
        self.update_attribute('PwdLastSet',-1)

    def get_password_last_set(self): 
        """Returns datetime object of when user last reset their password."""
        return self._get_password_last_set()
    
    def get_max_pwd_age(self):
        """Returns timespan object representing the max password age on a user's domain"""
        return pyadutils.convert_timespan(self.get_domain().maxPwdAge)
        
    def get_expiration(self):
        """Gets the expiration date of the password as a datetime object.
        The _ldap_adsi_obj.AccountExpirationDate can be inaccurate and
        return the UNIX Epoch instead of the true expiration date."""
        uac_settings = self.get_user_account_control_settings()
        if any(uac_settings[flag] for flag in ["SMARTCARD_REQUIRED",
         "DONT_EXPIRE_PASSWD", "WORKSTATION_TRUST_ACCOUNT",
         "SERVER_TRUST_ACCOUNT", "INTERDOMAIN_TRUST_ACCOUNT"]):
            return None
        elif self.get_attribute('pwdLastSet', False) is None:
            return datetime.datetime(1970,1,1)
        else:
            return self.get_password_last_set() + self.get_max_pwd_age()
            
    def set_expiration(self, dt):
        """Sets the expiration date of the password to the given value"""
        self._ldap_adsi_obj.AccountExpirationDate = dt
        self._flush()
        
    def get_password_expired(self):
        """Returns a bool representing whether the password has expired.
        The passwordexpired property will often return True even if not expired."""
        expiration_date = self.get_expiration()
        if expiration_date is None:
            return False
        return expiration_date < datetime.datetime.now()
        
    def unlock(self):
        """Unlock the user's account"""
        self.update_attribute('lockoutTime',0)
            
ADObject._py_ad_object_mappings['user'] = ADUser
