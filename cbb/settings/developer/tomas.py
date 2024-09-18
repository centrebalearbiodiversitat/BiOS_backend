from cbb.settings.base import *

SITE_URL = 'localhost:8000'
DEBUG = True

ALLOWED_HOSTS = ['*']
SECRET_KEY = "django-insecure-=d^f%8dfm)s@he-zv@dk$z)24q!#6)90c5+!!e5qz-y%qq4txr"

SITE_PREFIX = 'http://'
FULL_SITE_URL = f'{SITE_PREFIX}{SITE_URL}'
CORS_ALLOWED_ORIGINS = [
	'http://localhost:3000',
]
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
#     },
# }
