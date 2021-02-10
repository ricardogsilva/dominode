# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

# Django settings for the GeoNode project.
import ast
import os
try:
    from urllib.parse import urlparse, urlunparse
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
    from urlparse import urlparse, urlunparse
# Load more settings from a file called local_settings.py if it exists

GEONODE_DATABASE_USER = os.environ.get('GEONODE_DATABASE_USER')
GEONODE_DATABASE_PASSWORD = os.environ.get('GEONODE_DATABASE_PASSWORD')
GEONODE_DATABASE = os.environ.get('GEONODE_DATABASE')
GEONODE_DATABASE_HOST = os.environ.get('GEONODE_DATABASE_HOST')
GEONODE_DATABASE_PORT = os.environ.get('GEONODE_DATABASE_PORT')
DATABASE_URL = 'postgres://{}:{}@{}:{}/{}'.format(GEONODE_DATABASE_USER, GEONODE_DATABASE_PASSWORD, GEONODE_DATABASE_HOST, GEONODE_DATABASE_PORT, GEONODE_DATABASE)
# Geodatabase connection details for datastore
GEONODE_GEODATABASE_USER = os.environ.get('GEONODE_GEODATABASE_USER')
GEONODE_GEODATABASE_PASSWORD = os.environ.get('GEONODE_GEODATABASE_PASSWORD')
GEONODE_GEODATABASE = os.environ.get('GEONODE_GEODATABASE')
GEONODE_GEODATABASE_HOST = os.environ.get('GEONODE_GEODATABASE_HOST')
GEONODE_GEODATABASE_PORT = os.environ.get('GEONODE_GEODATABASE_PORT')
GEODATABASE_URL = 'postgis://{}:{}@{}:{}/{}'.format(GEONODE_GEODATABASE_USER, GEONODE_GEODATABASE_PASSWORD, GEONODE_GEODATABASE_HOST, GEONODE_GEODATABASE_PORT, GEONODE_GEODATABASE)
# import generic settings
os.environ['DATABASE_URL'] = DATABASE_URL
os.environ['GEODATABASE_URL'] = GEODATABASE_URL

DOMAIN = os.getenv('HTTP_HOST', "localhost")

PLAUSIBLE_DOMAIN = os.getenv('PLAUSIBLE_DOMAIN',"http://localhost")
PLAUSIBLE_URL = "{}/js/plausible.js".format(PLAUSIBLE_DOMAIN)

try:
    from geonode_dominode.local_settings import *
#    from geonode.local_settings import *
except ImportError:
    from geonode.settings import *

#
# General Django development settings
#
PROJECT_NAME = 'geonode_dominode'

# add trailing slash to site url. geoserver url will be relative to this
if not SITEURL.endswith('/'):
    SITEURL = '{}/'.format(SITEURL)

SITENAME = os.getenv("SITENAME", 'geonode_dominode')

# Defines the directory that contains the settings file as the LOCAL_ROOT
# It is used for relative settings elsewhere.
LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))

WSGI_APPLICATION = "{}.wsgi.application".format(PROJECT_NAME)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', "en")

# This sequence of INSTALLED_APPS seems unusually hacky, but there is good
# reason for it:
# - we need our custom dominode apps to be rendered before the stock geonode
#   apps in order to be able to override some geonode templates
# - on the other hand we also need to have the standard GeoNode groups app
#   loaded before we include our geonode_dominode app because we are replacing
#   the standard admin for geonode groups with our own, which uses
#   django-guardian.
#
INSTALLED_APPS = (
    'dominode_validation.apps.DominodeValidationConfig',
    'dominode_topomaps.apps.DominodeTopomapsConfig',
) + INSTALLED_APPS + (
    'geonode_dominode.apps.AppConfig',
    'rest_framework',
    # 'django_filters',
    'django_json_widget',
)

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': (
        'rest_framework.pagination.PageNumberPagination'),
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # TODO: use django oauth toolkit instead
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ]
}

# if PROJECT_NAME not in INSTALLED_APPS:
#     INSTALLED_APPS += (PROJECT_NAME,)

# Location of url mappings
ROOT_URLCONF = os.getenv('ROOT_URLCONF', '{}.urls'.format(PROJECT_NAME))

# Additional directories which hold static files
STATICFILES_DIRS.append(
    os.path.join(LOCAL_ROOT, "static"),
)

# Location of locale files
LOCALE_PATHS = (
    os.path.join(LOCAL_ROOT, 'locale'),
    ) + LOCALE_PATHS

TEMPLATES[0]['DIRS'].insert(0, os.path.join(LOCAL_ROOT, "templates"))
loaders = TEMPLATES[0]['OPTIONS'].get('loaders') or ['django.template.loaders.filesystem.Loader','django.template.loaders.app_directories.Loader']
# loaders.insert(0, 'apptemplates.Loader')
TEMPLATES[0]['OPTIONS']['loaders'] = loaders
TEMPLATES[0].pop('APP_DIRS', None)
TEMPLATES[0]['OPTIONS']['context_processors'].append(
    'geonode_dominode.context_processors.user_is_geoserver_editor')
TEMPLATES[0]['OPTIONS']['context_processors'].append(
    'geonode_dominode.context_processors.plausible_envs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d '
                      '%(thread)d %(message)s'
        },
        'simple': {
            'format': '%(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    "loggers": {
        "django": {
            "handlers": ["console"], "level": "ERROR", },
        "geonode": {
            "handlers": ["console"], "level": "INFO", },
        "geoserver-restconfig.catalog": {
            "handlers": ["console"], "level": "ERROR", },
        "owslib": {
            "handlers": ["console"], "level": "ERROR", },
        "pycsw": {
            "handlers": ["console"], "level": "ERROR", },
        "celery": {
            "handlers": ["console"], "level": "DEBUG", },
        "mapstore2_adapter.plugins.serializers": {
            "handlers": ["console"], "level": "DEBUG", },
        "geonode_logstash.logstash": {
            "handlers": ["console"], "level": "DEBUG", },
    },
}

CENTRALIZED_DASHBOARD_ENABLED = ast.literal_eval(os.getenv('CENTRALIZED_DASHBOARD_ENABLED', 'False'))
if CENTRALIZED_DASHBOARD_ENABLED and USER_ANALYTICS_ENABLED and 'geonode_logstash' not in INSTALLED_APPS:
    INSTALLED_APPS += ('geonode_logstash',)

    CELERY_BEAT_SCHEDULE['dispatch_metrics'] = {
        'task': 'geonode_logstash.tasks.dispatch_metrics',
        'schedule': 3600.0,
    }

LDAP_ENABLED = ast.literal_eval(os.getenv('LDAP_ENABLED', 'False'))
if LDAP_ENABLED and 'geonode_ldap' not in INSTALLED_APPS:
    INSTALLED_APPS += ('geonode_ldap',)

# Add your specific LDAP configuration after this comment:
# https://docs.geonode.org/en/master/advanced/contrib/#configuration

if DEBUG:
    LOGGING['loggers']['geonode'] = {
        "handlers": ["console"], "level": "DEBUG",
    }
    LOGGING['loggers']['geonode_dominode'] = {
        "handlers": ["console"], "level": "DEBUG"
    }
    LOGGING['loggers']['dominode_topomaps'] = {
        "handlers": ["console"], "level": "DEBUG"
    }
    LOGGING['handlers']['console']['level'] = 'DEBUG'


CELERY_TASK_QUEUES += (
    Queue(
        'geonode_dominode',
        GEONODE_EXCHANGE,
        routing_key='geonode_dominode'),
)

CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'default'

DOMINODE_PUBLISHED_TOPOMAPS = {
    'index_pattern': 'lsd_published-topomap-series',
    'sheet_path_pattern': (
        '/topomaps/v{version}/series-{series}/dominica_topomap-{series}-'
        '(?P<paper_size>\w+)-{sheet}_v{version}.pdf'
    ),
}