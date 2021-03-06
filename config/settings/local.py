# -*- coding: utf-8 -*-
'''
Local settings

- Run in Debug mode
- Use console backend for emails
- Add Django Debug Toolbar
- Add django-extensions as app
'''

from .common import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env("DJANGO_SECRET_KEY", default='s_%g+y+#x-f7i64$d35w&1h_^9!)^dc)3j7+gk)=$%-y6%a==g')

# Mail settings
# ------------------------------------------------------------------------------
EMAIL_HOST = 'mailhog'
EMAIL_PORT = 1025


# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += ('django_extensions', )

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Your local stuff: Below this line define 3rd party library settings

# FREEZE
# ------------------------------------------------------------------------------
FREEZE_SITE_URL = 'http://docker.dev:8000'
FREEZE_STATIC_ROOT = STATICFILES_DIRS[0]
FREEZE_INCLUDE_STATIC = True

STATIC_SITE_HTTP_HOST = 'cv.11craft.com'
