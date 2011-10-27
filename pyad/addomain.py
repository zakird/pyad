from adcontainer import *

class ADDomain(ADContainer):

    def get_default_upn(self): 
        """Returns the default userPrincipalName for the domain."""
        self._ldap_adsi_obj.GetInfoEx(["canonicalName",],0)
        return self._ldap_adsi_obj.get("canonicalName").rstrip('/')
        
def __get_domain(self):
    if self._domain_pyad_obj is None:
        domain_path = 'dc=' + self.dn.lower().split("dc=",1)[1]
        self._domain_pyad_obj = ADDomain.from_dn(domain_path, 
            options={'server':self.default_ldap_server,'port':self.default_ldap_port})
    return self._domain_pyad_obj
ADObject.get_domain = __get_domain

ADObject._py_ad_object_mappings['domain'] = ADDomain