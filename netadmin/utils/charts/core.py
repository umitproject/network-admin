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


class ChartColumn(object):
    """
    """
    def __init__(self, name, data):
        self.name = name
        self.data = data
        
    def __len__(self):
        return len(self.data)

class Chart(object):
    """
    """
    def __init__(self, title, width=WIDTH_DEFAULT, height=HEIGHT_DEFAULT):
        self.title = title
        self.width, self.height = width, height
        self.columns = []
        
    def add_column(self, name, data):
        col = ChartColumn(name, data)
        self.columns.append(col)
        return col
    
    def get_column(self, name):
        for col in self.columns:
            if col.name == name:
                return col
        return None
    
    def data_iter(self):
        cols_data = [col.data for col in self.columns]
        for row in zip(*cols_data):
            yield row
