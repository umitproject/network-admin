#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author: Amit Pal <amix.pal@gmail.com>
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
# Dictionary will be send out containing

import datetime
from datetime import timedelta

from django.utils.translation import ugettext as _

from netadmin.plugins import Plugin, Widget
from netadmin.plugins.options import get_option
from netadmin.shortcuts import get_host, get_hosts, get_alerts, get_events, \
    get_networks, get_network
from netadmin.utils.charts import ColumnChart, NumberColumn, DateColumn
from netadmin.utils.timehelper import date_iterator
import csv

class TraceRoute(Plugin):
	name = "Web Trace Route"
	description = "Basic Information Show On Map"
	
	
	def widgets(self):
		return [TraceRouteWidget]
    
__plugins__ = [TraceRoute]

class TraceRouteWidget(Widget):
	name = "Trace Route Widget"
	description = "Basic Information Show On Map"
	template_name = "map.html"
	
	def get_title(self):
		return "Trace Route"

	def context(self, widget):
		user = widget.widgets_area.user
		#hosts = get_hosts(user=user)
		geoIP = []
		geo_final = []
		for host in get_hosts(user=user):
		 geo_range = self.range_check(host.ipv4)
		 if geo_range:
			geoIP.append( '%s' % (geo_range[0][0]) )
		if geoIP:
			geo_LatLng = self.get_LatLng(geoIP)
		if geo_LatLng:
			for i in range(0,len(geo_LatLng)):
				geo_final.append( '[%s,%s], ' % (geo_LatLng[i][0], geo_LatLng[i][1]))
		return {
		'geoIP': geo_final[:10]
		}

	def range_check(self, the_ip):
		rowx = []
		#print the_ip
		with open('/home/lovestone/Desktop/network-admin/installed_plugins/trace_route/GeoIPCountryWhois.csv', mode='r') as f:
			for num,row in enumerate(csv.reader(f)):
				if row[0] <= the_ip <= row[1]:
					rowx.append([row[4]])
					return rowx
				else:
					continue       
		return rowx
	
	def get_LatLng(self, the_country):
		rowy = []
		#print the_country
		for x in range(0,len(the_country)):
			with open('/home/lovestone/Desktop/network-admin/installed_plugins/trace_route/GeoLiteCity-Location.csv', mode='r') as d:
				for num,row in enumerate(csv.reader(d)):
					if row[1]== the_country[x].strip():
						rowy.append([row[5],row[6]])
		return rowy
					
    
