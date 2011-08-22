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

from django.contrib.auth.models import User
from django.test import TestCase

from netadmin.networks.models import Host
from utils import user_has_access, grant_access, revoke_access, \
    user_can_edit, grant_edit, revoke_edit


class PermissionsTest(TestCase):
    """Tests for permissions
    """
    
    def setUp(self):
        self.user_a = User.objects.create_user('user_a', 'user_a@something.com', 'userpassword')
        self.user_a.save()
        
        self.user_b = User.objects.create_user('user_b', 'user_b@something.com', 'userpassword')
        self.user_b.save()
        
        self.host = Host(name='Host', ipv4='1.2.3.4', user=self.user_a)
        self.host.save()
        
    def test_user_access(self):
        access = user_has_access(self.host, self.user_a)
        self.assertEqual(access, True)
        
        access = user_has_access(self.host, self.user_b)
        self.assertEqual(access, False)
        
    def test_grant_access(self):
        access = user_has_access(self.host, self.user_b)
        self.assertEqual(access, False)
        
        grant_access(self.host, self.user_b)
        access = user_has_access(self.host, self.user_b)
        self.assertEqual(access, True)
        
    def test_revoke_access(self):
        grant_access(self.host, self.user_b)
        access = user_has_access(self.host, self.user_b)
        self.assertEqual(access, True)
        
        revoke_access(self.host, self.user_b)
        access = user_has_access(self.host, self.user_b)
        self.assertEqual(access, False)
        
    def test_can_edit(self):
        edit = user_can_edit(self.host, self.user_a)
        self.assertEqual(edit, True)
        
        revoke_access(self.host, self.user_b)
        edit = user_can_edit(self.host, self.user_b)
        self.assertEqual(edit, False)
        
        grant_access(self.host, self.user_b)
        edit = user_can_edit(self.host, self.user_b)
        self.assertEqual(edit, True)
        
    def test_revoke_edit(self):
        grant_access(self.host, self.user_b)
        edit = user_can_edit(self.host, self.user_b)
        self.assertEqual(edit, True)
        
        revoke_edit(self.host, self.user_b)
        edit = user_can_edit(self.host, self.user_b)
        self.assertEqual(edit, False)
        
        revoke_access(self.host, self.user_b)
        
    def test_grant_edit(self):
        grant_access(self.host, self.user_b)
        edit = user_can_edit(self.host, self.user_b)
        self.assertEqual(edit, True)
        
        revoke_edit(self.host, self.user_b)
        edit = user_can_edit(self.host, self.user_b)
        self.assertEqual(edit, False)
        
        grant_edit(self.host, self.user_b)
        edit = user_can_edit(self.host, self.user_b)
        self.assertEqual(edit, True)
