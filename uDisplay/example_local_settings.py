"""
   Django Local Settings

   uDisplay/local_settings.py
   Created By Mayank Jain
"""
DEBUG = True

SECRET_KEY = 'your_django_app_secret_key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

ALLOWED_HOSTS = [
    'your_domain',
]
