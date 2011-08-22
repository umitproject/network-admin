import os

from djangoappengine.settings_base import *

DEBUG = True

MEDIA_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'media')
MEDIA_URL = '/media/'

SECRET_KEY = '=r-$b*8hglm+858&9t043hlm6-&6-3d3vfc4((7yd0dbrakhvi'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'piston',
    
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
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
)

SITE_DOMAIN = "ns-dev.appspot.com"
AUTH_PROFILE_MODULE = 'users.UserProfile'
ADMIN_MEDIA_PREFIX = '/media/admin/'
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)
ROOT_URLCONF = 'urls'
LOGIN_URL = '/login/'

#
# Google AppEngine settings based on Django-nonrel documentation
#
DATABASES['native'] = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}

INSTALLED_APPS += (
    'djangotoolbox',
    'dbindexer',
    'permission_backend_nonrel',
    'autoload',
    'search',
    'djangoappengine',
)

AUTHENTICATION_BACKENDS = (
    'permission_backend_nonrel.backends.NonrelPermissionBackend',
)

MIDDLEWARE_CLASSES += (
    'autoload.middleware.AutoloadMiddleware',
)

TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'
GAE_MAIL_ACCOUNT = 'wasilewski.piotrek@gmail.com'
AUTOLOAD_SITECONF = 'search_indexes'