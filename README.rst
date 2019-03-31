Introduction
============

pyad is a Python library designed to provide a simple, Pythonic interface to Active Directory through ADSI on the Windows platform. Complete documentation can be found at http://zakird.github.io/pyad/. Code is maintained at https://github.com/zakird/pyad. The library can be downloaded from PyPI at https://pypi.python.org/pypi/pyad.


Requirements
============

pyad requires pywin32, available at http://sourceforge.net/projects/pywin32.

Alternatively,
::
    pip install pypiwin32

works as well.


Connecting to Active Directory
==============================

By default, pyad will connect to the Active Directory domain to which the machine is joined (rootDSE)::

    from pyad import aduser
    user = aduser.ADUser.from_cn("myuser")


However, it is possible to connect to a specific domain controller or to use alternate credentials, by calling pyad.set_defaults() or by passing in connection information in the options dictionary for each object you connect to. Authentication is performed over a secured connection, pyad will not pass credentials over clear text. The following options can be set in the `set_defaults` call: `ldap_server`, `gc_server`, `ldap_port`, `gc_port`, `username`, `password`, and `ssl` (True/False). For example, the following code will set the default connection parameters for all objects accessed through pyad::

    from pyad import *
    pyad.set_defaults(ldap_server="dc1.domain.com", username="service_account", password="mypassword")
    user = pyad.aduser.ADUser.from_cn("myuser")


It is also possible to pass in options when connecting to a specific object. This will not set the library defaults, but these settings will be used from any objects you derive from it (e.g. if you request group membership of a user) Example::

   from pyad import aduser
   user = aduser.ADUser.from_cn("myuser", options=dict(ldap_server="dc1.domain.com"))


Basic Object Manipulation
=========================

There are first order Python classes for different types of objects in Active Directory. For example, ADUser represents user objects and ADGroup represents groups. All objects subclass ADObject. Most methods are defined in ADObject, but subclasses generally provide additional helper methods (e.g. ADUser has `set_password` and ADGroup has `add_member`).

It is possible to connect to an object by distinguished name, CN, UPN, and GUID if you already know the type of object. Examples::

    from pyad import aduser
    user1 = aduser.ADUser.from_dn("cn=myuser, ou=staff, dc=domain, dc=com")
    user2 = aduser.ADUser.from_cn("myuser")
    user3 = aduser.ADUser.from_guid("XXX-XXX-XXX")


It is also possible to use the pyad factory with an arbitrary Active Directory object and to receive an appropriately classed Python object::

    from pyad import pyad
    user = pyad.from_cn("user1")
    computer = pyad.from_dn("cn=WS1,ou=Workstations,dc=domain,dc=com")
    group = pyad.from_guid("XXX-XXX-XXX")


Unlike the ADSI interface, pyad objects are intended to interact with one another. Instead of adding the DN of a user to the members attribute of a group to add the user, you instead add the user object to the group. For instance::

    user1 = ADUser.from_cn("myuser1")
    user2 = ADUser.from_cn("myuser2")
    group = ADGroup.from_dn("staff")

    group.add_members([user1, user2])

    for user in group.get_members():
        print user1.description


However, it is still possible to directly manipulate any attribute outside of the helper methods that pyad provides::

    user1 = ADUser.from_cn("myuser1")
    user.set_attribute("description", "new description")
    user.append_to_attribute("member", "cn=myuser1, ou=staff, dc=domain, dc=com")


More details on how to manipulate the objects you find to is found in the next section.


Creating, Moving, and Deleting Objects
======================================

There are two methodologies for creating and deleting objects. In both cases, you must first bind to the parent container. When creating a new object, several attributes are required, but other additional attributes can be specified with the `optional_attributes` parameter. Example 1::

    ou = ADContainer.from_dn("ou=workstations, dc=domain, dc=com")

    # create a new group without any optional attributes
    new_computer = ADComputer.create("WS-489", ou)

    # create a new group with additional attributes
    new_group = ADGroup.create("IT-STAFF", security_enabled=True, scope='UNIVERSAL',
                    optional_attributes = {"description":"all IT staff in our company"})

It is also possible to create new objects from the parent container::

    ou = ADContainer.from_dn("ou=workstations, dc=domain, dc=com")
    computer = ou.create_computer("WS-490")

Once objects are created, they can be moved::

    computer = ADComputer.from_cn("WS-500")
    computer.move(ADContainer.from_dn("ou=workstations, ou=HR, dc=company, dc=com"))

or renamed::

    computer = ADComputer.from_cn("WS-500")
    computer.rename("WS-501")

Objects can be removed by calling delete()::

    ADComputer.from_cn("WS-500").delete()


Searching Active Directory
==========================

As shown above, objects can be directly connected to via CN, DN, GUID, or UPN. However, objects can also be searched for through the ADQuery interface (and in the background, this is how objects are actually found when you connect by CN). It is important to note that the ADQuery interface will not provide you with pyad objects, but instead with only the attributes for which you queried, for performance reasons. Example::

    import pyad.adquery
    q = pyad.adquery.ADQuery()

    q.execute_query(
        attributes = ["distinguishedName", "description"],
        where_clause = "objectClass = '*'",
        base_dn = "OU=users, DC=domain, DC=com"
    )

    for row in q.get_results():
        print row["distinguishedName"]

License
=======

pyad is licensed under the Apache License, Version 2.0 (the "License"). You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
