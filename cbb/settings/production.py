from cbb.settings.base import *

DEBUG = False

STATIC_ROOT = "/var/www/site/static/"
STATIC_URL = "/static/"

CSRF_TRUSTED_ORIGINS = [
	"http://cbbdb.uib.es", "https://cbbdb.uib.es",
	"http://cbbdb.uib.cat", "https://cbbdb.uib.cat",
	"http://cbbdb.uib.eu", "https://cbbdb.uib.eu",
	"http://130.206.132.33", "https://130.206.132.33"
]
ALLOWED_HOSTS = [
	"cbbdb.uib.es",
	"cbbdb.uib.cat",
	"cbbdb.uib.eu",
	"localhost",
	"130.206.132.33"
]

CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS

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
