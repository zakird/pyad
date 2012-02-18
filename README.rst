Introduction
------------

pyad is a python library designed to provide a simple, object oriented interface to Active Directory through ADSI on the Windows platform. pyad requires pywin32, available at http://sourceforge.net/projects/pywin32.

pyad is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

A copy of the GNU General Public License is available at <http://www.gnu.org/licenses/>.

Basics
------

Active Directory objects are represented by standard python objects. There are classes for all major types of Active Directory objects: ADComputer, ADContainer, ADDomain, ADGroup, ADUser, all of which inherit from ADObject. It is possible to connect to objects via CN, DN, and GUID. The type will automatically be selected at runtime. Example::

    from pyad import pyad
    u = pyad.from_cn("user1")
    c = pyad.from_dn("cn=WS1,ou=Workstations,dc=domain,dc=com")
    g = pyad.from_cn("group1")
    
It is possible to read attribute values in two ways.::

    print u.displayName
    print u.get_attribute("displayName")
    
Attributes can be set by calling clear_attribute, update_attribute, update_attributes, append_to_attribute, and remove_from_attribute. Example::

    u.update_attribute("displayName", "new value")

There are other helper methods available for managing attributes. We provide further examples below for common actions for each object type.

Group Examples
--------------

1. Finding group members::

	for object in g.get_members(recursive=False):
		print object

2. Adding an object to a group::

	g.add_members(u)

or::

	u.add_to_group(g)

3. Set group scope::

	g.set_group_scope("UNIVERSAL")

User Examples
-------------

1. Set password::

	u.set_password("new_plaintext_password")

2. Force password change on login::

	u.force_pwd_change_on_login()

Container Examples
------------------

1. Find all objects in an OU::

	ou = pyad.adcontainer.ADContainer.from_dn("OU=Workstations,DC=company,DC=com")
	for obj in ou.get_children():
		print obj
		
2. Recursively find all computers below a certain OU::

	for c in ou.get_children(recursive=True, filter=[pyad.adcomputer.ADComputer]):
		print c
		
Creating Objects
----------------

It is possible to create objects through pyad. Example::

	ou = pyad.adcontainer.ADContainer.from_dn("OU=Workstations,DC=company,DC=com")
	c = pyad.adcomputer.ADComputer.create(
		name = 'myworkstation2',
		container_object = ou,
		enable = True,
		optional_attributes = dict(
			description = "newly created computer"
		)
	)
	
Querying
--------

It is also possible to make queries to find objects. Example::

	q = pyad.adquery.ADQuery()
	q.execute_query(
		attributes = ['distinguishedname', 'description'],
		where_clause = "cn like 'ws%'",
		base_dn = "dc=company,dc=com"
	)
	for r in q.get_results():
		print r['distinguishedname']

