Permissions system reference
============================

Network Administrator has its own permissions system, which is different
than the one that Django provides. Permissions in NA are granted per object.
This approach lets users to share hosts and networks.

ObjectPermission model
----------------------

Permissions system is based on ObjectPermission model.

.. class:: ObjectPermission()

    Simple relation between a user and object, describing
    permission for access to this object by user

    .. attribute:: user

        User who has been granted permission

    .. attribute:: content_type

    .. attribute:: object_id

    .. attribute:: content_object
    
    .. attribute:: edit

        If ``True``, user will be able to edit object

Utility functions
-----------------

The system comes with the following utility functions.

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


