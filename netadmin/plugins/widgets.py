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

from netadmin.plugins.utils import get_user_objects

class UnknownWidgetName(Exception):
    """Raised when widget's author didn't override name field
    """
    pass

class DefaultValueNotFound(Exception):
    pass


class Widget(object):
    """
    Base widget class which contains all data and methods essential
    to render widget and manage its settings.
    
    To create your own widget you have to write Widget subclass which
    should override the following fields:
    
        * name - "official" name that is shown in dashboard settings
        * description - short text that should describe widget's purpose and its usage
        * template_name - name of the template file used to render the widget
          (the template itself should be placed in templates/widgets/ directory)
          
    Although only name and template_name fields are obligatory, we encourage
    you to provide users with comprehensive description so they can understand
    better how to use your widget.
    """
    name = ""
    description = ""
    
    template_name = ""
    user = ""
    user_list = []
    username = []
    
    def __init__(self, user=None):
        self._user = user
    
    def get_name(self):
        """Returns widget's "official" name
        """
        if not self.name:
            class_name = self.__class__.__name__
            raise UnknownWidgetName(_("You have to override 'name' field in "
                                      "the %s class") % class_name)
        return self.name
    
    def get_title(self):
        return self.get_name()
    
    def context(self, widget):
        """
        Should return context dictionary that will be used to render
        the widget.
        """
        return {}
    
    def options(self, widget):
        """
        Should return options dictionary, where each key indicates option's
        name and each value is a dictionary with the following keys:
        
            * label - string that will be displayed in option's form
            * type (optional, if 'choices' field is provided) - type of the
              option's value
            * choices (optional, if 'type' field is provided) - list of
              two-elements tuples where the first element is exact value to be
              stored and the second one is a label shown in the option's form
            * default - option's default value
            * return_func - function which gets one argument - value of the
              option from the database - and should return value that will
              be returned by get_option method (NOT plugins.options.get_option function!)
        """
        return {}
		
    def get_option(self, name, widget):
        """
        Returns value of the option with specified name or returns result
        of the return_func function declared for widget's option with this name.
        """
        from options import get_option
        self.user = get_user_objects(None,widget)
        if self.username:
			for user in self.username:
				user_name = get_user_objects(user, widget)
				self.user_list.append(user_name)
        
        option = self.options(widget).get(name)
        
        if option:
            if not option.has_key('default'):
                raise DefaultValueNotFound(_("Default value for option '%s' "
                                             "has not been provided") % name)
            value = get_option(name, option.get('default'))
            return_func = option.get('return_func')
            if return_func:
                return return_func(value)
        else:
            value = get_option(name, '')
        return value
