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
        """
        The unset_option() function should remove all definitions of an option
        """
        def check_option(user=None):
            CustomOption.objects.get(name='opt', value='val', user=user)

        set_option('opt', 'val')
        unset_option('opt')
        self.assertRaises(CustomOption.DoesNotExist, check_option)

        set_option('opt', 'val', self.user)
        unset_option('opt', self.user)
        self.assertRaises(CustomOption.DoesNotExist, check_option)
        
    def test_user_option(self):
        """
        Setting and getting USER options should be done with
        set_user_option() and get_user_option() functions
        """
        set_user_option('opt', 'val', self.user)
        value = get_user_option('opt', self.user)
        self.assertEqual(value, 'val')
        
    def test_global_option(self):
        """
        Setting and getting GLOBAL options should be done with
        set_global_option() and get_global_option() functions
        """
        set_global_option('opt', 'val')
        value = get_global_option('opt')
        self.assertEqual(value, 'val')
        
    def test_reset_option(self):
        """
        The reset_option() function should remove all previous definitions
        of an option and reset its value
        """
        set_option('opt', 'val')
        reset_option('opt', 'new_val')
        value = get_option('opt', 'wrong value')
        self.assertEqual(value, 'new_val')
        
        set_option('opt', 'val', self.user)
        reset_option('opt', 'new_val', self.user)
        value = get_option('opt', 'wrong value', user=self.user)
        self.assertEqual(value, 'new_val')
        
    def test_default_value(self):
        """
        The second parameter of get_option() function is a default value for
        an option and it should be used in case of getting option that hasn't
        been set yet
        """
        value = get_option('opt', 'val')
        self.assertEqual(value, 'val')
        option = CustomOption.objects.get(name='opt')
        self.assertEqual(option.value, 'val')
        
        value = get_option('opt', 'val', self.user)
        self.assertEqual(value, 'val')
        option = CustomOption.objects.get(name='opt', user=self.user)
        self.assertEqual(option.value, 'val')
