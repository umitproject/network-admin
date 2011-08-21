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
from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_detail

from netadmin.webapi.views import api_ok, api_error

from core import load_plugins, widgets_list
from forms import PluginSettingsFormset, WidgetCreateForm, DashboardWidgetForm
from models import PluginSettings, WidgetsArea, WidgetSettings
from options import options_form, set_option, get_options


@login_required
def plugins_settings(request):
    """Simple admin page for activating and deactivating installed plugins
    """
    if not request.user.is_superuser:
        raise Http404()
    
    plugins = load_plugins()
    names_list = [sett.plugin_name for sett in PluginSettings.objects.all()]
    
    for plugin in plugins:
        if plugin.name not in names_list:
            sett = PluginSettings(plugin_name=plugin.name)
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
    """Widgets areas' settings where user can insert widget and set its order
    """
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
            if area.user == request.user:
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
    
@login_required
def widget_detail(request, widgetsettings_id):
    """Widget details page where user can set options defined for the widget
    """
    widget = WidgetSettings.objects.get(pk=widgetsettings_id)
    opts = widget.get_widget().options(widget)
    
    if request.method == "POST":
        form = options_form(opts)(request.POST)
        if form.is_valid():
            for field in form.cleaned_data:
                set_option(field, form.cleaned_data[field])
    
    if opts:
        defaults = [opt.get('default') for opt in opts.values()]
        initial = get_options(opts.keys(), defaults)
        form = options_form(opts)(initial=initial)
    else:
        form = None
    
    extra_context = {
        'options_form': form 
    }
    queryset = WidgetSettings.objects.all()
    return object_detail(request, queryset, widgetsettings_id,
                         template_name="plugins/widget_detail.html",
                         extra_context=extra_context)

@login_required
def widgets_ajax(request):
    widget_id = request.GET.get('widget_id')
    if widget_id:
        if request.GET.get('column') and request.GET.get('order'):
            column, order = request.GET.get('column'), request.GET.get('order')
            widget = WidgetSettings.objects.get(pk=widget_id)
            changed = widget.move(order, column)
            if changed:
                widget.save()
                area  = widget.widgets_area
                area.recalculate_order()
                return api_ok(_("Widgets order changed"))
            return api_ok(_("Widgets stay in the same order"))
        
    if request.GET.get('delete'):
        widget_id = request.GET.get('delete')
        try:
            widget = WidgetSettings.objects.get(pk=widget_id)
        except WidgetSettings.DoesNotExist:
            return api_error(_("Widget does not exist"))
        widget.delete()
        return api_ok(_("Widget removed successfully"))
    
    if request.method == 'POST':
        dashboard_form = DashboardWidgetForm(request.POST)
        if dashboard_form.is_valid():
            dashboard_form.save()
            return api_ok(_("Widget added successfully"))
        return api_error(_("The form is invalid: %s") % dashboard_form.errors)
    
    return api_error(_("Unknown action"))