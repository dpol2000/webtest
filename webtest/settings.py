import os
import sys
import socket
from config import get_config, get_config_key


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

config_keys = get_config()
SECRET_KEY = get_config_key("SECRET_KEY", config_keys)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'etest'
    #'debug_toolbar'
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'webtest.urls'

WSGI_APPLICATION = 'webtest.wsgi.application'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    "/usr/local/lib/python2.7/dist-packages/django/contrib/admin/static/admin/",
)

LOGIN_URL = '/'

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': ['django.contrib.auth.context_processors.auth']
        },
    },
]


if 'manage.py' in sys.argv[0]:
    from settings_local import *

    TEMPLATES[0]['OPTIONS']['debug'] = True

    db_name = get_config_key("DB_NAME_LOCAL", config_keys)
    db_user = get_config_key("DB_USER_LOCAL", config_keys)
    db_password = get_config_key("DB_PASSWORD_LOCAL", config_keys)
    db_host = ""

else:
    from settings_remote import *

    TEMPLATES[0]['OPTIONS']['debug'] = False

    db_name = get_config_key("DB_NAME_REMOTE", config_keys)
    db_user = get_config_key("DB_USER_REMOTE", config_keys)
    db_password = get_config_key("DB_PASSWORD_REMOTE", config_keys)
    db_host = get_config_key("DB_HOST_REMOTE", config_keys)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': db_name,                      # Or path to database file if using sqlite3.
        'USER': db_user,                      # Not used with sqlite3.
        'PASSWORD': db_password,                  # Not used with sqlite3.
        'HOST': db_host,                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


