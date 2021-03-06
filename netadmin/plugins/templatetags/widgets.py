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

from django import template
from django.template.loader import get_template
from django.template import Context

from netadmin.plugins.models import WidgetsArea
from netadmin.plugins.forms import DashboardWidgetForm
from netadmin.plugins.models import WidgetSettings


register = template.Library()


@register.simple_tag
def render_widget(object_id):
    """Renders widget's template with context returned by context() method
    """
    widget_settings = WidgetSettings.objects.get(id = object_id)
    widget = widget_settings.get_widget()
    template_name = widget.template_name
    context = widget.context(widget=widget_settings)
    t =  get_template("widgets/%s" % template_name)
    return t.render(Context(context))

@register.inclusion_tag("plugins/widgets_area.html")
def widgets_area(user, name, num_columns):
    """Renders area with all widgets assigned to it 
    """
    area, created = WidgetsArea.objects.get_or_create(name=name, user=user)
    if created:
        area.num_columns = num_columns
        area.save()
    context = {
        "widgets_area": area,
        "dashboard_form": DashboardWidgetForm(initial={'widgets_area': area, 'order': 1, 'column': 1})
    }
    return context
