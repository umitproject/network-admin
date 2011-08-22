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

try:
    import json
except ImportError:
    import simplejson as json
import oauth2 as oauth

import cgi
import urllib
import time


API_URL = ""

REQUEST_TOKEN_URL = '%s/oauth/request_token/' % API_URL
ACCESS_TOKEN_URL = '%s/oauth/access_token/' % API_URL
AUTHORIZE_URL = '%s/oauth/authorize/' % API_URL


class NetadminClientError(Exception):
    pass

class OAuthError(Exception):
    pass

class NetadminOAuthClient(object):
    
    verifier = '1'
    
    def __init__(self, consumer_key, consumer_secret,
                 request_token_url=REQUEST_TOKEN_URL,
                 access_token_url=ACCESS_TOKEN_URL,
                 authorize_url=AUTHORIZE_URL,
                 access_token=None):
        self.request_token_url = request_token_url
        self.access_token_url = access_token_url
        self.authorize_url = authorize_url
        self.consumer = oauth.Consumer(consumer_key, consumer_secret)
        self.access_token = access_token
    
    def fetch_request_token(self):
        client = oauth.Client(self.consumer)
        resp, content = client.request(self.request_token_url, 'GET')
        self.request_token = dict(cgi.parse_qsl(content))
        return self.request_token
    
    def fetch_access_token(self, request_token=None):
        if request_token:
            self.request_token = request_token
        token = oauth.Token(self.request_token['oauth_token'],
                            self.request_token['oauth_token_secret'])
        token.set_verifier(self.verifier)
        client = oauth.Client(self.consumer, token)
        
        resp, content = client.request(self.access_token_url, 'POST')
        self.access_token = dict(cgi.parse_qsl(content))
        return self.access_token
    
    def fetch_resource(self, resource_url, method='GET', access_token=None,
                       body=''):
        if access_token:
            self.access_token = access_token
        token = oauth.Token(self.access_token['oauth_token'],
                            self.access_token['oauth_token_secret'])
        token.set_verifier(self.verifier)
        client = oauth.Client(self.consumer, token)
        
        body = urllib.urlencode(body)
        
        response, content = client.request(resource_url, method, body)
        return response, content
    
    def request(self, resource_url, method='GET', body=''):
        content = self.fetch_resource(resource_url, method, body=body)[1]
        return json.loads(content)
    
    def get(self, resource_url, body=''):
        return self.request(resource_url, 'GET', body)
    
    def post(self, resource_url, body=''):
        return self.request(resource_url, 'POST', body)
    
    def get_host_list(self):
        return self.get('%s/api/host/list/' % API_URL)
    
    def get_host(self, host_id):
        return self.get('%s/api/host/%s/' % (API_URL, str(host_id)))
    
    def get_network_list(self):
        return self.get('%s/api/network/list/' % API_URL)
    
    def get_network(self, net_id):
        return self.get('%s/api/network/%s/' % (API_URL, str(net_id)))
    
    def report_event(self, description, short_description, timestamp, protocol,
                     event_type, fields_class,
                     hostname='', host_ipv4='', host_ipv6='', *args, **kwargs):
        """
        Reports event
        
        Note: To send additional fields just pass them as named parameters
        """
        if not (hostname or host_ipv4 or host_ipv6):
            raise NetadminClientError(_("No host specified"))
        data = {
            'description': description,
            'short_description': short_description,
            'timestamp': timestamp,
            'protocol': protocol,
            'event_type': event_type,
            'fields_class': fields_class,
            'hostname': hostname,
            'source_host_ipv4': host_ipv4,
            'source_host_ipv6': host_ipv6
        }
        data.update(kwargs)
        return self.post('%s/api/event/report/' % API_URL, data)
