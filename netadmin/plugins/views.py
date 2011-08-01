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

from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from netadmin.plugins.core import load_plugins
from netadmin.plugins.forms import PluginSettingsFormset
from netadmin.plugins.models import PluginSettings


@login_required
def plugins_settings(request):
    if not request.user.is_superuser:
        raise Exception
    
    plugins = load_plugins()
    names_list = [sett.plugin_name for sett in PluginSettings.objects.all()]
    
    for plugin in plugins:
        meta = plugin().plugin_meta()
        if meta['name'] not in names_list:
            sett = PluginSettings(plugin_name=meta['name'])
            sett.save()
            
    if request.method == "POST":
        formset = PluginSettingsFormset(request.POST)
        if formset.is_valid():
            settings = formset.save()
    else:
        formset = PluginSettingsFormset()
    
    return direct_to_template(request, "plugins/settings.html",
                              extra_context={"settings_formset": formset})