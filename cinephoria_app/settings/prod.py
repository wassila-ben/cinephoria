from .base import *
import os
import dj_database_url


# prod avec Heroku
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')


SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv('DEBUG', 'False') == 'True'

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'     # dossier collecté par collectstatic
STATICFILES_DIRS = [BASE_DIR / 'static']   # dossier où sont tes fichiers persos

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres"):
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    print(" Pas de DATABASE_URL valide. Utilisation de SQLite.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


SECURE_HSTS_SECONDS = 3600
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'style-src': ("'self'", 'https://cdn.jsdelivr.net', "'unsafe-inline'"),
        'font-src': ("'self'", 'https://cdn.jsdelivr.net', 'data:'),
        'script-src': ("'self'",),
        'img-src': ("'self'", 'data:'),
        'connect-src': ("'self'",),
        'frame-src': ("'none'",),
    }
}




