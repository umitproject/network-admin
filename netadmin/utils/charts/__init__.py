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

from django.utils.translation import ugettext as _


def format_value(value, value_type):
    if value_type == 'number':
        return value
    if value_type == 'string':
        return '%s' % value
    if value_type == 'date':
        return 'new Date(%i, %i, %i)' % (value.year, value.month, value.day)
    if value_type == 'datetime':
        return 'new Date(%i, %i, %i, %i, %i, %i)' % \
            (value.year, value.month, value.day,
             value.hour, value.minute, value.second)
    return value

class ChartColumn(objects):
    
    data = []
    
    def __init__(self, label):
        self.label = label
        
    def __iter__(self):
        for element in data:
            yield self._format(element)
            
    def _format(self, element):
        return element
        
class NumberColumn(ChartColumn):
    type = 'number'
    
class StringColumn(ChartColumn):
    type = 'string'
    
    def _format(self, element):
        return str(element)
    
class DateColumn(ChartColumn):
    type = 'date'
    
    def _format(self, element):
        return 'new Date(%i, %i, %i)' % \
            (element.year, element.month, element.day)
            
class DatetimeColumn(ChartColumn):
    type = 'datetime'
    
    def _format(self, element):
        return 'new Date(%i, %i, %i, %i, %i, %i)' % \
            (element.year, element.month, element.day,
             element.hour, element.minute, element.second)

class ChartTypeNotDefined(Exception):
    pass

class Chart(object):
    """
    Base class for every type of chart.
    
    To display data from queryset you have to set up columns list where each
    column is defined as a dictionary with the following fields:
    
        * id - column identifier
        * label (optional) - column name that will be displayed on chart
        * field - name of model field which value will be displayed
        * type - type of data in the column
    """
    
    # basic chart settings
    title = ''
    width = 700
    height = 400
    
    # drop row if one of its values is None
    drop_if_none = False
    
    # chart data
    columns = []
    multicolumns = []
    
    def __init__(self, queryset):
        if not hasattr(self, 'chart_type'):
            raise ChartTypeNotDefined(_("You cannot use Chart class directly. "
                                        "Instead you should use class that "
                                        "inherit from Chart.")) 
        self.queryset = queryset
        self._update_labels()
        self._update_data()
        self._update_multicolumns()
        self._format_values()
        
    def _first_column(self):
        if self.columns:
            return self.columns[0]
        return None
    first_column = property(_first_column)
    
    def _format_values(self):
        for column in self.columns:
            column['data'] = [format_value(val, column['type']) for val in column['data']]
        
    def _update_column_field(self, field_name, default_func, *args, **kwargs):
        for column in self.columns:
            get_func_name = 'get_%s_%s' % (column['id'], field_name)
            if hasattr(self, get_func_name):
                column[field_name] = getattr(self, get_func_name)(*args, **kwargs)
            else:
                column[field_name] = default_func(column)
                
    def _update_multicolumns(self):
        for multicol in self.multicolumns:
            get_cols_func = 'get_%s_columns' % multicol
            if hasattr(self, get_cols_func):
                cols = getattr(self, get_cols_func)(self.queryset, self.first_column)
                c = []
                counter = 0
                for col in cols:
                    col['id'] = '%s%i' % (multicol, counter)
                    counter += 1
                    c.append(col)
                self.columns += c
        
    def _update_labels(self):
        self._update_column_field('label', lambda c: c['label'])
                
    def _update_data(self):
        self._update_column_field('data', lambda c: [],
                                  self.queryset, self.first_column)
        
        empty_columns = [col for col in self.columns if not col['data']]
        for column in empty_columns:
            if 'field' in column:
                data = []
                for element in self.queryset:
                    val = getattr(element, column['field'])
                    data.append(val)
                column['data'] = data
        
    def num_rows(self):
        return len(self.first_column['data'])
    
class LineChart(Chart):
    chart_type = 'LineChart'
    
class ColumnChart(Chart):
    chart_type = 'ColumnChart'
    
class ScatterChart(Chart):
    chart_type = 'ScatterChart'
    
class AnnotatedTimeLine(Chart):
    chart_type = 'AnnotatedTimeLine'