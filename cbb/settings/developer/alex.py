from cbb.settings.base import *

SITE_URL = 'localhost:8000'
DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


SITE_PREFIX = 'http://'
FULL_SITE_URL = f'{SITE_PREFIX}{SITE_URL}'
CORS_ALLOWED_ORIGINS = [
    'localhost',
    '127.0.0.1',
]
