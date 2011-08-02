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
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template

from netadmin.plugins.core import load_plugins
from netadmin.plugins.forms import PluginSettingsFormset, WidgetCreateForm
from netadmin.plugins.models import PluginSettings, Dashboard, WidgetSettings


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
    
@login_required
def dashboard_settings(request, widget_remove=None):
    if not request.user.is_superuser:
        raise Exception
    
    dashboard, created = Dashboard.objects.get_or_create(user=request.user,
                                                         name=_("Dashboard"))
    
    if request.method == "GET" and widget_remove:
        widget_settings = WidgetSettings.objects.get(pk=widget_remove)
        if widget_settings.dashboard != dashboard:
            raise Exception
        widget_settings.delete()
        widget_settings.dashboard.recalculate_order()
    
    if request.method == "POST":
        widget_form = WidgetCreateForm(request.POST)
        widget_form.save()
    
    widgets_settings = dashboard.widgetsettings_set.all().order_by('column','order')
    context = {
        'dashboard': dashboard,
        'widgets_settings': widgets_settings,
        'widget_form': WidgetCreateForm(initial={'dashboard': dashboard})
    }
    return direct_to_template(request, "plugins/dashboard_settings.html",
                              extra_context=context)
    