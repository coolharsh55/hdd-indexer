"""Settings for HDD-indexer (django)

    Defines settings for HDD-indexer (django)
"""

from django.conf import global_settings
import os

TMDB_KEY = '9dd0aeee75f0ac85dfe0261c522829aa'
""" used for TMDb API to retrieve movie metadata
"""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
"""Gives the (base) directory of the current project
"""

PROJECT_PATH = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
"""Gives the absolute path of the project directory on any system
"""

SECRET_KEY = '71=%^+z08qoj-b7&-799_)ljad=*sil%%$8ofs%l_-cse)@8!x'
"""Django secret key - is unique per project
"""

DEBUG = True
"""Debugging settings
    True will show info on errors,
    False will show error pages (404, etc.)
"""

ALLOWED_HOSTS = ['*', ]
"""Server allowed hosts
When on server, this specifies which hosts are served
"""

INSTALLED_APPS = (
    # admin
    'grappelli',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # external apps
    'solo',

    # project apps
    'hdd_settings',
    'movie_metadata',
)
"""Installed apps
Shows a list of apps to load
"""

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)
"""Middleware
Provides middleware functionality in Django
"""

ROOT_URLCONF = 'hdd_indexer.urls'
"""Urls used for first serving on server
All other urls should be derived from the root urls
"""

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['hdd_indexer/templates', ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
"""Templates for serving
Contains pages served using Django views
"""

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
)
"""Context processors for Templates
Provide additional functionality inside templates
"""

WSGI_APPLICATION = 'hdd_indexer.wsgi.application'
"""WSGI config
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'OPTIONS': {
            'timeout': 300,
        }
    }
}

DATABASE_OPTIONS = {
    'timeout': 60,
}
"""Database settings for this project
Set to SQLite3 for hdd-indexer
"""

LANGUAGE_CODE = 'en-us'
"""Language English (USA)
"""

TIME_ZONE = 'UTC'
"""Time Zone set to UTC (GMT)
"""

USE_I18N = True
"""Internationalization set to True
"""

USE_L10N = True
"""Localization set to True
"""

USE_TZ = True
"""Time Zone library set to true
"""

STATIC_URL = '/static/'
"""Url for serving static content
"""

STATICFILES_DIRS = (
    PROJECT_PATH + '/static/',
)
"""Directories containing static files
"""

GRAPPELLI_ADMIN_TITLE = 'HDD-indexer'
"""Grappelli admin title
"""

# ensure logs directory exists
try:
    os.makedirs('./logs/')
except OSError:
    if not os.path.isdir('./logs/'):
        raise

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)s] %(message)s',
            'datefmt': "%d/%b %H:%M:%S",
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'system': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/system.log',
            'formatter': 'verbose'
        },
        'server': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/server.log',
            'formatter': 'verbose'
        },
        'load': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/load.log',
            'formatter': 'verbose'
        },
        'crawl': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/crawl.log',
            'formatter': 'verbose'
        },
        'movie': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/movie.log',
            'formatter': 'verbose'
        },
        'setup': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/setup.log',
            'formatter': 'verbose'
        },
        'export': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/export.log',
            'formatter': 'verbose',
        }

    },
    'loggers': {
        'django': {
            'handlers': ['system'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'server': {
            'handlers': ['server'],
            'level': 'DEBUG',
        },
        'load': {
            'handlers': ['load'],
            'level': 'DEBUG',
        },
        'crawl': {
            'handlers': ['crawl'],
            'level': 'DEBUG',
        },
        'movie': {
            'handlers': ['movie'],
            'level': 'DEBUG',
        },
        'setup': {
            'handlers': ['server'],
            'level': 'DEBUG',
        },
        'export': {
            'handlers': ['export'],
            'level': 'DEBUG',
        }
    }
}
