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

from django.utils.translation import ugettext as _

from models import CustomOption


class UnknownOption(Exception):
    """Raised when option with given name is not defined
    """
    pass

class OptionDuplicated(Exception):
    """Raised when option with given name was defined more than once
    """
    pass


def set_options(name, value):
    """Sets value of an option
    """
    option, created = CustomOption.objects.get_or_create(name=name)
    option.value = str(value)
    option.save()
    return option

def reset_option(name, value):
    """
    Removes all definitions of an option and sets its value once again.
    
    Use this function in case of OptionDuplicated error.
    """
    CustomOption.objects.filter(name=name).delete()
    option = CustomOption(name=name, value=value)
    option.save()
    return option

def get_option(name):
    """Returns value of an option
    """
    try:
        option = CustomOption.objects.get(name=name)
    except CustomOption.DoesNotExist:
        raise UnknownOption(_("Requested option '%s' does not exist") % name)
    except CustomOption.MultipleObjectsReturned:
        raise OptionDuplicated(_("There are more than one option objects. "
                                 "You can fix this problem by using "
                                 "'reset_option' function."))
    return option.value
