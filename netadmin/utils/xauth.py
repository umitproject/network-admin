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
    import simplejson as json
except ImportError:
    import json

import urllib
import oauth2 as oauth


class XAuthError(Exception):
    pass

class NetadminClientError(Exception):
    pass

class NetadminXAuthClient(object):
    access_token = None
    
    def __init__(self, consumer_key, consumer_secret, api_url):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.api_url = api_url

    def fetch_access_token(self, username, password):
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        client = oauth.Client(consumer)
        client.add_credentials(username, password)
        client.set_signature_method = oauth.SignatureMethod_HMAC_SHA1()
    
        x_auth_params = {
            'x_auth_username': username,
            'x_auth_password': password,
            'x_auth_mode': 'client_auth'
        }
    
        url = '%s/oauth/access_token/' % self.api_url
        body = urllib.urlencode(x_auth_params)
    
        response, content = client.request(url, method='POST', body=body)
    
        token = json.loads(content).get('message')
        try:
            token = (token['oauth_token'], token['oauth_token_secret'])
        except TypeError:
            raise XAuthError('Invalid credentials')
    
        return token
    
    def set_access_token(self, token):
        self.access_token = token
    
    def _get_resource(self, resource_url, method='GET', body='', as_json=True):
        if not self.access_token:
            raise XAuthError(_("Invalid access token"))
        token = self.access_token
        
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
    
        token = oauth.Token(*token)
        client = oauth.Client(consumer, token)
        
        url = '%s%s' % (self.api_url, resource_url)
        
        response, content = client.request(url, method, body=body)
        
        if as_json:
            return json.loads(content)
        
        return content
    
    def get(self, resource_url, body=''):
        return self._get_resource(resource_url, 'GET', body)
    
    def post(self, resource_url, body=''):
        return self._get_resource(resource_url, 'POST', body)
    
    def get_host_list(self):
        return self.get('/api/host/list/')
    
    def get_host(self, host_id):
        return self.get('/api/host/%s/' % str(host_id))
    
    def get_network_list(self):
        return self.get('/api/network/list/')
    
    def get_network(self, net_id):
        return self.get('/api/network/%s/' % str(net_id))
    
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
        return self.post('/api/event/report/', data)
