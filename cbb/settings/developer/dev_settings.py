import os
from dotenv import load_dotenv
from cbb.settings.base import *

# Load environment variables from .env file
load_dotenv()

# --- SECURITY CONFIGURATION ---
# Handle DEBUG boolean from string (case-insensitive to support 'true', 'True')
DEBUG = str(os.getenv("DEBUG", "False")).lower() == "true"

# Load SECRET_KEY from .env (mapped to DJANGO_SECRET_KEY)
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# Raise error if SECRET_KEY is missing to prevent insecure startup
if not SECRET_KEY:
	raise ValueError("DJANGO_SECRET_KEY is missing in .env file!")

# --- SITE CONFIGURATION ---
# Load SITE_URL, defaulting to localhost:8000 if not found
SITE_URL = os.getenv("SITE_URL", "localhost:8000")

ALLOWED_HOSTS = ["*"]

SITE_PREFIX = "http://"
FULL_SITE_URL = f"{SITE_PREFIX}{SITE_URL}"

# CORS Configuration: Define allowed origins for Cross-Origin Resource Sharing
CORS_ALLOWED_ORIGINS = [
	"http://localhost:3000",  # Local Next.js frontend
	"http://127.0.0.1:3000",  # Local IP alternative
	f"{SITE_PREFIX}{SITE_URL}",  # Dynamic backend URL from env
	f"{SITE_PREFIX}localhost:8000",  # Explicit fallback for local Django development
]

# Uncomment to obtain logs of Django processes.
# LOGGING = {
#   "version": 1,
#   "disable_existing_loggers": False,
#   "formatters": {
#       "simple": {
#           "format": "{levelname} \n{message} \n{asctime} \n{module} \n{filename} \n{lineno}",
#           "style": "{",
#       },
#   },
#   "handlers": {
#       "console": {
#           "level": "DEBUG",
#           "class": "logging.StreamHandler",
#           "formatter": "simple",
#       },
#       "file": {
#           "level": "DEBUG",
#           "class": "logging.FileHandler",
#           "filename": "django_queries.log",  # Choose a file name and path
#       },
#   },
#   "loggers": {
#       "django.db.backends": {
#           "handlers": ["console"],
#           "level": "DEBUG",
#           "propagate": False,
#       },
#         'apps.API.urls': {
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
#             'level': 'INFO',  # Default logging level
#         },
#   },
# }
