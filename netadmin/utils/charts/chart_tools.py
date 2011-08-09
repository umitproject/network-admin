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

from core import Chart


CHART_TOOLS_PACKAGES = ['corechart', 'gauge', 'geochart', 'table', \
                        'treemap', 'annotatedtimeline']


class InvalidChartsPackage(Exception):
    pass


class ChartColumn(object):
    
    _type_name = ''
        
    @staticmethod    
    def format(value):
        return value
        
    def column_type(self):
        return self._type_name
        
class NumberColumn(ChartColumn):
    _type_name = 'number'
    
class StringColumn(ChartColumn):
    _type_name = 'string'
    
    @staticmethod
    def format(value):
        return "'%s'" % value
    
class DateColumn(ChartColumn):
    _type_name = 'date'
    
    @staticmethod
    def format(value):
        return 'new Date(%i, %i, %i)' % \
            (value.year, value.month, value.day)
            
class DatetimeColumn(ChartColumn):
    _type_name = 'datetime'
    
    @staticmethod
    def format(value):
        return 'new Date(%i, %i, %i, %i, %i, %i)' % \
            (value.year, value.month, value.day,
             value.hour, value.minute, value.second)

class ChartToolsChart(Chart):
    def formatted_data(self):
        x_col_class = self.x['type']
        y_col_class = self.y['type']
        
        x = [x_col_class.format(val) for val in self.raw_data['x']]
        y = [[y_col_class.format(val) for val in it] for it in self.raw_data['y']]
        
        return dict(zip(x, zip(*y)))
        
    def num_rows(self):
        return len(self.raw_data['x'])
    
    def columns(self):
        x_col_class = self.x['type']
        y_col_class = self.y['type']
        
        x_name = self.x['label']
        x_type = x_col_class().column_type()
        
        y_name = self.y['label']
        y_type = y_col_class().column_type()
        
        cols = [{'name': x_name, 'type': x_type}]
        for i in xrange(0, len(self.raw_data['y'])):
            cols.append({'name': y_name, 'type': y_type})
        return cols

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