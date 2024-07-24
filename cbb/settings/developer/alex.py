from cbb.settings.base import *

SITE_URL = "localhost:8000"
DEBUG = True

ALLOWED_HOSTS = ["*"]
SECRET_KEY = "django-insecure-=d^f%8dfm)s@he-zv@dk$z)24q!#6)90c5+!!e5qz-y%qq4txr"

DATABASES = {
	"default": {
		"ENGINE": "django.db.backends.sqlite3",
		"NAME": BASE_DIR / "db.sqlite3",
	}
}


SITE_PREFIX = "http://"
FULL_SITE_URL = f"{SITE_PREFIX}{SITE_URL}"
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]

# LOGGING = {
# 	"version": 1,
# 	"disable_existing_loggers": False,
# 	"handlers": {
# 		"console": {
# 			"level": "DEBUG",
# 			"class": "logging.StreamHandler",
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
# 	},
# }
