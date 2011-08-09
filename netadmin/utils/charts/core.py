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

WIDTH_DEFAULT = 700
HEIGHT_DEFAULT = 400


class ChartAxisError(Exception):
    pass

class ChartData(dict):
    def x(self):
        return self.keys()
    
    def y(self):
        return self.values()

class Chart(object):
    raw_data = {'x': [], 'y': []}
    
    # metadata for X and Y axes
    x = {'label': 'x'}
    y = {'label': 'y'}
    
    def __init__(self, data_x, data_y, name='',
                 width=WIDTH_DEFAULT, height=WIDTH_DEFAULT):
        self.name = name
        self.width = width
        self.height = height
        
        try:
            iter(data_x)
        except TypeError:
            raise ChartAxisError(_("'data_x' must be iterable"))
        self.raw_data['x'] = self.map_x(data_x)
        
        try:
            y = [self.map_y(dataset, data_x) for dataset in data_y]
        except TypeError:
            raise ChartAxisError(_("'data_y' must be iterable"))
        self.raw_data['y'] = y
        
    def get_data(self):
        x = self.raw_data['x']
        y = zip(*self.raw_data['y'])
        return dict(zip(x, y))
    
    def map_x(self, data_x):
        """
        Should return list of values for the X axis.
        
        While overriding this method you can base your result on
        original values passed to the chart object as x_data argument.
        """
        return data_x
        
    def map_y(self, dataset, data_x):
        """
        Should return list of values for the Y axis.
        
        While overriding this method you can base your result on
        the following arguments:
            * iterable - element of the y_data list passed to the chart object
            * x_data - list of values for the X axis (after mapping!)
        """
        return dataset
