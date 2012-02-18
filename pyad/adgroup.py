from adobject import *
import pyadconstants

class ADGroup(ADObject):

    @classmethod
    def create(cls, name, container_object, security_enabled=True, scope='GLOBAL', optional_attributes={}):
        return container_object.create_group(name=name, 
            security_enabled=security_enabled, 
            scope=scope, 
            optional_attributes=optional_attributes)
    
    def add_members(self, members): 
        """Accepts a list of pyAD objects or a single pyAD object and adds as members to the group."""
        return self.append_to_attribute('member', map(lambda member: member.dn, pyadutils.generate_list(members)))

    def remove_members(self, members): 
        """Accepts a list of pyAD objects or a single pyAD object and removes these as members from the group."""
        return self.remove_from_attribute('member', map(lambda member: member.dn, pyadutils.generate_list(members)))

    def remove_all_members(self): 
        """Removes all members of the group."""
        return self.remove_from_attribute('member',self.get_attribute('member'))

    def get_members(self, recursive=False, ignoreGroups=False):
        """Returns a list of group members.
            recursive - True/False. Determines whether to recursively traverse through nested groups.
            ignoreGroups - True/False. Determines whether or not to return an ADGroup objects in list or to ignore them."""
        return self._get_members(recursive, ignoreGroups, [])
        
    def _get_members(self, recursive, ignoreGroups, processedGroups): 
        """Returns a list of pyAD objects that are members of the group."""
        processedGroups.append(self.guid)
        # we need to keep track of which groups have been enumerated so far so that 
        # we don't enter an infinite loop accidentally if group A is a member 
        # of group B and group B is a member of group A. 
        m = [] 
        for dn in self.get_attribute('member'):
            pyADobj = pyAD(dn)
            if pyADobj.type == 'group' and pyADobj.guid not in processedGroups:
                if recursive:
                    m.extend(pyADobj._get_members(recursive=True, 
                        ignoreGroups=ignoreGroups, 
                        processedGroups=processedGroups))
                if not ignoreGroups:
                    m.append(pyADobj)
            elif pyADobj.type != "group":
                m.append(pyADobj)
        return list((set(m))) # converting to set removes duplicates
        
    def sync_membership(self, new_population):
        "Synchronizes membership of group so that it matches the list of entries in new_population"
        current_members = set(self.get_members())
        new_population = set(new_population)
        self.add_members(list(new_population - current_members))
        self.remove_members(list(current_members - new_population))

    def check_contains_member(self, check_member, recursive=False): 
        """Checks whether a pyAD object is a member of the group.
            check_member expects a pyAD object to be checked.
            recursive expects True/False which determines whether the group membership will be searched recursively."""
        if check_member in self.get_members(recursive=recursive, ignoreGroups=False):
            return True
        else:
            return False

    def get_group_scope(self): 
        """Returns the group scope GLOBAL, UNIVERSAL, or LOCAL."""
        group_type = self.get_attribute('groupType', False)
        if group_type & pyadconstants.ADS_GROUP_TYPE['GLOBAL'] == pyadconstants.ADS_GROUP_TYPE['GLOBAL']:
            return 'GLOBAL'
        elif group_type & pyadconstants.ADS_GROUP_TYPE['UNIVERSAL'] == pyadconstants.ADS_GROUP_TYPE['UNIVERSAL']:
            return 'UNIVERSAL'
        else:
            return 'LOCAL'

    def set_group_scope(self, new_scope): 
        """Sets group scope. new_scope expects GLOBAL, UNIVERSAL, or LOCAL."""
        if new_scope in ('LOCAL','GLOBAL','UNIVERSAL'):
            self.update_attribute('groupType',(self.get_attribute('groupType',False) & pyadconstants.ADS_GROUP_TYPE['SECURITY_ENABLED']) | pyadconstants.ADS_GROUP_TYPE[new_scope])
        else:
            raise InvalidValue("new_scope",new_scope,('LOCAL','GLOBAL','UNIVERSAL'))

    def get_group_type(self):
        """Returns group type DISTRIBUTION or SECURITY.""" 
        if self.get_attribute('groupType',False) in (2,4,8): # 0x2, 0x4, 0x8 are the distribution group types since a security group must include -0x80000000.
            return 'DISTRIBUTION'
        else:
            return 'SECURITY'

    def set_group_type(self, new_type):
        """Sets group type. new_type expects DISTRIBUTION or SECURITY."""
        if new_type == 'DISTRIBUTION': 
            self.update_attribute('groupType',(self.get_attribute('groupType',False) ^ pyadconstants.ADS_GROUP_TYPE['SECURITY_ENABLED']))
        elif new_type == 'SECURITY':
            self.update_attribute('groupType',(self.get_attribute('groupType',False)\
                ^ pyadconstants.ADS_GROUP_TYPE['SECURITY_ENABLED'])\
                | _ADS_GROUP_TYPE['SECURITY_ENABLED'])
        else:
            raise InvalidValue("new_type",new_type,('DISTRIBUTION','SECURITY'))
        
ADObject._py_ad_object_mappings['group'] = ADGroup

def __get_memberOfs(self, recursive=False, scope='all'):
    return self._get_memberOfs(recursive, scope, [])

def __is_member_of(self, group, recursive=False):
    return group in self.get_memberOfs(recursive=recursive)

def ___p_get_memberOfs(self, recursive=False, scope='all', processed_groups=[]):
    """Returns a list of groups (ADGroup objects) that the current object is a member of.
    
    recursive - True/False. This determines whether to return groups that the object is nested into indirectly.
    scope - domain, forest, all. This determines whether to only return group membership within the current domain (queries from domain) (scope=domain),
        the forest (will only include universal groups, queries from global catalog) (scope=forest), or both (scope=all)
    processed_groups - reserved, leave empty."""
    
    if self not in processed_groups:
        if scope in ('domain','all'):
            for dn in self.get_attribute('memberOf'):
                obj = ADGroup.from_dn(dn)
                if recursive and obj not in processed_groups and dn != self.dn:
                    processed_groups.extend(obj._get_memberOfs(recursive, scope, processed_groups))
                processed_groups.append(obj)
        if scope in ('forest','all'):
            for dn in self.get_attribute('memberOf',source='GC'):
                obj = ADGroup.from_dn(dn)
                if recursive and obj not in processed_groups and dn != self.dn:
                    processed_groups.extend(obj._get_memberOfs(recursive, scope, processed_groups))
                processed_groups.append(obj)
    return list(set(processed_groups))

ADObject.get_memberOfs = __get_memberOfs
ADObject.is_member_of = __is_member_of
ADObject._get_memberOfs = ___p_get_memberOfs
