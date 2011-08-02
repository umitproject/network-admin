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

import netadmin.plugins.installed as installed_plugins
from netadmin.plugins.models import PluginSettings


__plugins__ = []


def load_plugins(active=False):
    """Returns list of all installed plugins
    """
    global __plugins__
    if __plugins__:
        __plugins__ = []
    plugins_path = os.path.dirname(installed_plugins.__file__)
    iter_modules = pkgutil.iter_modules([plugins_path])
    plugins_modules = [name for loader, name, ispkg in iter_modules]
    for plugin_module in plugins_modules:
        mod = __import__('netadmin.plugins.installed.%s.main' % plugin_module,
                         fromlist=['__plugins__'])
        __plugins__.extend(mod.__plugins__)
    plugins = __plugins__
    if active:
        settings = PluginSettings.objects.all()
        for sett in settings:
            if not sett.is_active:
                for plugin in plugins:
                    if plugin().plugin_meta()['name'] == sett.plugin_name:
                        plugins.remove(plugin)
    return plugins

class Plugin(object):
    
    _name = ''
    _description = _("Description not available")
    _author = _("Anonymous")
    _license = _("Unknown")
    
    def plugin_meta(self):
        meta = {
            'name': self._name if self._name else self.__class__.__name__,
            'description': self._description,
            'author': self._author,
            'license': self._license
        }
        return meta
    
    def activate(self):
        """Called when plugin is activated
        """
        pass
    
    def deactivate(self):
        """Called when plugin is deactivated
        """
        pass
    
    def actions(self):
        """Should return list of tuples: (action_name, callback_function)
        """
        return []
    
    def widgets(self):
        """Should return list of widgets
        """
        return []
