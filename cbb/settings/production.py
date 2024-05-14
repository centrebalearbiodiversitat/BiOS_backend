from cbb.settings.base import *

DEBUG = os.environ.get("DEBUG", "").lower() == "true"

SITE_PREFIX = "https://"
SITE_URL = os.environ.get("SITE_URL")
FULL_SITE_URL = f"{SITE_PREFIX}{SITE_URL}"
CSRF_TRUSTED_ORIGINS = ["https://" + SITE_URL]
ALLOWED_HOSTS = ["127.0.0.1", SITE_URL, "*"]

CORS_ALLOWED_ORIGINS = ["127.0.0.1", SITE_URL, "*"]

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
	SECRET_FILE = os.path.join(BASE_DIR, "..", "secrets", "key.txt")
	try:
		SECRET_KEY = open(SECRET_FILE).read().strip()
	except IOError:
		try:
			from django.core.management.utils import get_random_secret_key

			SECRET_KEY = get_random_secret_key()

			if not os.path.exists(os.path.dirname(SECRET_FILE)):
				os.makedirs(os.path.dirname(SECRET_FILE))

			secret = open(SECRET_FILE, "w")
			secret.write(SECRET_KEY)
			secret.close()
		except IOError:
			Exception(
				"Please create a %s file with random characters \
            to generate your secret key!"
				% SECRET_FILE
			)


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
	"default": {
		"ENGINE": "django.db.backends.postgresql",
		"HOST": os.environ.get("DB_HOST"),
		"PORT": os.environ.get("DB_PORT"),
		"NAME": os.environ.get("POSTGRES_DB"),
		"USER": os.environ.get("POSTGRES_USER"),
		"PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
	}
}
