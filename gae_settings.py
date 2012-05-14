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


from djangoappengine.settings_base import *


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
SITE_DOMAIN = 'example.appspot.com'
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
)

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
    'netadmin.plugins'
)

INSTALLED_APPS += NETADMIN_APPS

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

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)
ROOT_URLCONF = 'urls'
LOGIN_URL = '/login/'

ACTIVATION_FROM_EMAIL = 'your_email@example.com'

DATABASES['native'] = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}

GAE_APPS = (
    'djangotoolbox',
    'dbindexer',
    'permission_backend_nonrel',
    'autoload',
    'search',
    'djangoappengine',
)

INSTALLED_APPS += GAE_APPS

AUTHENTICATION_BACKENDS = (
    'permission_backend_nonrel.backends.NonrelPermissionBackend',
)

MIDDLEWARE_CLASSES += (
    'autoload.middleware.AutoloadMiddleware',
)

TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'
GAE_MAIL_ACCOUNT = 'your_email@example.com'
AUTOLOAD_SITECONF = 'search_indexes'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

try:
    from local_settings import *
except ImportError:
    pass
