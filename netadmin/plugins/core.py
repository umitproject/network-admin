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

import os.path
import pkgutil

from django.utils.translation import ugettext as _

import installed_plugins
from models import PluginSettings


class PluginNameError(Exception):
    """Raised when plugin's name is not specified
    """
    pass

class Plugin(object):
    """Base class for plugins
    """
    name = ''
    description = _("Description not available")
    author = _("Anonymous")
    
    def get_name(self):
        if not self.name:
            raise PluginNameError(_("Plugin name not specified"))
        return self.name
    
    def activate(self):
        """Called when a plugin is activated
        """
        pass
    
    def deactivate(self):
        """Called when a plugin is deactivated
        """
        pass
    
    def actions(self):
        """
        Should return list of tuples: (action_name, callback_function)
        
        To read more about actions see: netadmin.plugins.actions
        """
        return []
    
    def widgets(self):
        """
        Should return list of widgets
        
        To read more about widgets see: netadmin.plugins.widgets
        """
        return []
    
    def options(self):
        """
        Should return options dictionary
        
        To read more about options see: netadmin.plugins.options
        """
        return {}
    
def load_plugins(user=None, active=False):
    """
    Returns list of all installed plugins. If 'active' is set to True, then
    only plugins activated by administrator are listed. 
    """
    plugins = []
    plugins_path = os.path.dirname(installed_plugins.__file__)
    iter_modules = pkgutil.iter_modules([plugins_path])
    plugins_modules = [name for loader, name, ispkg in iter_modules]
    for plugin_module in plugins_modules:
        mod = __import__('installed_plugins.%s.main' % plugin_module,
                         fromlist=['__plugins__'])
        if hasattr(mod, '__plugins__'):
            plugins.extend(mod.__plugins__)
    if active:
        settings = PluginSettings.objects.all()
        for sett in settings:
            if not sett.is_active:
                for plugin in plugins:
                    if plugin().name == sett.plugin_name:
                        plugins.remove(plugin)
    return [plugin(user) for plugin in plugins]

def widgets_list(user=None):
    """Returns list of all widgets defined in installed plugins
    """
    plugins = load_plugins(active=True)
    widgets = sum([plugin.widgets() for plugin in plugins], [])
    return [widget(user) for widget in widgets]
