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

from core import Chart, ChartColumn


CHART_TOOLS_PACKAGES = ['corechart', 'gauge', 'geochart', 'table', \
                        'treemap', 'annotatedtimeline']


class InvalidChartsPackage(Exception):
    pass


class DatatableColumn(ChartColumn):
    """
    """
    type_name = ''
    
    def __init__(self, name, data):
        self.name = name
        self._data = data
    
    def format(self, value):
        return value
        
    def get_data(self):
        return [self.format(value) for value in self._data]
    
    data = property(get_data)
        
class NumberColumn(DatatableColumn):
    type_name = 'number'
    
class StringColumn(DatatableColumn):
    type_name = 'string'
    
    def format(self, value):
        return "'%s'" % value
    
class DateColumn(DatatableColumn):
    type_name = 'date'
    
    def format(self, value):
        return 'new Date(%i, %i, %i)' % \
            (value.year, value.month, value.day)
            
class DatetimeColumn(DatatableColumn):
    type_name = 'datetime'
    
    def format(self, value):
        return 'new Date(%i, %i, %i, %i, %i, %i)' % \
            (value.year, value.month, value.day,
             value.hour, value.minute, value.second)


class ChartToolsChart(Chart):
    """
    """
    chart_type = ''
    
    def add_column(self, name, data, column_class):
        col = column_class(name, data)
        self.columns.append(col)
        return col
    
    def num_rows(self):
        if self.columns:
            # we assume that all columns have the same length
            return len(self.columns[0])
        return 0

class LineChart(ChartToolsChart):
    chart_type = 'LineChart'
    
class ColumnChart(ChartToolsChart):
    chart_type = 'ColumnChart'
    
class ScatterChart(ChartToolsChart):
    chart_type = 'ScatterChart'
    
class AnnotatedTimeLine(ChartToolsChart):
    chart_type = 'AnnotatedTimeLine'
    
class PieChart(ChartToolsChart):
    chart_type = 'PieChart'