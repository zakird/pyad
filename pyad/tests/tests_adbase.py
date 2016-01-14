from __future__ import absolute_import
from .pyadunittest import *

class TestADBase(ADTestCase):
    def setUp(self):
        # set all defaults back to their default
        pyad.adbase.ADBase.default_ldap_server = None
        pyad.adbase.ADBase.default_gc_server = None
        pyad.adbase.ADBase.default_ldap_port = None
        pyad.adbase.ADBase.default_gc_port = None
    
    def test_detected_forest(self):
        self.assertEqual(pyad.adbase.ADBase.default_domain, self.SANDBOX_DOMAIN)
    
    def test_detected_domain(self):
        self.assertEqual(pyad.adbase.ADBase.default_forest, self.SANDBOX_FOREST)
    
    def test_set_defaults(self):
        pyad.adbase.set_defaults(ldap_server = 'iowadc1', ldap_port = 389)
        self.assertEqual(pyad.adbase.ADBase.default_ldap_server, 'iowadc1')
        self.assertEqual(pyad.adbase.ADBase.default_ldap_port, 389)
