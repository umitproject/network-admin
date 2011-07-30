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

import re

from django.utils.translation import ugettext as _

from netadmin.utils.charts.datatable import ChartColumn


GOOGLE_CHARTS_PACKAGES = ['corechart', 'gauge', 'geochart', 'table', 'treemap']

WIDTH_DEFAULT = 700
HEIGHT_DEFAULT = 400


class InvalidChartsPackage(Exception):
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
    width = 700
    height= 400
    
    def __init__(self, queryset):
        if getattr(self, 'chart_type') == 'Chart':
            raise ChartTypeNotDefined(_("You cannot use Chart class directly. "
                                        "Instead you should use class that "
                                        "inherit from Chart.")) 
        self._queryset = queryset
        self._get_data()
        
    def __iter__(self):
        """Iterates over each column
        """
        cols = [getattr(self, col_name) for col_name in self._columns]
        cols += self._get_yield_columns()
        for col in cols:
            yield col
            
    def __hash__(self):
        return hash(self._queryset) + hash(self.__class__)
    
    def __len__(self):
        """Returns number of rows in chart
        """
        if not self._columns:
            return 0
        first_column = getattr(self, self._columns[0])
        return len(first_column)
            
    def _get_yield_columns(self):
        yield_func_re = re.compile(r'^columns_.*$')
        cols = []
        for attr in vars(self.__class__):
            if yield_func_re.match(attr):
                yield_func = getattr(self, attr)
                for col in yield_func(self._queryset):
                    cols.append(col)
        return cols
        
    def _get_columns(self):
        """Returns list of names of all columns in chart
        """
        if hasattr(self, 'order'):
            cols = getattr(self, 'order')
        else:
            cols = vars(self.__class__)
        return [col for col in cols if isinstance(getattr(self, col), ChartColumn)]
    _columns = property(_get_columns)
    
    def _get_data(self):
        """Updates data for all columns in chart
        """
        queryset = self._queryset
        for column_name in self._columns:
            column = getattr(self, column_name)
            if column._data:
                continue
            if column.get_data:
                data = [column.get_data(element) for element in queryset]
            elif hasattr(self, 'get_%s_data' % column_name):
                get_data_func = getattr(self, 'get_%s_data' % column_name)
                data = get_data_func(queryset)
            else:
                data = [getattr(element, column_name) for element in queryset]
            column._data = data
    
    def get_col_label(self, col_name):
        for col in self._columns:
            if col == col_name:
                if col._label:
                    return col._label
                else:
                    return col_name.capitalize()
        return col_name.capitalize()
    
    def chart_type(self):
        return self.__class__.__name__
    
class LineChart(Chart):
    chart_type = 'LineChart'
    
class ColumnChart(Chart):
    chart_type = 'ColumnChart'
    
class ScatterChart(Chart):
    chart_type = 'ScatterChart'
    
class AnnotatedTimeLine(Chart):
    chart_type = 'AnnotatedTimeLine'
    
class PieChart(Chart):
    chart_type = 'PieChart'