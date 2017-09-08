"""Django settings for tests."""

import os
import django

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production

SECRET_KEY = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'


LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale/'),
)

USE_TZ = True

EXTERNAL_APPS = [
    'django_mongoengine.mongo_auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_mongoengine',
    'mongoengine',
]

INTERNAL_APPS = [
    'mongo_coupons',
]

INSTALLED_APPS = EXTERNAL_APPS + INTERNAL_APPS

MEDIA_URL = '/media/'   # Avoids https://code.djangoproject.com/ticket/21451

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tests.urls'

STATIC_ROOT = os.path.join(BASE_DIR, 'tests', 'static')

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'tests', 'additional_static'),
    ("prefix", os.path.join(BASE_DIR, 'tests', 'additional_static')),
]


MONGODB_DATABASES = {
    "default": {
        "name": 'mongo-coupons',
        "host": '127.0.0.1',
        # "username": MONGO_USER,
        # "password": MONGO_PASSWORD,
        "tz_aware": True, # if you using timezones in django (USE_TZ = True)
    }
}

DATABASES = {
    'default': {'ENGINE': 'django.db.backends.dummy'}
}

if django.VERSION[:2] < (1, 6):
    TEST_RUNNER = 'discover_runner.DiscoverRunner'
