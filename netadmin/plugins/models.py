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

from django.contrib.auth.models import User
from django.db import models


class PluginSettings(models.Model):
    plugin_name = models.CharField(max_length=30, editable=False)
    is_active = models.BooleanField(default=False)
    
    def __unicode__(self):
        return "Plugin '%s' settings" % self.plugin_name
    
class CustomOption(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=300)
    
    def __unicode__(self):
        return "'%s'='%s'" % (self.name, self.value)

class Dashboard(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return "'%s' owned by user %s" % \
            (self.name, self.user.username)
            
    def num_widgets(self, column):
        """Returns number of widgets in a column on dashboard
        """
        widgets = self.widgetsettings_set.all()
        if widgets:
            return widgets.filter(column=column).count()
        return 0
    
    def recalculate_order(self):
        widgets = self.widgetsettings_set.all().order_by('column')
        column = 1
        order = 1
        for widget in widgets:
            if widget.column != column:
                column = widget.column
                order = 1
            widget.order = order
            widget.save()
            order += 1
            
    def insert_widget(self, widget, column):
        """Inserts widget into column
        """
        widget_class = widget.__class__.__name__
        order = self.num_widgets(column) + 1
        widget = WidgetSettings(dashboard=self, column=column,
                                order=order, widget_class=widget_class)
        widget.save()
        return widget

class WidgetSettings(models.Model):
    dashboard = models.ForeignKey(Dashboard)
    column = models.SmallIntegerField()
    order = models.SmallIntegerField()
    widget_class = models.CharField(max_length=30)
    
    def __unicode__(self):
        return "on dashboard '%s'" % self.dashboard.name
    
    def save(self):
        if not self.pk:
            self.order = self.dashboard.num_widgets(self.column) + 1
        super(WidgetSettings, self).save() 
    
    def get_widget(self):
        from netadmin.plugins.core import load_plugins
        plugins = load_plugins()
        for plugin in plugins:
            widgets = plugin().widgets()
            for widget in widgets:
                if widget.__name__ == self.widget_class:
                    return widget
        return None
