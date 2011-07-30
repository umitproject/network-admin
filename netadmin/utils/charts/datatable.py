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


class ChartColumn(object):
    
    _type_name = ''
    
    def __init__(self, label='', data=[], get_data=None):
        self._label = label
        self._data = data
        self.get_data = get_data
        
    def __iter__(self):
        for element in self._data:
            yield element
            
    def __len__(self):
        return len(self._data)
            
    def _format(self, element):
        return element
    
    def data(self):
        for element in self._data:
            yield self._format(element)
    
    def set_label(self, label):
        self._label = label
        
    def column_type(self):
        return self._type_name
    
    def column_label(self):
        return self._label
        
class NumberColumn(ChartColumn):
    _type_name = 'number'
    
class StringColumn(ChartColumn):
    _type_name = 'string'
    
    def _format(self, element):
        return "'%s'" % element
    
class DateColumn(ChartColumn):
    _type_name = 'date'
    
    def _format(self, element):
        return 'new Date(%i, %i, %i)' % \
            (element.year, element.month, element.day)
            
class DatetimeColumn(ChartColumn):
    _type_name = 'datetime'
    
    def _format(self, element):
        return 'new Date(%i, %i, %i, %i, %i, %i)' % \
            (element.year, element.month, element.day,
             element.hour, element.minute, element.second)
