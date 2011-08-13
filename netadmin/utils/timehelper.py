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
"""
This module provides a few utility functions for managing time
"""
import datetime
from datetime import timedelta


DELTA_DAY = timedelta(days=1)
DELTA_HOUR = timedelta(hours=1)
DELTA_MINUTE = timedelta(minutes=1)


def datetime_iterator(date_from, date_to, delta):
    """Generates range of dates
    """
    if date_from <= date_to:
        while date_from <= date_to:
            yield date_from
            date_from += delta

def date_iterator(date_from, date_to=datetime.date.today(), delta=DELTA_DAY):
    return datetime_iterator(date_from, date_to, delta)
        
def time_iterator(time_from, time_to=datetime.datetime.now(), delta=DELTA_HOUR):
    return datetime_iterator(date_from, date_to, delta)
    