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

from core import load_plugins, widgets_list
from forms import PluginSettingsFormset, WidgetCreateForm
from models import PluginSettings, WidgetsArea, WidgetSettings


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
def widgets_settings(request, widget_remove=None,
                     widget_up=None, widget_down=None):
    if request.method == "GET":
        if widget_remove:
            widget_settings = WidgetSettings.objects.get(pk=widget_remove)
            if widget_settings.widgets_area.user == request.user:
                widget_settings.delete()
                widget_settings.widgets_area.recalculate_order()
        if widget_up or widget_down:
            widget_pk = widget_up or widget_down
            widget = WidgetSettings.objects.get(pk=widget_pk)
            area = widget.widgets_area
            if widget_up:
                area.widget_up(widget)
            else:
                area.widget_down(widget)
    
    if request.method == "POST":
        widget_form = WidgetCreateForm(request.user, request.POST)
        widget_form.save()
        
    if widgets_list():
        widget_form = WidgetCreateForm(user=request.user)
    else:
        widget_form = None
    
    context = {
        'widgets_areas': WidgetsArea.objects.filter(user=request.user),
        'widget_form': widget_form
    }
    return direct_to_template(request, "plugins/widgets_settings.html",
                              extra_context=context)
    