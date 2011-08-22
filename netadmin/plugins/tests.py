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

import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from models import CustomOption
from options import set_option, reset_option, get_option, unset_option, \
    set_user_option, set_global_option, get_user_option, get_global_option

class OptionsTest(TestCase):
    """Tests for options
    """
    
    def setUp(self):
        self.user = User.objects.create_user('user', 'user@something.com',
            'userpassword')
        self.user.save()
        
    def test_unset_option(self):
        option = CustomOption(name='opt', value='val')
        option.save()
        unset_option('opt')
        try:
            option = CustomOption.objects.get(name='opt', value='val')
        except CustomOption.DoesNotExist:
            option = None
        self.assertEqual(option, None)
        
        option = CustomOption(name='opt', value='val', user=self.user)
        option.save()
        unset_option('opt', self.user)
        try:
            option = CustomOption.objects.get(name='opt', value='val',
                user=self.user)
        except CustomOption.DoesNotExist:
            option = None
        self.assertEqual(option, None)
        
    def test_set_option(self):
        set_option('opt', 'val')
        option = CustomOption.objects.get(name='opt', value='val')
        option.delete()
        
        set_global_option('opt', 'val')
        option = CustomOption.objects.get(name='opt', value='val')
        option.delete()
        
    def test_set_user_option(self):
        set_option('opt', 'val', self.user)
        option = CustomOption.objects.get(name='opt', value='val',
            user=self.user)
        option.delete()
        
        set_user_option('opt', 'val', self.user)
        option = CustomOption.objects.get(name='opt', value='val',
            user=self.user)
        option.delete()
        
    def test_set_and_get_option(self):
        set_option('opt', 'val')
        value = get_option('opt', 'wrong value')
        self.assertEqual(value, 'val')
        unset_option('opt')
        
    def test_user_option(self):
        set_user_option('opt', 'val', self.user)
        value = get_user_option('opt', self.user)
        self.assertEqual(value, 'val')
        
    def test_global_option(self):
        set_global_option('opt', 'val')
        value = get_global_option('opt')
        self.assertEqual(value, 'val')
        
    def test_reset_option(self):
        set_option('opt', 'val')
        reset_option('opt', 'new_val')
        value = get_option('opt', 'wrong value')
        self.assertEqual(value, 'new_val')
        
        set_option('opt', 'val', self.user)
        reset_option('opt', 'new_val', self.user)
        value = get_option('opt', 'wrong value', user=self.user)
        self.assertEqual(value, 'new_val')
        
    def test_default_value(self):
        value = get_option('opt', 'val')
        self.assertEqual(value, 'val')
        option = CustomOption.objects.get(name='opt')
        self.assertEqual(option.value, 'val')
        
        value = get_option('opt', 'val', self.user)
        self.assertEqual(value, 'val')
        option = CustomOption.objects.get(name='opt', user=self.user)
        self.assertEqual(option.value, 'val')
