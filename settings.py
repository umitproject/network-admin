# Initialize App Engine and import the default settings (DB backend, etc.).
# If you want to use a different backend you have to remove all occurences
# of "djangoappengine" from this file.
from djangoappengine.settings_base import *

import os

DEBUG = True

GAE_MAIL_ACCOUNT = 'wasilewski.piotrek@gmail.com'

# Uncomment this if you're using the high-replication datastore.
# TODO: Once App Engine fixes the "s~" prefix mess we can remove this.
#DATABASES['default']['HIGH_REPLICATION'] = True

# Activate django-dbindexer for the default database
DATABASES['native'] = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}

MEDIA_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'media')
MEDIA_URL = '/media/'

SECRET_KEY = '=r-$b*8hglm+858&9t043hlm6-&6-3d3vfc4((7yd0dbrakhvi'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'djangotoolbox',
    'dbindexer',
    'permission_backend_nonrel',
    'autoload',
    'piston',
    'search',
    
    'netadmin.reportmeta',
    'netadmin.webapi',
    'netadmin.networks',
    'netadmin.events',
    'netadmin.users',
    'netadmin.permissions',
    'netadmin.notifier',
    'netadmin.utils.charts',
    'netadmin.plugins',
    
    #'django_nose',

    # djangoappengine should come last, so it can override a few manage.py commands
    'djangoappengine',
)

AUTHENTICATION_BACKENDS = (
    'permission_backend_nonrel.backends.NonrelPermissionBackend',
)

AUTOLOAD_SITECONF = 'search_indexes'
#SEARCH_BACKEND = 'search.backends.gae_background_tasks'

MIDDLEWARE_CLASSES = (
    # This loads the index definitions, so it has to come firsts
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    'autoload.middleware.AutoloadMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
)

AUTH_PROFILE_MODULE = 'users.UserProfile'

# This test runner captures stdout and associates tracebacks with their
# corresponding output. Helps a lot with print-debugging.
TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'
#TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

ADMIN_MEDIA_PREFIX = '/media/admin/'
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)

ROOT_URLCONF = 'urls'

LOGIN_URL = '/login/'
