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


CUSTOM_OPTION_MAX_LENGTH = 300


class PluginSettings(models.Model):
    """
    """
    plugin_name = models.CharField(max_length=30, editable=False)
    is_active = models.BooleanField(default=False)
    
    def __unicode__(self):
        return "Plugin '%s' settings" % self.plugin_name
    
    def save(self, *args, **kwargs):
        """Calls plugin's activate or deactivate method after saving 
        """
        active = self.is_active
        super(PluginSettings, self).save(*args, **kwargs)
        if active != self.is_active:
            if self.is_active:
                self.get_plugin().activate()
            else:
                self.get_plugin().deactivate()
    
class CustomOption(models.Model):
    """
    The base model for custom options that could be used in plugin to
    save its state and/or user's preferences.
    
    The 'name' field must be unique in case of global option.
    Otherwise, if 'user' field is not blank 'name' have to be unique for the specified user.
    
    Regardless the type of saved value, it is converted and stored as a string.
    This is up to plugin's author to provide __str__ method for saved object
    and to convert option's value back to required type (if it cannot be string).
    """
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=CUSTOM_OPTION_MAX_LENGTH)
    user = models.ForeignKey(User, blank=True)
    
    def __unicode__(self):
        return "'%s'='%s'" % (self.name, self.value)
    
    def is_global(self):
        """Returns True if option is global, that is when user field is blank
        """
        if self.user:
            return False
        return True
    
class WidgetsArea(models.Model):
    """
    Widgets area is a set of widgets that has unique name. Every user has
    only one area with given name. Within area widgets should be ordered
    by columns and rows (respectively 'column' and 'order' fields in
    WidgetSettings model).
    """
    user = models.ForeignKey(User)
    name = models.CharField(max_length=30)
    num_columns = models.SmallIntegerField(choices=[(1,1), (2,2), (3,3)], default=1)
    
    def __unicode__(self):
        return "%s's '%s'" % (self.user.username, self.name)
    
    def widgets(self):
        """Returns WidgetSettings queryset
        """
        return self.widgetsettings_set.order_by('column', 'order')
            
    def num_widgets(self, column):
        """Returns number of widgets in a column on widgets area
        """
        widgets = self.widgetsettings_set.all()
        if widgets:
            return widgets.filter(column=column).count()
        return 0
    
    def recalculate_order(self):
        """
        Updates order for all widgets in the widgets area.
        
        Use this method to make sure that each widget has unique
        pair of column--order fields.
        """
        widgets = self.widgetsettings_set.all().order_by('column', 'order')
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
        if column < 1 or column > self.num_columns:
            raise IndexError(_("Column number out of range"))
        widget_class = widget.__class__.__name__
        order = self.num_widgets(column) + 1
        widget = WidgetSettings(widgets_area=self, column=column,
                                order=order, widget_class=widget_class)
        widget.save()
        return widget
    
    def _change_widget_order(self, widget, change):
        if widget.order + change < 1:
            return
        if widget.widgets_area != self:
            return
        col_widgets = self.widgetsettings_set.filter(column=widget.column)
        if widget not in col_widgets:
            return
        try:
            other_widget = col_widgets.get(order=widget.order+change)
        except WidgetSettings.DoesNotExist:
            return
        other_widget.order -= change 
        other_widget.save()
        widget.order += change
        widget.save()
        return widget
    
    def widget_up(self, widget):
        """Moves widget up (decrease its order)
        """
        return self._change_widget_order(widget, -1)
    
    def widget_down(self, widget):
        """Moves widget down (increase its order)
        """
        return self._change_widget_order(widget, 1)
    
    def columns(self):
        """
        Returns list of WidgetSettings querysets where each queryset
        contains widgets with a different column index
        """
        cols = []
        for i in xrange(1, self.num_columns + 1):
            widgets = self.widgetsettings_set.filter(column=i).order_by('order')
            cols.append(widgets)
        return cols

class WidgetSettings(models.Model):
    """
    Settings that specifies widget's position in selected area.
    The field 'widget_class' indicates Widget subclass defined in plugin.
    """
    widgets_area = models.ForeignKey(WidgetsArea)
    column = models.SmallIntegerField()
    order = models.SmallIntegerField()
    widget_class = models.CharField(max_length=30)
    
    def __unicode__(self):
        return "on widgets area '%s'" % self.widgets_area.name
    
    def save(self):
        """Sets widget's order on first save
        """
        if not self.pk:
            self.order = self.widgets_area.num_widgets(self.column) + 1
        super(WidgetSettings, self).save() 
    
    def get_widget(self):
        """
        Returns instance of Widget class which contains methods that give you
        access to widget's name, description, options, template context etc.
        """
        from netadmin.plugins.core import load_plugins
        plugins = load_plugins()
        for plugin in plugins:
            widgets = [widget() for widget in plugin.widgets()]
            for widget in widgets:
                if widget.__class__.__name__ == self.widget_class:
                    return widget
        return None
    
    def get_user(self):
        """Returns user--owner of the area to which widget is assigned
        """
        return self.widgets_area.user
    
    def set_user(self, user):
        """Sets user--owner of the area to which widget is assigned
        """
        area = self.widgets_area
        area.user = user
        area.save()
        
    user = property(get_user, set_user)
