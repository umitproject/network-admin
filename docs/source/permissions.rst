Permissions system reference
============================

Network Administrator has its own permissions system, which is different
than the one provided by Django. Permissions in NA are granted per object.
This approach lets you to easily share hosts and networks.

ObjectPermission model
----------------------

Permissions system is based on ObjectPermission model, which is used to store
information about connections between users and objects.

.. Note::
    This model is the lowest level of the system, and it should be used only
    by NA's core modules.

.. class:: ObjectPermission()

    Simple relation between a user and object, describing
    permission for access to this object by user

    .. attribute:: user

        User who has been granted permission

    .. attribute:: content_type

    .. attribute:: object_id

    .. attribute:: content_object

        Points to the object on which the permission was granted
    
    .. attribute:: edit

        If ``True``, user will be able to edit object

Class-based permissions system
------------------------------

Since class-based approach is much better then using functions, we applied it
to the permissions system. Now both Host and Network models are subclassing
SharedObject class [#sharedobject]_, which provides a bunch of useful methods
for granting and revoking access and for getting information about users who
are sharing an object.

.. class:: SharedObject()

    Subclass for every model you want to be shared by users

    .. method:: has_access (user)

        Returns True if user has permission to access the object

    .. method:: can_edit (user)

        Returns True if user has permission to edit the object

    .. method:: share (user, edit=False)

        Grants user an access to the object and sets edit permission
        to specified value (by default: False)

    .. method:: revoke (user)

        Revokes user an access to the object

    .. method:: sharing_users ()

        Returns list of users who share the object

    .. classmethod:: shared_objects(user)

        Returns list of objects owned or shared by the user

The other advantage of SharedObject is that you don't have to import
any function - everything you need is inside an object. Look at the example
below to see how it works:

    >>> host = Host.objects.all()[0]
    >>> owner = User.objects.all()[0]
    >>> friend = User.objects.all()[1]
    >>> host.user = owner
    >>> host.save()
    >>> host.has_access(owner)
    True
    >>> host.has_access(friend)
    False
    >>> host.share(friend)
    <ObjectPermission: for friend on host>
    >>> host.has_access(friend)
    True
    >>> host.revoke(owner)
    Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
    CannotRevoke: The user is owner of this host
    >>> host.revoke(friend)
    >>> host.has_access(friend)
    False
    

Utility functions (deprecated)
------------------------------

The only proper way of accessing permissions is through methods provided
by SharedObject class. However some of core modules are still using functions
that are listed below. Until we fix this issue, the following section will
stay in the documentation.

.. function:: user_has_access(obj, user)

    Returns ``True`` if user has permission to access the object

.. function:: user_can_edit(obj, user)

    Returns ``True`` if user has permission to edit the object

.. function:: filter_user_objects(user, model)

    Returns all objects accessible to the user

.. function:: grant_access(obj, user)

    Grants user an access on the object

.. function:: revoke_access(obj, user)

.. function:: grant_edit(obj, user)

.. function:: revoke_edit(obj, user)

.. function:: get_object_or_forbidden(model, object_id, user)

    Returns tuple of two elements: the first is the object, the second is
    ``True`` or ``False``, whether the user is able to edit the object or not.
    If the user has no access to the object, the ``Http404`` exception
    is raised.

.. rubric:: Footnotes

.. [#sharedobject] SharedObject class is defined in
    ``netadmin.permissions.utils`` module
