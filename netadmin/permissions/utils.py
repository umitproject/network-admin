#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author: Piotrek Wasilewski <wasilewski.piotrek@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib.contenttypes.models import ContentType
from django.http import Http404

from netadmin.permissions.models import ObjectPermission

class CannotRevoke(Exception):
    """Raised in case of revoking user access to his object
    """
    pass

class SharedObject(object):
    """Subclass for every object you want to be shared by users
    """
    def has_access(self, user):
        """Returns True if user has permission to access the object
        """
        if hasattr(self, 'user') and self.user == user:
            return True

        ct = ContentType.objects.get_for_model(self.__class__)
        try:
            perm = ObjectPermission.objects.get(user=user, content_type=ct,
                object_id=self.pk)
        except ObjectPermission.DoesNotExist:
            return False

        return True

    def can_edit(self, user):
        """Returns True if user has permission to edit the object
        """
        if hasattr(self, 'user') and self.user == user:
            return True

        ct = ContentType.objects.get_for_model(self.__class__)
        try:
            perm = ObjectPermission.objects.get(user=user, content_type=ct,
                object_id=self.pk)
        except ObjectPermission.DoesNotExist:
            return False

        if perm.edit:
            return True
        else:
            return False

    def share(self, user, edit=False):
        """
        Grants user an access to the object and sets edit permission
        to specified value (by default: False)
        """
        if hasattr(self, 'user') and self.user == user:
            return

        ct = ContentType.objects.get_for_model(self.__class__)
        try:
            perm = ObjectPermission.objects.get(user=user, content_type=ct,
                object_id=self.pk)
            if perm.edit != edit:
                perm.edit = edit
                perm.save()
        except ObjectPermission.DoesNotExist:
            perm = ObjectPermission(user=user, content_object=self, edit=edit)
            perm.save()

        return perm

    def revoke(self, user):
        """Revokes user an access to the object
        """
        if hasattr(self, 'user') and self.user == user:
            raise CannotRevoke("The user is owner of this host")

        ct = ContentType.objects.get_for_model(self.__class__)
        try:
            perm = ObjectPermission.objects.get(user=user, content_type=ct,
                object_id=self.pk)
        except ObjectPermission.DoesNotExist:
            return
        perm.delete()

    @classmethod
    def shared_objects(cls, user):
        """Returns list of objects owned or shared by the user
        """
        owned = cls.objects.filter(user=user)
        pks = [obj.pk for obj in owned]

        ct = ContentType.objects.get_for_model(cls)
        access = ObjectPermission.objects.filter(content_type=ct, user=user)
        for obj in access:
            if obj.content_object.pk not in pks:
                pks.append(obj.content_object.pk)
                
        return cls.objects.filter(pk__in=pks)

def user_has_access(obj, user):
    """Returns True if user has permission to access the object"""
    if hasattr(obj, 'user') and obj.user == user:
        return True
    ct = ContentType.objects.get_for_model(obj.__class__)
    try:
        perm = ObjectPermission.objects.get(user=user, content_type=ct,
            object_id=obj.pk)
    except ObjectPermission.DoesNotExist:
        return False
    return True

def user_can_edit(obj, user):
    """Returns True if user has permission to edit the object"""
    if hasattr(obj, 'user') and obj.user == user:
        return True
    ct = ContentType.objects.get_for_model(obj.__class__)
    try:
        perm = ObjectPermission.objects.get(user=user, content_type=ct,
            object_id=obj.pk)
    except ObjectPermission.DoesNotExist:
        return False
    if perm.edit:
        return True
    else:
        return False
    
def filter_user_objects(user, model):
    """Returns all objects accessible to the user"""
    owned = model.objects.filter(user=user)
    pks = [obj.pk for obj in owned]
    ct = ContentType.objects.get_for_model(model)
    access = ObjectPermission.objects.filter(content_type=ct, user=user)
    for obj in access:
        if obj.content_object.pk not in pks:
            pks.append(obj.content_object.pk)
    return model.objects.filter(pk__in=pks)
    
def grant_access(obj, user):
    if hasattr(obj, 'user') and obj.user == user:
        return
    created = False
    ct = ContentType.objects.get_for_model(obj.__class__)
    try:
        perm = ObjectPermission.objects.get(user=user, content_type=ct,
            object_id=obj.pk)
    except ObjectPermission.DoesNotExist:
        perm = ObjectPermission(user=user, content_object=obj)
        perm.save()
        created = True
    return perm, created

def revoke_access(obj, user):
    ct = ContentType.objects.get_for_model(obj.__class__)
    try:
        perm = ObjectPermission.objects.get(user=user, content_type=ct,
            object_id=obj.pk)
    except ObjectPermission.DoesNotExist:
        return
    perm.delete()
    
def _set_edit(obj, user, edit):
    ct = ContentType.objects.get_for_model(obj.__class__)
    perm = ObjectPermission.objects.get(user=user, content_type=ct,
        object_id=obj.pk)
    perm.edit = edit
    perm.save()
    
def grant_edit(obj, user):
    _set_edit(obj, user, True)
    
def revoke_edit(obj, user):
    _set_edit(obj, user, False)
    
def get_object_or_forbidden(model, object_id, user):
    obj = model.objects.get(pk=object_id)
    
    if hasattr(obj, 'user') and obj.user == user:
        return obj, True
    
    if user_has_access(obj, user):
        return obj, user_can_edit(obj, user)
    
    raise Http404()