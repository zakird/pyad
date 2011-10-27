from adobject import *

class ADComputer(ADObject):
    """"""
    @classmethod
    def create(cls, name, container_object, enable=True, optional_attributes={}):
        assert type(name) == str
        assert container_object.__class__.__name__ == 'ADContainer'
        return container_object.create_computer(name=name,enable=enable,optional_attributes=optional_attributes)

    def get_creator(self):
        """returns ADUser object of the user who added the computer to the domain. Returns None if user no longer exists."""
        try:
            sid = str(pyadutils.convert_sid(self.get_attribute('mS-DS-CreatorSID', False))).split(':')[1]
            dn = adsearch.by_sid(sid)
            return ADUser(dn)
        except:
            return None

ADObject._py_ad_object_mappings['computer'] = ADComputer