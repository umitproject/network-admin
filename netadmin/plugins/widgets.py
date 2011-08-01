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

from netadmin.plugins.models import WidgetSettings, Dashboard


def get_dashboard_order(column, dashboard):
    """Returns ordinal for a new widget in column on dashboard
    """
    widgets = WidgetSettings.objects.filter(dashboard=dashboard,
                                            column=column).order_by('-order')
    if not widgets:
        return 1
    return widgets[0].order + 1

def insert_widget(widget_class, dashboard_id, column):
    """Inserts new widget into dashboard
    """
    dashboard = Dashboard.objects.get(pk=dashboard_id)
    order = get_dashboard_order(column, dashboard)
    widget_settings = WidgetSettings(dashboard=dashboard, column=column,
                                     order=order, widget_class=widget_class)
    widget_settings.save()

class Widget(object):
    
    name = ""
    description = ""
    
    template_name = ""
    
    def context(self):
        return {}
