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

from django import forms
from django.utils.translation import ugettext as _

from models import CustomOption, CUSTOM_OPTION_MAX_LENGTH


class UnknownOption(Exception):
    """Raised when option with given name is not defined
    """
    pass

class OptionDuplicated(Exception):
    """Raised when option with given name was defined more than once
    """
    pass


def set_option(name, value, user=None):
    """Sets value of an option
    """
    option, created = CustomOption.objects.get_or_create(name=name, user=user)
    option.value = str(value)
    option.save()
    return option

def reset_option(name, value, user=None):
    """
    Removes all definitions of an option and sets its value once again.
    
    Use this function in case of OptionDuplicated error, e.g.
    
        # get value of a global option and make sure it's not duplicated
        try:
            value = get_option(option_name)
        except OptionDuplicated:
            reset_option(option_name, default_value)
            value = default_value
    """
    CustomOption.objects.filter(name=name, user=user).delete()
    option = CustomOption(name=name, value=value, user=user)
    option.save()
    return option

def unset_option(name, user=None):
    try:
        option = CustomOption(name=name, user=user)
    except CustomOption.DoesNotExist:
        return
    option.delete()

def get_option(name, default, user=None):
    """Returns value of an option
    """
    try:
        option = CustomOption.objects.get(name=name, user=user)
    except CustomOption.DoesNotExist:
        option = set_option(name, default, user)
    except CustomOption.MultipleObjectsReturned:
        raise OptionDuplicated(_("There are more than one option objects. "
                                 "You can fix this problem by using "
                                 "'reset_option' function."))
    return option.value

def get_user_option(name, user, default=None):
    return get_option(name, default, user)

def get_global_option(name, default=None):
    return get_option(name, default)

def set_user_option(name, value, user):
    return set_option(name, value, user)

def set_global_option(name, value):
    return set_option(name, value)

def get_options(list_of_names, list_of_defaults=None, user=None):
    """Returns dictionary with values for all options from the list of names
    """
    values = {}
    if not list_of_defaults:
        list_of_defaults = [None for e in list_of_names]
    for name, default in zip(list_of_names, list_of_defaults):
        values[name] = get_option(name, default, user)
    return values

def options_form(options_dict):
    """
    Returns form class generated based on options dictionary
    of plugin or widget.
    """
    class OptionsForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super(OptionsForm, self).__init__(*args, **kwargs)
            
            for key in options_dict:
                option = options_dict[key]
                label = option.get('label', key)
                option_type = option.get('type')
                
                if option.get('choices'):
                    field = forms.ChoiceField(choices=option.get('choices'))
                elif option_type == 'integer':
                    field = forms.IntegerField()
                elif option_type == 'bool':
                    field = forms.BooleanField()
                else:
                    field = forms.CharField(max_length=CUSTOM_OPTION_MAX_LENGTH)
                    
                field.label = label   
                self.fields[key] = field
                
    return OptionsForm
