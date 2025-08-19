from cbb.settings.base import *


SITE_URL = "localhost:8000"
DEBUG = True
ALLOWED_HOSTS = ["*"]
SECRET_KEY = "django-insecure-=d^f%8dfm)s@he-zv@dk$z)24q!#6)90c5+!!e5qz-y%qq4txr"
SITE_PREFIX = "http://"
FULL_SITE_URL = f"{SITE_PREFIX}{SITE_URL}"
CORS_ALLOWED_ORIGINS = ["http://localhost:8000"]


# LOGGING = {
# 	"version": 1,
# 	"disable_existing_loggers": False,
# 	"formatters": {
# 		"simple": {
# 			"format": "{levelname} \n{message} \n{asctime} \n{module} \n{filename} \n{lineno}",
# 			"style": "{",
# 		},
# 	},
# 	"handlers": {
# 		"console": {
# 			"level": "DEBUG",
# 			"class": "logging.StreamHandler",
# 			"formatter": "simple",
# 		},
# 		"file": {
# 			"level": "DEBUG",
# 			"class": "logging.FileHandler",
# 			"filename": "django_queries.log",  # Choose a file name and path
# 		},
# 	},
# 	"loggers": {
# 		"django.db.backends": {
# 			"handlers": ["console"],
# 			"level": "DEBUG",
# 			"propagate": False,
# 		},
#         'apps.API.urls': {  # Reemplaza con la ruta correcta a tu archivo
#             'handlers': ['console'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
#         'drf_yasg': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
#         '': {
#             'handlers': ['console'],
#             'level': 'INFO',  # Nivel de logging por defecto
#         },
# 	},
# }
