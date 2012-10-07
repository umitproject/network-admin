#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Adriano Monteiro Marques
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
import os

DEBUG = True

# By default Django disables debug mode when running test. However in webapi
# tests we need to know if DEBUG was set to True, otherwise testing this
# application would be difficult.
API_TEST_DEBUG = True if DEBUG else False

if DEBUG:
    STATICFILES_DIRS = (
        os.path.join(os.path.dirname(__file__), 'static'),
    )
else:
    STATIC_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '%sadmin/' % STATIC_URL

SECRET_KEY = '=r-$b*8hglm+858&9t043hlm6-&6-3d3vfc4((7yd0dbrakhvi'

AUTH_PROFILE_MODULE = 'users.UserProfile'

SITE_ID = 1
SITE_DOMAIN = 'example.com'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_L10N = True

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'piston',
    'haystack',
    'djcelery'
)

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"

if DEBUG:
    INSTALLED_APPS += ('django.contrib.staticfiles',)

NETADMIN_APPS = (
    'netadmin',
    'netadmin.reportmeta',
    'netadmin.webapi',
    'netadmin.networks',
    'netadmin.events',
    'netadmin.users',
    'netadmin.permissions',
    'netadmin.notifier',
    'netadmin.utils.charts',
    'netadmin.plugins',
    'netadmin.analytics'
)

INSTALLED_APPS += NETADMIN_APPS
SITE_DOMAIN = 'example.com'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
)

PROJECT_ROOT = os.path.dirname(__file__)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)
ROOT_URLCONF = 'urls'
LOGIN_URL = '/login/'

ACTIVATION_FROM_EMAIL = 'your_email@example.com'

HAYSTACK_SITECONF = 'search_indexes'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(os.path.dirname(__file__), 'whoosh_index')

import djcelery
djcelery.setup_loader()

try:
    from local_settings import *
except ImportError:
    pass
