import unittest
import pyad

class ADTestCase(unittest.TestCase):
    SANDBOX_OU = "ou=pyad,ou=services,ou=ris,ou=vpr,dc=iowa,dc=uiowa,dc=edu"
    SANDBOX_DOMAIN = 'DC=iowa,DC=uiowa,DC=edu'
    SANDBOX_FOREST = 'DC=uiowa,DC=edu'
    
    KNOWN_EXISTS_USER = 'durumericz'
    KNOWN_EXISTS_COMPUTER = 'VPR0751'
    KNOWN_DNE_OBJECT = "durumeric_z"

    def assertHasAttribute(self, obj, attribute):
        self.assertTrue(hasattr(obj._ldap_adsi_obj, attribute))
        
    def assertAttributeValue(self, obj, attribute, value):
        self.assertEqual(obj._ldap_adsi_obj.GetEx(attribute), value)