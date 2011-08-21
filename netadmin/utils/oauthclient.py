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

import cgi
try:
    import json
except ImportError:
    import simplejson as json
import oauth2 as oauth


API_URL = ""

REQUEST_TOKEN_URL = '%s/oauth/request_token/' % API_URL
ACCESS_TOKEN_URL = '%s/oauth/access_token/' % API_URL
AUTHORIZE_URL = '%s/oauth/authorize/' % API_URL


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
    
    def fetch_resource(self, resource_url, method='GET', access_token=None):
        if access_token:
            self.access_token = access_token
        token = oauth.Token(self.access_token['oauth_token'],
                            self.access_token['oauth_token_secret'])
        token.set_verifier(self.verifier)
        client = oauth.Client(self.consumer, token)
        response, content = client.request(resource_url, method)
        return response, content
    
    def fetch_json_resource(self, resource_url, method='GET'):
        content = self.fetch_resource(resource_url, method)[1]
        return json.loads(content)
    
    def get_hosts_list(self):
        return self.fetch_json_resource('%s/api/host/list/' % API_URL, 'GET')
    
    def get_host(self, host_id):
        return self.fetch_json_resource('%s/api/host/%s/' % (API_URL, str(host_id)), 'GET')
        
if __name__=='__main__':
    access_token = {'oauth_token_secret': 'j9XRFjGJVe6PebWe3uqHMR9s8XQpW9G5',
                    'oauth_token': 'a7zQ4QNbamqDVdPGdZ'}
    client = NetadminOAuthClient('1234', 'abcd', access_token=access_token)
    import pprint
    hosts = client.get_hosts_list()
    for host in hosts['hosts']:
        id = host['id']
        data = client.get_host(id)
        print data['host_name'], data['ipv4'], data['ipv6']